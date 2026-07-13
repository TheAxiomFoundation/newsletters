# Claude Code Configuration

Custom subagents and slash commands for Axiom Foundation newsletter management.

## Subagents

### newsletter-writer
Converts Axiom updates (blog posts, release notes, repo milestones) into email-compatible newsletter HTML sections with Axiom brand styling.

### newsletter-previewer
Opens newsletter HTML in a browser, captures desktop/mobile screenshots, and validates email-client compatibility.

### campaign-analyzer
Fetches campaign statistics from the Mailchimp API, identifies performance trends, and suggests improvements.

## Slash Commands

- `/create-newsletter --stories story1,story2 [--audience all|uk|us]` — assemble a new edition in `editions/`
- `/preview-newsletter editions/file.html` — screenshots + compatibility report
- `/upload-draft editions/file.html --audience all --subject "..." --preview "..."` — create a Mailchimp draft
- `/campaign-stats YYYY-MM-DD` — performance report for a sent campaign

## Example Workflow

```bash
/create-newsletter --stories launch-recap,rulespec-us-milestone --audience all
/preview-newsletter editions/2026-08-01.html
/upload-draft editions/2026-08-01.html --audience all --subject "..." --preview "..."
/campaign-stats 2026-08-01
```
