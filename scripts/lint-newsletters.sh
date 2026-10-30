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
SCRIPT_DIR="$(dirname "$0")"
PYTHON="$(command -v python3 || true)"
if [ -z "$PYTHON" ]; then
    echo "  ❌ ERROR: python3 is required to check for hosting addresses. Install Python and rerun the lint."
    exit 1
fi

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

    # Check every edition and template: public links go to axiom.org.
    # The checker decodes entities and percent-escapes and prints line:host.
    hosting_status=0
    hosting=$(PYTHONPATH="$SCRIPT_DIR/../src" "$PYTHON" -m newsletter_uploader.hosting_links "$file") || hosting_status=$?
    if [ "$hosting_status" -eq 1 ] && [ -n "$hosting" ]; then
        echo "    ❌ ERROR: Link to a hosting address. Public links go to the page's axiom.org route, never *.vercel.app, theaxiomfoundation.github.io or another hosting address (see \"Links\" in CLAUDE.md)."
        echo "$hosting"
        if [ -n "$GITHUB_ACTIONS" ]; then
            while IFS= read -r entry; do
                echo "::error file=$file,line=${entry%%:*}::Links ${entry#*:}, a hosting address. Link the axiom.org route instead (see \"Links\" in CLAUDE.md)."
            done <<< "$hosting"
        fi
        ERRORS=$((ERRORS + 1))
    elif [ "$hosting_status" -ne 0 ] || [ -n "$hosting" ]; then
        echo "    ❌ ERROR: Could not check $file for hosting addresses. Fix the checker before committing."
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
