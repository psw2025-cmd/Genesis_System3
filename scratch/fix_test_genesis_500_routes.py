import shutil
from pathlib import Path

# 1. Update tests/test_genesis_500_routes.py
t_path = Path("tests/test_genesis_500_routes.py")
text = t_path.read_text(encoding="utf-8")
old = 'sys.path.insert(0, r"C:\\content\\app")'
new = """ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content" / "app"))"""
if old in text:
    t_path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Updated test_genesis_500_routes.py to use workspace content/app")
else:
    print("old not found in test_genesis_500_routes.py")

# 2. Also sync premium.html to C:\content\app\templates\premium.html
src_html = Path("content/app/templates/premium.html")
dest_html = Path("C:/content/app/templates/premium.html")
if dest_html.parent.exists():
    shutil.copy2(src_html, dest_html)
    print("Synced premium.html to C:/content/app/templates/premium.html")
