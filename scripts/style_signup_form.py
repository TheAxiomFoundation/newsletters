"""Apply Axiom newsletter styling to the hosted Mailchimp signup form.

Pushes the newsletter's visual language (warm-brown citation-network outer,
paper card, white masthead with the gradient wordmark, amber buttons and
links) to the list's hosted signup form via the Mailchimp Marketing API
signup-forms endpoint.

Note: POST replaces the whole form config (header, contents, styles), so this
script always sends the complete set.

The hosted form's Subscribe button uses Mailchimp's newer theme class
(.formEmailButton) with a hardcoded gray "!important" rule that the
forms_buttons API selector cannot reach. The signup_message content accepts
HTML, so the config prepends a small <style> override to recolor it amber.

Usage:
    python scripts/style_signup_form.py

Requires MAILCHIMP_API_KEY and MAILCHIMP_LIST_ID in the environment or .env.
"""

import base64
import json
import os
import sys
import urllib.request

WORDMARK_URL = (
    "https://raw.githubusercontent.com/TheAxiomFoundation/axiom-brand/main/"
    "png/wordmark/axiom-full-gradient-2400w.png"
)
TEXTURE_URL = (
    "https://raw.githubusercontent.com/TheAxiomFoundation/newsletters/main/"
    "assets/images/citation-network-bg.png"
)

# Newsletter palette (see CLAUDE.md "Axiom Color Scheme")
WARM_BROWN = "#f0e7d8"  # outer background
PAPER = "#faf9f6"  # content card
INK = "#1c1917"  # headings / labels
BODY = "#44403c"  # body text
AMBER = "#b45309"  # links, buttons, accents
AMBER_DARK = "#92400e"  # button hover
MUTED = "#a8a29e"  # help text
WHITE = "#ffffff"  # masthead

# Overrides Mailchimp's theme button (gray, !important) that the forms_buttons
# selector cannot reach; rendered inline ahead of the signup message text.
BUTTON_OVERRIDE = (
    "<style>"
    ".formEmailButton,.formEmailButton span{"
    f"background-color:{AMBER} !important;color:{WHITE} !important;"
    "border-radius:7px !important;}"
    ".formEmailButton:hover,.formEmailButton:hover span{"
    f"background-color:{AMBER_DARK} !important;}}"
    f".confirm-thanks .formEmailButtonOval{{background-color:{AMBER};}}"
    "</style>"
)

FORM_CONFIG = {
    "header": {
        "image_url": WORDMARK_URL,
        "image_width": "280",
        "image_alt": "Axiom Foundation",
        "image_link": "https://axiom-foundation.org",
        "image_align": "center",
        "image_border_width": "0",
        "image_border_style": "none",
        "image_target": "_blank",
        "text": "",
    },
    "contents": [
        {
            "section": "signup_message",
            "value": BUTTON_OVERRIDE
            + (
                "Occasional updates from the Axiom Foundation — new corpora, "
                "engine releases, events, and research. Sent when there is "
                "something concrete to report."
            ),
        },
        {
            "section": "signup_thank_you_title",
            "value": "Subscribed — see you in the next edition.",
        },
        {
            "section": "unsub_message",
            "value": "You have been unsubscribed. You can rejoin any time.",
        },
    ],
    "styles": [
        {
            "selector": "page_background",
            "options": [
                {"property": "background-color", "value": WARM_BROWN},
                {"property": "background-image", "value": f"url('{TEXTURE_URL}')"},
                {"property": "background-repeat", "value": "repeat"},
                {"property": "background-position", "value": "top center"},
            ],
        },
        {
            "selector": "page_header",
            "options": [
                {"property": "background-color", "value": WHITE},
                {"property": "color", "value": INK},
            ],
        },
        {
            "selector": "page_outer_wrapper",
            "options": [
                {"property": "background-color", "value": PAPER},
                {"property": "border-radius", "value": "14px"},
                {"property": "border", "value": "1px solid #e7e5e4"},
            ],
        },
        {
            "selector": "body_background",
            "options": [
                {"property": "background-color", "value": PAPER},
                {"property": "color", "value": BODY},
            ],
        },
        {
            "selector": "body_link_style",
            "options": [{"property": "color", "value": AMBER}],
        },
        {
            "selector": "forms_buttons",
            "options": [
                {"property": "background-color", "value": AMBER},
                {"property": "color", "value": WHITE},
                {"property": "border-radius", "value": "7px"},
                {"property": "font-weight", "value": "500"},
            ],
        },
        {
            "selector": "forms_buttons_hovered",
            "options": [
                {"property": "background-color", "value": AMBER_DARK},
                {"property": "color", "value": WHITE},
            ],
        },
        {
            "selector": "forms_field_label",
            "options": [{"property": "color", "value": INK}],
        },
        {
            "selector": "forms_field_text",
            "options": [{"property": "color", "value": BODY}],
        },
        {
            "selector": "forms_required",
            "options": [{"property": "color", "value": AMBER}],
        },
        {
            "selector": "forms_required_legend",
            "options": [{"property": "color", "value": AMBER}],
        },
        {
            "selector": "forms_help_text",
            "options": [{"property": "color", "value": MUTED}],
        },
    ],
}


def load_env(path=".env"):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))


def main():
    load_env()
    api_key = os.environ.get("MAILCHIMP_API_KEY")
    list_id = os.environ.get("MAILCHIMP_LIST_ID")
    if not api_key or not list_id:
        sys.exit("MAILCHIMP_API_KEY and MAILCHIMP_LIST_ID must be set (see .env)")

    dc = api_key.rsplit("-", 1)[-1] if "-" in api_key else "us12"
    url = f"https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/signup-forms"
    auth = base64.b64encode(f"anystring:{api_key}".encode()).decode()

    request = urllib.request.Request(
        url,
        data=json.dumps(FORM_CONFIG).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        sys.exit(f"Mailchimp API error {error.code}: {error.read().decode()}")

    print(f"Signup form updated: {result.get('signup_form_url', url)}")


if __name__ == "__main__":
    main()
