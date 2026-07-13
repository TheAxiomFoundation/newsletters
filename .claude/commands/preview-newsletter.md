---
description: Preview newsletter HTML with screenshots and validation checks
argument-hint: <html-file>
---

Open the newsletter in a browser, capture screenshots, and validate email compatibility.

## Usage

```bash
/preview-newsletter editions/2026-08-01.html
```

## Process

Use the `newsletter-previewer` subagent to:

1. **Open in browser** - Display the HTML for visual review
2. **Capture screenshots** - Desktop (600px) and mobile (320px) views
3. **Validate compatibility** - Check for email client issues
4. **Review content** - Verify links, images, styling

## What Gets Checked

**Email Compatibility:**
- Inline styles only (no external CSS)
- 600px max width
- No modern CSS features (flexbox/grid)
- Table-based layouts
- Full URLs for images (no relative paths, no refs/heads/)
- Mailchimp merge tags present

**Visual Quality (Axiom brand):**
- Paper wordmark renders on the ink header
- Amber hero gradient (#b45309 → #8a3d08) displays properly
- CTAs are amber on paper; text readable on all backgrounds
- Cards and sections have proper borders

**Content:**
- All links valid and working
- Images load correctly
- Headers use sentence case
- Professional tone

## When to Use

- Before uploading to Mailchimp
- After making styling changes
- Before scheduling a send
