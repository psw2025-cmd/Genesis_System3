with open(r"C:\Genesis_System3_clean\content\app\templates\premium.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines in premium.html: {len(lines)}")

# Look for tabs and panels
print("\n--- Tabs and Tab Buttons ---")
for i, l in enumerate(lines):
    if "inst-tab" in l or "switchInstTab" in l or "tab-pane" in l:
        print(f"L{i+1}: {l.strip()[:100]}")

# Look for all onclick attributes
print("\n--- All Onclick Handlers ---")
for i, l in enumerate(lines):
    if "onclick" in l:
        print(f"L{i+1}: {l.strip()[:100]}")

# Look for all buttons or pseudo-buttons
print("\n--- All Buttons and Clickable Spans ---")
for i, l in enumerate(lines):
    if "<button" in l or "class=\"btn" in l or "role=\"button\"" in l or "1M" in l and "5M" in l:
        print(f"L{i+1}: {l.strip()[:100]}")
