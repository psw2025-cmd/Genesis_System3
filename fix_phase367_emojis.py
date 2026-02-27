#!/usr/bin/env python
"""Fix remaining emojis and issues in phases"""

import sys

# Fix phase 367 remaining emoji issues
with open('c:\\Genesis_System3\\core\\engine\\system3_phase367_safety_guardrail_recommender.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements_367 = [
    ('⚠️ **', '[WARN] **'),
]

for old, new in replacements_367:
    content = content.replace(old, new)

with open('c:\\Genesis_System3\\core\\engine\\system3_phase367_safety_guardrail_recommender.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Phase 367 fixed!")
