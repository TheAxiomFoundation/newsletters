---
description: Get campaign statistics from Mailchimp
argument-hint: <YYYY-MM-DD>
---

Fetch and display statistics for a newsletter campaign by date.

## Usage

```bash
/campaign-stats 2026-08-01
```

## Process

1. **Extract date** from `$1` argument

2. **Use campaign-analyzer subagent** to:
   - Fetch all sent campaigns from Mailchimp (credentials from `.env`)
   - Find campaign matching the date
   - Retrieve detailed statistics
   - Analyze performance

3. **Display metrics**:
   - Campaign subject line and send time
   - Recipients count
   - Open rate (unique opens / sent)
   - Click rate (subscriber clicks / sent)
   - Top clicked links
   - Archive URL

4. **Provide context**:
   - Compare to newsletter average
   - Identify standout performance areas
   - Suggest improvements if below average

## Error Handling

If no campaign found for the date, show available campaigns from the past 3 months.
