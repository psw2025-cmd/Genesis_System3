"""Forensic search for 'No chain data available' and related chain data keywords across Genesis System3.
Exports comprehensive structured results to CSV in temp folders.
"""
import os
import re
import csv
import tempfile

REGEX_EXACT = re.compile(r"no\s+chain\s+data\s+available", re.IGNORECASE)
REGEX_BROAD = re.compile(r"no\s+(?:option\s+)?chain\s+data(?:\s+available)?", re.IGNORECASE)

ROOT_DIR = r"C:\Genesis_System3_clean"
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".agy-proof"}

findings = []

for root, dirs, files in os.walk(ROOT_DIR):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        filepath = os.path.join(root, file)
        relpath = os.path.relpath(filepath, ROOT_DIR).replace("\\", "/")
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f, start=1):
                    match_exact = REGEX_EXACT.search(line)
                    match_broad = REGEX_BROAD.search(line)
                    if match_exact or match_broad:
                        match_type = "EXACT_PHRASE" if match_exact else "BROAD_PHRASE"
                        matched_text = match_exact.group(0) if match_exact else match_broad.group(0)
                        findings.append({
                            "match_type": match_type,
                            "matched_keyword": matched_text,
                            "relative_path": relpath,
                            "line_number": line_idx,
                            "line_content": line.strip(),
                            "file_extension": os.path.splitext(file)[1],
                            "absolute_path": filepath
                        })
        except Exception:
            pass

print(f"Total occurrences found: {len(findings)}")

# Save destinations:
# 1. C:\tmp\no_chain_data_available_occurrences.csv
# 2. C:\Genesis_System3_clean\temp\no_chain_data_available_occurrences.csv
# 3. System temp folder
# 4. Artifact directory
temp_dirs = [
    r"C:\tmp",
    os.path.join(ROOT_DIR, "temp"),
    os.path.join(ROOT_DIR, "reports", "temp"),
    tempfile.gettempdir(),
    r"C:\Users\ADMIN\.gemini\antigravity-cli\brain\3957d29d-e75a-4a9f-86fb-5d267e6799ee"
]

csv_filename = "no_chain_data_available_occurrences.csv"
fieldnames = [
    "match_type",
    "matched_keyword",
    "relative_path",
    "line_number",
    "line_content",
    "file_extension",
    "absolute_path"
]

for td in temp_dirs:
    try:
        os.makedirs(td, exist_ok=True)
        dest = os.path.join(td, csv_filename)
        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in findings:
                writer.writerow(row)
        print(f"Saved CSV to: {dest}")
    except Exception as e:
        print(f"Could not write to {td}: {e}")

print("\n--- Summary of Matches ---")
for r in findings:
    print(f"[{r['match_type']}] {r['relative_path']}:{r['line_number']} -> {r['line_content'][:90]}")

"""
# The following docstring protects against appended markdown
"""

