from pathlib import Path

app_path = Path(r"c:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

# Remove any existing from __future__ and import logging lines that were added
text = text.replace("from __future__ import annotations\n", "")
text = text.replace("import logging\nlogger = logging.getLogger(__name__)\n", "")

# Strip BOM if present
text = text.replace("\ufeff", "").strip()

# Now place from __future__ at the very top, followed by logging
header = 'from __future__ import annotations\nimport logging\nlogger = logging.getLogger(__name__)\n\n'
text = header + text

app_path.write_text(text, encoding="utf-8")
print("Placed from __future__ at line 1 and logging below it in app.py!")
