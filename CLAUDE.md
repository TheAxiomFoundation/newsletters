# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Newsletter repository containing HTML email templates for the Axiom Foundation's
Mailchimp campaigns, plus a small Python uploader package. Mirrors
[PolicyEngine/newsletters](https://github.com/PolicyEngine/newsletters) with Axiom
branding.

## Repository Structure

```
axiom-newsletters/
├── editions/          # Newsletter HTML files (one per edition, YYYY-MM-DD.html)
├── templates/
│   └── axiom-newsletter-template.html  # Axiom-styled base template
├── assets/
│   └── images/        # Newsletter image assets (referenced by absolute URL)
├── config/
│   └── mailchimp-settings.json  # API key placeholder (real key goes in .env)
├── src/newsletter_uploader/     # Upload package (CLI: upload-newsletter)
└── tests/
```

## Newsletter Template Structure

All newsletter HTML files follow this pattern:

The design borrows Axiom's own vernacular (edition numbering, mono labels,
artifact chips) rather than a generic marketing layout — but stays plain-language:
no code blocks. Light and paper-first, matching axiom-foundation.org: warm-gray
outer, paper card, amber-wash masthead, amber spent sparingly; ink appears only
in type — no dark surfaces.

1. **Inline Styles**: All styling is inline (required for email compatibility)
2. **Fonts**: Geist (headings/body) + **Geist Mono** (edition number, chips,
   code, link labels) from Google Fonts, with system fallbacks
   (`'SFMono-Regular', Menlo, Consolas, monospace`)
3. **Max Width**: 600px centered container, 14px radius
4. **Axiom Color Scheme** (from [axiom-brand](https://github.com/TheAxiomFoundation/axiom-brand)):
   - Warm gray (outer background): `#eceae5`
   - Paper (content card): `#faf9f6` · Inset panel: `#f5f2ec`
   - Amber-wash masthead: `linear-gradient(160deg, #f9efdf, #f3e2c8)` (fallback `#f6e8d3`)
   - Ink (type only — headings, key details): `#1c1917`
   - Amber (chips, links, CTAs, headline accent, YAML keys): `#b45309`
   - Seal hairline gradient: `#b45309 → #d97706 → #f3e5d3` (3px, under the header)
   - Body text: `#44403c` · Headings: `#1c1917` · Hairlines: `#e7e5e4`
   - Muted mono labels: `#a8a29e` · Footer text: `#8d867c`
5. **Signature elements** (use, don't dilute):
   - **Detail panel**: key facts (event details, dates, a highlighted number) in
     a light inset panel — `#f5f2ec`, 1px `#e7e5e4` border, 3px amber left edge,
     mono uppercase label in amber, headline detail in ink. Plain language, no
     code or YAML.
   - **Edition number**: `Nº 0NN · YYYY-MM-DD` in Geist Mono, amber, in the
     amber-wash masthead — increments every send.
   - **Headline accent**: the key word or phrase of the H1 in amber `#b45309`
     (mirrors the site's "Computable law for all." treatment).
   - **Artifact chips**: each story row is labeled by what kind of artifact it is
     (`corpus`, `engine`, `api`, `event`, `research`) — lowercase mono chip with
     1px `#d9b28a` border. Structure encodes content type, never decoration.
   - **One CTA button** per edition (amber, hero). All other links are mono
     arrow-links (`label →`) in amber.
   - **∀ note**: optional standing mission note in an inset panel with a 3px
     amber left border and the ∀ glyph (U+2200).
6. **Mailchimp Variables**: Footer includes merge tags like `*|EMAIL|*`, `*|UNSUB|*`, `*|UPDATE_PROFILE|*`, `*|LIST:ADDRESSLINE|*`
7. **Logo**: Gradient wordmark on the amber-wash masthead:
   `https://raw.githubusercontent.com/TheAxiomFoundation/axiom-brand/main/png/wordmark/axiom-full-gradient-2400w.png`
   (full lockup with FOUNDATION subline — brand rule: outward-facing surfaces use
   the FULL lockup until brand recognition is established)

## Creating New Newsletters

**IMPORTANT: Always start from the most recent newsletter as a template.** The
template structure evolves over time, so copying from the latest edition ensures
current styling and layout patterns. If `editions/` is empty, start from
`templates/axiom-newsletter-template.html`.

1. Find the most recent newsletter in `editions/` (sorted by date)
2. Copy it as a new file with date format: `YYYY-MM-DD.html` (add an audience
   suffix like `-uk` only if the send is segmented)
3. Update content while maintaining:
   - Inline styles for email client compatibility
   - Responsive table layout in footer (Mailchimp CAN-SPAM compliance)
   - Mailchimp merge tags in footer
   - External assets use full URLs (no relative paths)

## Email Compatibility

### ⚠️ CRITICAL: All Images Must Use Absolute URLs

**NEVER use relative paths** like `../assets/images/...` or `./images/...` in newsletters.

Email clients fetch images from URLs - they cannot resolve relative paths. Always use absolute URLs:

```html
<!-- ❌ WRONG - will show broken image -->
<img src="../assets/images/dashboard.png">

<!-- ✅ CORRECT - absolute URL -->
<img src="https://raw.githubusercontent.com/TheAxiomFoundation/newsletters/main/assets/images/dashboard.png">
```

For images on a feature branch, use the branch name (but merge before sending so
`main` URLs resolve):
```
https://raw.githubusercontent.com/TheAxiomFoundation/newsletters/branch-name/assets/images/image.png
```

Never use `refs/heads/` in URLs — it can break rendering in Mailchimp
(`scripts/lint-newsletters.sh` enforces both rules, and CI runs it).

### Other Email Compatibility Rules

- **No CSS files**: All styles must be inline
- **Limited CSS**: Avoid modern CSS features (flexbox, grid)
- **Table layouts**: Use tables for complex layouts (email clients don't support modern layout)
- **No JavaScript**: Email clients block JavaScript
- **External images**: Use full URLs for all images
- **Responsive design**: Use media queries in `<style>` tags for mobile
- **Logo format**: Use the PNG wordmarks from axiom-brand (Outlook and some
  clients block SVGs)

## Voice and Content

- Sentence case headings; no emoji in research/engineering sections
- Lead with the concrete result ("all fourteen IFR sections encoded"), not the
  activity ("we worked on encodings")
- Audience: policy technologists, benefits-delivery teams, civic-tech engineers,
  funders
- Standing footer links: Website (axiom-foundation.org), GitHub
  (github.com/TheAxiomFoundation), Contact (hello@axiom-foundation.org)

## File Naming Conventions

- Newsletter editions: `YYYY-MM-DD.html` (e.g., `2026-08-01.html`)
- Images: Descriptive names in `assets/images/`

## Configuration

- `config/mailchimp-settings.json` contains an API key placeholder (the real key
  is never committed)
- `.env` file contains `MAILCHIMP_API_KEY` and `MAILCHIMP_LIST_ID` for the
  upload script (gitignored)
- No build configuration needed

## Uploading to Mailchimp

This repo includes a Python package (`newsletter_uploader`) with full test coverage.

### Installation

```bash
pip install -e ".[dev]"
export MAILCHIMP_API_KEY="your-key-usX"
export MAILCHIMP_LIST_ID="your-list-id"
```

### Usage

```bash
# All subscribers (the normal case)
upload-newsletter editions/2026-08-01.html \
  --audience all \
  --subject "Axiom launch: the world's rules, encoded" \
  --preview "RuleSpec, the engine, and the API"
```

**Audience targeting:**
- `--audience all` - All subscribers (no filtering)
- `--audience uk` - Only subscribers with `COUNTRY` = "United Kingdom" (requires
  a `COUNTRY` merge field on the Mailchimp audience)
- `--audience us` - All non-UK subscribers (includes missing country data)

The command creates a **draft campaign** (not sent) that you can review, test,
and send from the Mailchimp web interface. Sender defaults are
`Axiom Foundation <hello@axiom-foundation.org>`.

### Updating Existing Drafts

**IMPORTANT:** When making changes to a newsletter that has already been
uploaded to Mailchimp, **update the existing campaign** instead of creating a
new one:

```bash
upload-newsletter editions/2026-08-01.html \
  --campaign-id existing-campaign-id \
  --subject "..." \
  --preview "..."
```

### Development

```bash
pytest -v
black src/ tests/
ruff check src/ tests/
```

## Claude Code Automations

Custom subagents and slash commands for newsletter workflow (see `.claude/README.md`):

**Subagents:**
- `newsletter-writer` - Converts posts/updates into Axiom-styled newsletter HTML sections
- `campaign-analyzer` - Analyzes Mailchimp performance data

**Slash Commands:**
- `/create-newsletter --stories story1,story2 --audience all`
- `/preview-newsletter editions/file.html`
- `/upload-draft editions/file.html --audience all --subject "..." --preview "..."`
- `/campaign-stats 2026-08-01`
