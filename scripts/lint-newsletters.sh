#!/bin/bash
# Lint newsletter HTML files for common email compatibility issues

set -e
shopt -s nullglob

ERRORS=0
FILES=(editions/*.html templates/*.html)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No newsletter HTML files found - nothing to lint."
    exit 0
fi

echo "Checking newsletter HTML files..."

for file in "${FILES[@]}"; do
    echo "  Checking $file..."

    # Check for relative image paths (../  or ./ or just images/)
    if grep -qE 'src="\.\./' "$file" || grep -qE 'src="\./' "$file" || grep -qE 'src="[^h][^t][^t][^p].*\.(png|jpg|jpeg|gif|svg)"' "$file"; then
        echo "    ❌ ERROR: Relative image path found. Use absolute URLs (https://...)"
        grep -nE 'src="\.\./' "$file" || true
        grep -nE 'src="\./' "$file" || true
        ERRORS=$((ERRORS + 1))
    fi

    # Check for refs/heads/ in URLs - causes rendering issues in Mailchimp
    if grep -q 'refs/heads/' "$file"; then
        echo "    ❌ ERROR: URL contains refs/heads/ which can break in Mailchimp. Use /main/ directly."
        grep -n 'refs/heads/' "$file"
        ERRORS=$((ERRORS + 1))
    fi

done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ Found $ERRORS error(s). Please fix before committing."
    exit 1
else
    echo ""
    echo "✅ All newsletter files passed lint checks."
fi
