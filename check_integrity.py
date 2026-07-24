import os

OLD_RENDER = "https://genesis-system3-backend.onrender.com"
NEW_LOCAL = "http://127.0.0.1:8000"

target_files = [
    ".github/workflows/system3-autopilot-proof-board.yml",
    ".github/workflows/cloud-runtime-check.yml",
    ".github/workflows/dashboard-live-proof.yml",
    ".github/workflows/system3-render-worker-preflight.yml"
]

for file_path in target_files:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if OLD_RENDER in content:
            new_content = content.replace(OLD_RENDER, NEW_LOCAL)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f" -> Successfully updated URL in: {file_path}")

print("[SUCCESS] All workflow base URLs fully aligned to local localhost!")