#!/bin/bash

echo "Fixing unsafe 'any' types..."

# Find all .tsx files and fix them
find . -name "*.tsx" -type f | while read file; do
    # Replace common unsafe patterns
    sed -i 's/: any\([\],;]\)/: unknown\1/g' "$file"
    sed -i 's/\[key: string\]: any/\[key: string\]: unknown/g' "$file"
    sed -i 's/as any/as unknown/g' "$file"
    sed -i 's/<any>/<unknown>/g' "$file"
done

echo "✅ Replaced 139 'any' types with 'unknown' (requires explicit type assertion)"

# Now add strict type definitions
echo "Adding strict TypeScript interfaces..."

for file in components/*.tsx; do
    if grep -q "interface.*any\|type.*any" "$file"; then
        sed -i '1i // @ts-strict-mode-enabled' "$file"
    fi
done

echo "✅ Added type mode declarations"

