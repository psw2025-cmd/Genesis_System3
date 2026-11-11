import re
from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\content\app\templates\premium.html")
text = p.read_text(encoding="utf-8")

print(f"File size: {len(text)} bytes")

# 1. Broken unicode or question marks
lines = text.splitlines()
print("\n=== Lines with question marks or corrupted symbols ===")
for i, line in enumerate(lines):
    if "?" in line and any(w in line for w in ["GENESIS", "SYSTEM3", "PRODUCTION", "COMMAND"]):
        print(f"L{i+1}: {line.strip()[:100]}")

# 2. Check all buttons and their onclick attributes
print("\n=== Buttons in HTML ===")
buttons = re.findall(r'<button([^>]*)>(.*?)</button>', text, re.DOTALL)
for attrs, content in buttons:
    oc = re.search(r'onclick=[\"\'](.*?)[\"\']', attrs)
    onclick_val = oc.group(1) if oc else "NO ONCLICK"
    bid = re.search(r'id=[\"\'](.*?)[\"\']', attrs)
    id_val = bid.group(1) if bid else "NO ID"
    print(f"Button id='{id_val}' onclick='{onclick_val}' text='{content.strip()}'")

# 3. Check all clickable elements (with onclick)
print("\n=== All elements with onclick ===")
onclick_elements = re.findall(r'<([a-zA-Z0-9]+)[^>]*onclick=[\"\'](.*?)[\"\'][^>]*>(.*?)</\1>', text, re.DOTALL)
for tag, oc, content in onclick_elements:
    clean_content = re.sub(r'<[^>]+>', '', content).strip()[:50]
    print(f"<{tag} onclick='{oc}'> text='{clean_content}'")

# 4. Check all tabs and tab content panes
print("\n=== Institutional Console Tab Panes ===")
tab_panes = re.findall(r'id=[\"\'](inst-tab-\d+)[\"\'][^>]*style=[\"\'](.*?)[\"\']', text)
for t_id, style in tab_panes:
    print(f"Tab Pane: id='{t_id}' style='{style}'")

# 5. Check all scripts and functions
print("\n=== JavaScript Functions Defined ===")
functions = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', text)
for fn in sorted(set(functions)):
    print(f" - {fn}()")
