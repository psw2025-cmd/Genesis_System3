with open(r"C:\Genesis_System3_clean\content\app\templates\premium.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(r"C:\Genesis_System3_clean\reports\latest\tabs_preview.txt", "w", encoding="utf-8") as out:
    for i in range(340, 520):
        if i < len(lines):
            out.write(f"L{i+1}: {lines[i]}")
print("Saved tabs_preview.txt")
