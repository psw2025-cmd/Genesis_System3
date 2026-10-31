#!/usr/bin/env python3
"""
System3 Ultra - Comprehensive Reference Verification Script
File: verify_references.py
Path: ./verify_references.py

Purpose:
    Verifies the existence of system3_ultra_weekly_runner.py and dynamically 
    scans all files in docs/ and the root directory for references.
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TARGET_FILE = "system3_ultra_weekly_runner.py"

def check_target_file_exists(root_dir: str) -> bool:
    target_path = os.path.join(root_dir, TARGET_FILE)
    exists = os.path.isfile(target_path)
    status_str = "EXISTS" if exists else "MISSING"
    print(f"[{status_str}] Target File: {TARGET_FILE}")
    return exists

def get_all_scannable_files(root_dir: str) -> list:
    """Collects all .md, .py, and text files from root and docs/ subfolders."""
    scannable_files = []
    valid_extensions = ('.md', '.py', '.txt', '.rst', '.json', '.yaml', '.yml')

    # 1. Root level files
    for entry in os.listdir(root_dir):
        full_path = os.path.join(root_dir, entry)
        if os.path.isfile(full_path) and entry.endswith(valid_extensions):
            if entry != os.path.basename(__file__):  # Skip verify_references.py
                scannable_files.append(full_path)

    # 2. Files inside docs/ folder (recursive)
    docs_dir = os.path.join(root_dir, "docs")
    if os.path.isdir(docs_dir):
        for subroot, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(valid_extensions):
                    scannable_files.append(os.path.join(subroot, file))

    return scannable_files

def scan_file_for_reference(file_path: str, root_dir: str) -> int:
    rel_path = os.path.relpath(file_path, root_dir)
    matches = 0
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, 1):
                if TARGET_FILE in line:
                    if matches == 0:
                        print(f"Scanning: {rel_path}")
                    matches += 1
                    print(f"  [MATCH] Line {line_no}: {line.strip()}")
    except Exception as e:
        print(f"  [ERROR] Could not read {rel_path}: {e}")

    return matches

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    print("=" * 70)
    print("SYSTEM3 ULTRA - DYNAMIC REFERENCE VERIFICATION SUITE")
    print(f"Root Directory: {root_dir}")
    print("=" * 70 + "\n")

    # 1. Check if target file exists
    file_exists = check_target_file_exists(root_dir)
    print("-" * 70 + "\n")

    # 2. Gather files from root and docs/
    files_to_scan = get_all_scannable_files(root_dir)
    print(f"Discovered {len(files_to_scan)} file(s) to scan in root and docs/\n")

    # 3. Perform scan
    total_references = 0
    files_with_references = 0

    for file_path in files_to_scan:
        count = scan_file_for_reference(file_path, root_dir)
        if count > 0:
            total_references += count
            files_with_references += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Target File ({TARGET_FILE}): {'Found' if file_exists else 'MISSING'}")
    print(f"Total Files Scanned: {len(files_to_scan)}")
    print(f"Files Containing References: {files_with_references}")
    print(f"Total Reference Instances: {total_references}")
    print("=" * 70)

if __name__ == "__main__":
    main()