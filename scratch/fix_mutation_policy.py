from pathlib import Path

p = Path("dashboard/backend/mutation_policy.py")
text = p.read_text(encoding="utf-8")

old = """    if p.startswith((
        "/api/live-trading/",
        "/api/orders/","""

new = """    if p.startswith((
        "/api/live-trading/",
        "/api/orders/",
        "/api/v1/placeorder","""

if old in text:
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Updated mutation_policy.py")
else:
    print("Pattern not found in mutation_policy.py")
