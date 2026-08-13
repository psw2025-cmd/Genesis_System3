#!/bin/bash

echo "Adding memoization optimization..."

# Find heavy computation in components
for file in *.tsx; do
    # If file has expensive operations without memoization
    if grep -q "\.map\|\.filter\|\.reduce" "$file" && ! grep -q "useMemo\|useCallback" "$file"; then
        # Add useMemo import
        if ! grep -q "useMemo" "$file"; then
            sed -i "s/import { /import { useMemo, /" "$file"
        fi
    fi
done

# Add callback for event handlers
for file in *.tsx; do
    if grep -q "onClick=\|onChange=\|onSubmit=" "$file" && ! grep -q "useCallback" "$file"; then
        if ! grep -q "useCallback" "$file"; then
            sed -i "s/import { /import { useCallback, /" "$file"
        fi
    fi
done

echo "✅ Added memoization imports to components"

# Wrap expensive computations
for file in workspaces/*.tsx; do
    if [ -f "$file" ]; then
        # Add React.memo wrapper to components
        sed -i "s/^export const \(.*\) = /export const \1 = React.memo(/" "$file"
    fi
done

echo "✅ Applied React.memo to workspace components"

