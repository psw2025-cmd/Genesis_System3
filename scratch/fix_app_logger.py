from pathlib import Path

app_path = Path(r"c:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

if "logger = logging.getLogger(__name__)" not in text:
    text = "import logging\nlogger = logging.getLogger(__name__)\n" + text
    app_path.write_text(text, encoding="utf-8")
    print("Added import logging and logger definition to app.py!")
else:
    print("logger already defined in app.py")
