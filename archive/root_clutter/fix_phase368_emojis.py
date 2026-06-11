#!/usr/bin/env python
"""Fix emojis in phase 368"""

with open('c:\\Genesis_System3\\core\\engine\\system3_phase368_broker_latency_monitor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emojis with ASCII equivalents
replacements = [
    ('"normal": "🟢"', '"normal": "[OK]"'),
    ('"elevated": "🟡"', '"elevated": "[WARN]"'),
    ('"critical": "🔴"', '"critical": "[ALERT]"'),
    ('"unknown": "⚪"', '"unknown": "[INFO]"'),
    ('### 🟢', '### [OK]'),
    ('### 🟡', '### [WARN]'),
    ('### 🔴', '### [ALERT]'),
    ('### 🟠', '### [CAUTION]'),
    ('"🔴" if anomaly["severity"] == "critical" else "🟠" if anomaly["severity"] == "high" else "🟡"', 
     '"[ALERT]" if anomaly["severity"] == "critical" else "[CAUTION]" if anomaly["severity"] == "high" else "[WARN]"'),
    ('**Status:** ✅ Monitoring Complete', '**Status:** [OK] Monitoring Complete'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('c:\\Genesis_System3\\core\\engine\\system3_phase368_broker_latency_monitor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Phase 368 emojis fixed!")
