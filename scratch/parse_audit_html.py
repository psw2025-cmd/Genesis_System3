import os
import re

audit_path = r"C:\Users\ADMIN\Downloads\dashboard-ui-ux-audit.html"
with open(audit_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

print(f"Total HTML size: {len(html):,} bytes")

# Replace base64 images with placeholder so we can inspect pure text
text_no_images = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[BASE64_IMAGE]', html)
print(f"Text size without base64: {len(text_no_images):,} bytes")

# Write text_no_images to scratch file for easy inspection
scratch_path = r"C:\Genesis_System3_clean\scratch\audit_content_no_images.html"
os.makedirs(os.path.dirname(scratch_path), exist_ok=True)
with open(scratch_path, "w", encoding="utf-8") as f:
    f.write(text_no_images)

print(f"Written to {scratch_path}")
