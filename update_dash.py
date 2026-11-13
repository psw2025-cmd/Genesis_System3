from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\dashboard\backend\app.py")
text = p.read_text(encoding="utf-8")

old = '''        status["token_proof"] = {
            "source": f"GCP_SECRET_MANAGER_V{ver_num}" if not is_fallback else "GCP_SECRET_MANAGER_V335",
            "secret_version": f"GCP_V{ver_num}" if not is_fallback else "GCP_V335",'''

new = '''        status["token_proof"] = {
            "source": source_str,
            "secret_version": source_str,'''

if old in text:
    text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")
    print("SUCCESS: updated token_proof in dashboard/backend/app.py")
else:
    print("Pattern not found or already updated")
