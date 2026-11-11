from pathlib import Path

app_path = Path(r"c:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

# Strip any BOM characters anywhere in text
text = text.replace("\ufeff", "")
app_path.write_text(text, encoding="utf-8")
print("Successfully stripped U+FEFF BOM from app.py!")
