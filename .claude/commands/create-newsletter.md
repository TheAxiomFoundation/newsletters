---
description: Create a newsletter from Axiom stories and event information
argument-hint: --stories story1,story2 [--event event-slug] [--audience all|uk|us]
---

Create a new newsletter HTML file from Axiom Foundation stories (blog posts, release notes, repo milestones) and optional event information.

## Usage

```bash
/create-newsletter --stories launch-recap,rulespec-us-milestone --audience all
/create-newsletter --stories medicaid-ce-encodings --event ifc-comment-webinar --audience us
```

## Process

1. **Parse arguments** from `$ARGUMENTS`:
   - `--stories`: Comma-separated story identifiers. Each may be a markdown file path, a URL, or a slug to locate in the axiom-foundation.org content or a repo changelog.
   - `--event`: Optional event slug (looks for a matching .md file or registration link)
   - `--audience`: Target audience (all, uk, or us) - defaults to all

2. **For each story**:
   - Use the `newsletter-writer` subagent to generate an HTML section
   - Lead with the concrete result; include one call-to-action link

3. **Compile newsletter**:
   - Copy the most recent file in `editions/` (or `templates/axiom-newsletter-template.html` if none) to `editions/YYYY-MM-DD.html` with today's date
   - Put the strongest story in the amber hero section
   - Add remaining stories as content-card sections
   - Keep footer with Mailchimp merge tags intact

4. **Show result**:
   - Path to generated file
   - Preview of content
   - Next steps: `/preview-newsletter`, then `/upload-draft`

## Example Output

```
✅ Newsletter created: editions/2026-08-01.html

Sections included:
  • Hero: Axiom public launch recap
  • Update: rulespec-us Medicaid CE coverage complete
  • Update: axiom-api trial keys open

Next steps:
  /upload-draft editions/2026-08-01.html --audience all --subject "..." --preview "..."
```
