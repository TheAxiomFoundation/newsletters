"""Import contacts from an Attio list into a Mailchimp audience.

Pulls every person on the Attio list (default: July '26 Launch Webinar
Invites), resolves their company reference to a company name, and
batch-imports them into the main Axiom Foundation audience as subscribed
members with FNAME/LNAME/ORG/ROLE merge fields (matching the signup form's
fields), tagged with the cohort name so they stay distinguishable from
organic subscribers.

Re-runnable: existing members are updated, not duplicated.

Usage:
    python scripts/import_attio_contacts.py

Requires ATTIO_API_KEY and MAILCHIMP_API_KEY in the environment or .env.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ATTIO_LIST_ID = "f259205e-7e4c-42f2-87df-a03dfdf46afd"  # July '26 Launch Webinar Invites
MAILCHIMP_AUDIENCE_ID = "fbea2dd394"  # Axiom Foundation (main audience)
MEMBER_TAG = "July 26 Launch Webinar Invites"
MAILCHIMP_DC = "us12"
BATCH_SIZE = 500  # Mailchimp's max members per batch-subscribe call


def load_env(path=".env"):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))


def request_json(url, headers, body=None, method=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={**headers, "Content-Type": "application/json"},
        method=method or ("POST" if body is not None else "GET"),
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"API error {error.code} for {url}: {error.read().decode()[:500]}")


def attio(path, body=None):
    return request_json(
        f"https://api.attio.com/v2{path}",
        {"Authorization": f"Bearer {os.environ['ATTIO_API_KEY']}"},
        body,
    )


def mailchimp(path, body=None, method=None):
    auth = base64.b64encode(f"anystring:{os.environ['MAILCHIMP_API_KEY']}".encode())
    return request_json(
        f"https://{MAILCHIMP_DC}.api.mailchimp.com/3.0{path}",
        {"Authorization": f"Basic {auth.decode()}"},
        body,
        method,
    )


def first_value(values, attribute, key=None):
    entries = values.get(attribute) or []
    active = [e for e in entries if e.get("active_until") is None] or entries
    if not active:
        return None
    return active[0].get(key) if key else active[0]


def fetch_people():
    record_ids, offset = [], 0
    while True:
        batch = attio(
            f"/lists/{ATTIO_LIST_ID}/entries/query",
            {"limit": 500, "offset": offset},
        )["data"]
        record_ids += [e["parent_record_id"] for e in batch]
        if len(batch) < 500:
            break
        offset += 500
    record_ids = list(dict.fromkeys(record_ids))
    print(f"Attio list entries: {len(record_ids)} unique people")

    def fetch(record_id):
        return attio(f"/objects/people/records/{record_id}")["data"]["values"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(fetch, record_ids))


def company_names(people):
    ids = set()
    for values in people:
        company = first_value(values, "company")
        if company:
            ids.add(company["target_record_id"])
    print(f"Resolving {len(ids)} companies")

    def fetch(company_id):
        values = attio(f"/objects/companies/records/{company_id}")["data"]["values"]
        return company_id, first_value(values, "name", "value") or ""

    with ThreadPoolExecutor(max_workers=8) as pool:
        return dict(pool.map(fetch, ids))


def build_members(people, companies):
    members, skipped = [], 0
    for values in people:
        email = first_value(values, "email_addresses", "email_address")
        if not email:
            skipped += 1
            continue
        name = first_value(values, "name") or {}
        company = first_value(values, "company")
        members.append(
            {
                "email_address": email,
                "status": "subscribed",
                "tags": [MEMBER_TAG],
                "merge_fields": {
                    "FNAME": name.get("first_name") or "",
                    "LNAME": name.get("last_name") or "",
                    "ORG": companies.get(company["target_record_id"], "") if company else "",
                    "ROLE": first_value(values, "job_title", "value") or "",
                },
            }
        )
    return members, skipped


def ensure_merge_fields():
    existing = {
        f["tag"]: f
        for f in mailchimp(f"/lists/{MAILCHIMP_AUDIENCE_ID}/merge-fields?count=50")[
            "merge_fields"
        ]
    }
    for tag, name in [("ORG", "Organization"), ("ROLE", "Role")]:
        if tag not in existing:
            mailchimp(
                f"/lists/{MAILCHIMP_AUDIENCE_ID}/merge-fields",
                {"tag": tag, "name": name, "type": "text", "required": False},
            )
            print(f"Added merge field {tag}")
    return existing


def set_required(fields, tags, required):
    """Mailchimp enforces required merge fields on API imports too, and Attio
    data has gaps (empty roles), so imports run with the flags relaxed and
    restore them afterwards to keep the signup form's fields required."""
    for tag in tags:
        field = fields.get(tag)
        if field:
            mailchimp(
                f"/lists/{MAILCHIMP_AUDIENCE_ID}/merge-fields/{field['merge_id']}",
                {"required": required},
                method="PATCH",
            )


def main():
    load_env()
    for key in ("ATTIO_API_KEY", "MAILCHIMP_API_KEY"):
        if not os.environ.get(key):
            sys.exit(f"{key} must be set (see .env)")

    people = fetch_people()
    companies = company_names(people)
    members, skipped = build_members(people, companies)
    print(f"Members to import: {len(members)} (skipped {skipped} without email)")

    fields = ensure_merge_fields()
    required_tags = [t for t, f in fields.items() if f.get("required")]
    set_required(fields, required_tags, False)

    try:
        created = updated = errored = 0
        for start in range(0, len(members), BATCH_SIZE):
            chunk = members[start : start + BATCH_SIZE]
            result = mailchimp(
                f"/lists/{MAILCHIMP_AUDIENCE_ID}",
                {"members": chunk, "update_existing": True},
            )
            created += result["total_created"]
            updated += result["total_updated"]
            errored += result["error_count"]
            for error in result["errors"][:5]:
                print(f"  error: {error['email_address']}: {error['error']}")
    finally:
        set_required(fields, required_tags, True)

    print(f"Done: {created} created, {updated} updated, {errored} errors")


if __name__ == "__main__":
    main()
