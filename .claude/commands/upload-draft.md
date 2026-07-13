---
description: Upload newsletter to Mailchimp as a draft campaign
argument-hint: <html-file> --audience <all|uk|us> --subject "..." --preview "..."
---

Upload a newsletter HTML file to Mailchimp as a draft campaign with audience targeting.

## Usage

```bash
/upload-draft editions/2026-08-01.html --audience all --subject "Subject line" --preview "Preview text"
```

## Process

This is a wrapper around the `upload-newsletter` command that:

1. Validates the HTML file exists
2. Runs `./scripts/lint-newsletters.sh` first and stops on errors
3. Prompts for required fields if missing
4. Runs the upload command (requires `MAILCHIMP_API_KEY` and `MAILCHIMP_LIST_ID`)
5. Shows the Mailchimp edit URL

## Arguments

- `html-file`: Path to newsletter HTML file (required)
- `--audience`: Target audience - `all`, `uk`, or `us` (required for new campaigns)
  - `all`: All subscribers
  - `uk`: Only subscribers with COUNTRY = "United Kingdom" (requires COUNTRY merge field)
  - `us`: All non-UK subscribers
- `--subject`: Email subject line (required)
- `--preview`: Preview text shown in inbox (required)
- `--title`: Optional internal campaign title (defaults to filename)
- `--campaign-id`: Update an existing draft instead of creating a new one

## Implementation

```bash
upload-newsletter $ARGUMENTS
```

The command creates a DRAFT campaign — review and send from the Mailchimp web interface. When revising an already-uploaded newsletter, always pass `--campaign-id` instead of creating a duplicate.
