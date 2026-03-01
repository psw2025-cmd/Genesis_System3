import os
from pathlib import Path

outputs_dir = Path("outputs")
print(f"Listing files in {outputs_dir.resolve()}:")

if not outputs_dir.exists():
    print("outputs/ directory does not exist.")
else:
    for f in outputs_dir.iterdir():
        if f.is_file():
            print(f"{f.name} - {f.stat().st_size} bytes")
