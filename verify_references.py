#!/usr/bin/env python3
"""
System3 Ultra - Reference Verification Script
File: verify_references.py
Path: ./verify_references.py

Purpose:
    Verifies the existence of system3_ultra_weekly_runner.py and scans 
    all workspace files to check for direct references to it.
"""

import os
import sys

TARGET_FILE = "system3_ultra_weekly_runner.py"

DOCUMENTATION_FILES = [
    "system3_ultra_delivery_summary.md",
    "system3_ultra_implementation_complete.md",
    "system3_ultra_commands.md",
    "system3_operational_master_playbook.md",
    "system3_ultra_launch_flow.md",
    "system3_directory_tree.md",
    "system3_ultra_expected_outputs.md",
    "system3_ultra_validation.py",
    "system3_ultra.py"
]

def check_target_file_exists(root_dir: str) -> bool:
    target_path = os.path.join(root_dir, TARGET_FILE)
    exists = os.path.isfile(target_path)
    status_str = "EXISTS" if exists else "MISSING"
    print(f"[{status_str}] Target File: {TARGET_FILE}")
    return exists

def scan_file_for_reference(file_path: str) -> int:
    if not os.path.isfile(file_path):
        print(f"  [NOT FOUND] File does not exist locally: {file_path}")
        return 0
    
    matches = 0
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, 1):
                if TARGET_FILE in line:
                    matches += 1
                    print(f"  [MATCH] Line {line_no}: {line.strip()}")
    except Exception as e:
        print(f"  [ERROR] Could not read {file_path}: {e}")
    
    return matches

def main():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    print("=" * 70)
    print("SYSTEM3 ULTRA - REFERENCE VERIFICATION SUITE")
    print(f"Root Directory: {root_dir}")
    print("=" * 70 + "\n")

    # 1. Check if the target file exists locally
    file_exists = check_target_file_exists(root_dir)
    print("-" * 70)

    # 2. Scan documentation and code files for references
    print(f"\nScanning key workspace files for references to '{TARGET_FILE}':\n")
    total_references = 0
    files_scanned = 0

    for rel_path in DOCUMENTATION_FILES:
        full_path = os.path.join(root_dir, rel_path)
        print(f"Scanning: {rel_path}")
        count = scan_file_for_reference(full_path)
        total_references += count
        files_scanned += 1
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Target File ({TARGET_FILE}): {'Found' if file_exists else 'MISSING'}")
    print(f"Files Scanned: {files_scanned}")
    print(f"Total References Found: {total_references}")
    print("=" * 70)

if __name__ == "__main__":
    main()