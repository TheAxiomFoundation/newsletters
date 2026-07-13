# Axiom Foundation Newsletter Repository

HTML templates and Mailchimp tooling for Axiom Foundation newsletters. Mirrors the
structure of [PolicyEngine/newsletters](https://github.com/PolicyEngine/newsletters)
with Axiom branding.

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

1. Set your Mailchimp credentials:
```bash
export MAILCHIMP_API_KEY="your-key-usX"   # datacenter suffix required
export MAILCHIMP_LIST_ID="your-list-id"
```

2. Create a newsletter HTML file in `editions/` (e.g., `2026-08-01.html`). Start
   from the most recent edition, or from
   `templates/axiom-newsletter-template.html` if none exists yet.

3. Upload to Mailchimp as a draft:
```bash
upload-newsletter editions/2026-08-01.html \
  --audience all \
  --subject "Your Subject Line" \
  --preview "Preview text shown in inbox"
```

4. Review the draft in Mailchimp and send when ready

## Audience Targeting

- `--audience all` - All subscribers (the default choice until segments exist)
- `--audience uk` - Subscribers with `COUNTRY` = "United Kingdom" (requires the
  `COUNTRY` merge field on the audience)
- `--audience us` - All non-UK subscribers (includes missing country data)

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=newsletter_uploader --cov-report=term-missing

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Lint newsletter HTML for email-compatibility issues
./scripts/lint-newsletters.sh
```

## Package Structure

- `src/newsletter_uploader/` - Python package
  - `mailchimp_client.py` - Mailchimp API client
  - `audience.py` - Audience targeting logic
  - `uploader.py` - Newsletter uploader
  - `cli.py` - Command-line interface
- `tests/` - Test suite
- `editions/` - Newsletter HTML files, one per send (`YYYY-MM-DD.html`)
- `templates/` - The Axiom-styled base template
- `assets/images/` - Newsletter images (referenced by absolute raw.githubusercontent URLs)
- `.env` - Contains `MAILCHIMP_API_KEY` / `MAILCHIMP_LIST_ID` (gitignored)

## Brand

Colors, wordmarks, and email header assets come from
[axiom-brand](https://github.com/TheAxiomFoundation/axiom-brand); see `CLAUDE.md`
for the newsletter styling rules.
