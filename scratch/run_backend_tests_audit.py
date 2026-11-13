import subprocess
import sys
import json
from pathlib import Path

python_exe = r"C:\Genesis_System3_clean\.venv\Scripts\python.exe"

# Run pytest on all test files with --collect-only first to know what tests exist
collect = subprocess.run(
    [python_exe, "-m", "pytest", "--collect-only", "-q"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)
lines = [l for l in collect.stdout.splitlines() if "::" in l]
print(f"Total collected tests: {len(lines)}")

# Let's run pytest with -ra and a summary
test_proc = subprocess.run(
    [python_exe, "-m", "pytest", "-ra", "-q", "--tb=short"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=300
)

print("Pytest stdout preview:")
out_lines = test_proc.stdout.splitlines()
for l in out_lines[-30:]:
    print(l)

if test_proc.stderr:
    print("Pytest stderr preview:")
    err_lines = test_proc.stderr.splitlines()
    for l in err_lines[-20:]:
        print(l)

Path("scratch/pytest_full_output.txt").write_text(test_proc.stdout + "\n" + test_proc.stderr, encoding="utf-8")
print(f"Return code: {test_proc.returncode}")
