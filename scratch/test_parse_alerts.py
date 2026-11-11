import json

alerts = []
with open('c:/Genesis_System3_clean/outputs/alerts.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<'):
            try:
                alerts.append(json.loads(line))
            except Exception as e:
                print("Failed parsing line:", line[:50], e)

print("Parsed alerts count:", len(alerts))
for a in alerts:
    print(a)
