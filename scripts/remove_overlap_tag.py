"""Remove a cohort tag from Mailchimp members who also carry another tag.

Used to keep launch cohorts disjoint: members on both the webinar-invite
and NYC-social-event lists keep only the social-event tag, so campaigns
targeting each tag segment never overlap.

Usage:
    python scripts/remove_overlap_tag.py \
        --keep-tag "July 26 NYC Launch Social Event" \
        --remove-tag "July 26 Launch Webinar Invites"

Requires MAILCHIMP_API_KEY in the environment or .env.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

MAILCHIMP_AUDIENCE_ID = "fbea2dd394"  # Axiom Foundation (main audience)
MAILCHIMP_DC = "us12"


def load_env(path=".env"):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))


def mailchimp(path, body=None):
    auth = base64.b64encode(f"anystring:{os.environ['MAILCHIMP_API_KEY']}".encode())
    req = urllib.request.Request(
        f"https://{MAILCHIMP_DC}.api.mailchimp.com/3.0{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Basic {auth.decode()}",
            "Content-Type": "application/json",
        },
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return {}
            return json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"API error {error.code} for {path}: {error.read().decode()[:500]}")


def segment_id(tag_name):
    segments = mailchimp(
        f"/lists/{MAILCHIMP_AUDIENCE_ID}/segments?type=static&count=100"
    )["segments"]
    for segment in segments:
        if segment["name"] == tag_name:
            return segment["id"]
    sys.exit(f"No tag segment named {tag_name!r} on the audience")


def segment_emails(seg_id):
    emails, offset = set(), 0
    while True:
        page = mailchimp(
            f"/lists/{MAILCHIMP_AUDIENCE_ID}/segments/{seg_id}/members"
            f"?count=1000&offset={offset}&fields=members.email_address,total_items"
        )
        emails |= {m["email_address"].lower() for m in page["members"]}
        offset += 1000
        if offset >= page["total_items"]:
            return emails


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-tag", required=True)
    parser.add_argument("--remove-tag", required=True)
    args = parser.parse_args()

    load_env()
    if not os.environ.get("MAILCHIMP_API_KEY"):
        sys.exit("MAILCHIMP_API_KEY must be set (see .env)")

    keep = segment_emails(segment_id(args.keep_tag))
    remove = segment_emails(segment_id(args.remove_tag))
    overlap = sorted(keep & remove)
    print(f"{args.keep_tag!r}: {len(keep)} members")
    print(f"{args.remove_tag!r}: {len(remove)} members")
    print(f"overlap (will lose {args.remove_tag!r}): {len(overlap)}")

    import hashlib

    for email in overlap:
        member_hash = hashlib.md5(email.encode()).hexdigest()
        mailchimp(
            f"/lists/{MAILCHIMP_AUDIENCE_ID}/members/{member_hash}/tags",
            {"tags": [{"name": args.remove_tag, "status": "inactive"}]},
        )
    print(f"Done: removed {args.remove_tag!r} from {len(overlap)} members")


if __name__ == "__main__":
    main()
