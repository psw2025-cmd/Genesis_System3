# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_NAME = "SYSTEM3_FOLDER_DEEP_REPORT.md"
PART1_NAME = "SYSTEM3_FOLDER_DEEP_REPORT_PART1.md"
PART2_NAME = "SYSTEM3_FOLDER_DEEP_REPORT_PART2.md"


def main():
    report_path = os.path.join(BASE_DIR, REPORT_NAME)
    part1_path = os.path.join(BASE_DIR, PART1_NAME)
    part2_path = os.path.join(BASE_DIR, PART2_NAME)

    if not os.path.exists(report_path):
        print(f"[ERROR] '{REPORT_NAME}' not found in {BASE_DIR}")
        print("Make sure SYSTEM3_FOLDER_DEEP_REPORT.md is in the same folder as this script.")
        sys.exit(1)

    print(f"[INFO] Reading report: {report_path}")
    
    # Read file to calculate sizes
    with open(report_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        lines = content.splitlines(keepends=True)
    
    total_lines = len(lines)
    if total_lines == 0:
        print("[ERROR] Report file is empty.")
        sys.exit(1)
    
    # Calculate cumulative byte sizes for each line
    print("[INFO] Calculating line sizes...")
    line_sizes = []
    for line in lines:
        line_sizes.append(len(line.encode('utf-8')))
    
    total_size = sum(line_sizes)
    target_size = total_size // 2
    
    print(f"[INFO] Total size: {total_size:,} bytes")
    print(f"[INFO] Target size per part: {target_size:,} bytes")
    
    # Find the exact split point by cumulative size
    print("[INFO] Finding optimal split point...")
    cumulative = 0
    best_split = 0
    best_diff = total_size  # Start with worst case
    
    # Find the line index where cumulative size is closest to target
    for i in range(total_lines):
        cumulative += line_sizes[i]
        diff = abs(cumulative - target_size)
        if diff < best_diff:
            best_diff = diff
            best_split = i + 1
    
    # Verify the split point
    part1_size_at_best = sum(line_sizes[:best_split])
    part2_size_at_best = sum(line_sizes[best_split:])
    
    print(f"[INFO] Optimal split found at line {best_split}")
    print(f"[INFO]   Part 1 size: {part1_size_at_best:,} bytes ({part1_size_at_best*100//total_size}%)")
    print(f"[INFO]   Part 2 size: {part2_size_at_best:,} bytes ({part2_size_at_best*100//total_size}%)")
    print(f"[INFO]   Size difference: {abs(part1_size_at_best - part2_size_at_best):,} bytes")
    
    # Use the size-optimized split (NO heading alignment to ensure equal sizes)
    start2_index = best_split
    
    # Safety: ensure there is at least something in both parts
    if start2_index <= 5:
        print(f"[WARN] Split too early (line {start2_index}), adjusting...")
        start2_index = total_lines // 2
    if start2_index >= total_lines - 5:
        print(f"[WARN] Split too late (line {start2_index}), adjusting...")
        start2_index = total_lines // 2

    part1_lines = lines[:start2_index]
    part2_lines = lines[start2_index:]
    
    part1_size = sum(line_sizes[:start2_index])
    part2_size = sum(line_sizes[start2_index:])
    
    print(f"\n[INFO] Split Summary:")
    print(f"[INFO] Total lines       : {total_lines}")
    print(f"[INFO] Part 1 line count : {len(part1_lines)}")
    print(f"[INFO] Part 1 size       : {part1_size:,} bytes ({part1_size*100//total_size}%)")
    print(f"[INFO] Part 2 line count : {len(part2_lines)}")
    print(f"[INFO] Part 2 size       : {part2_size:,} bytes ({part2_size*100//total_size}%)")
    print(f"[INFO] Size difference   : {abs(part1_size - part2_size):,} bytes")
    
    # Check size ratio
    size_ratio = max(part1_size, part2_size) / min(part1_size, part2_size) if min(part1_size, part2_size) > 0 else 0
    if size_ratio > 1.05:  # More than 5% difference
        print(f"[WARN] Size ratio is {size_ratio:.2f}:1 - parts are not perfectly equal")
        print(f"[INFO] This may be due to very uneven line sizes in the source file")
    else:
        print(f"[OK] Parts are approximately equal (ratio: {size_ratio:.2f}:1)")

    # Optional: add explicit headers to each part
    header1 = [
        "# SYSTEM3 FOLDER DEEP REPORT - PART 1\n",
        "_Original file: SYSTEM3_FOLDER_DEEP_REPORT.md_\n\n",
    ]
    header2 = [
        "# SYSTEM3 FOLDER DEEP REPORT - PART 2\n",
        "_Original file: SYSTEM3_FOLDER_DEEP_REPORT.md_\n\n",
    ]

    print(f"\n[INFO] Writing output files...")
    with open(part1_path, "w", encoding="utf-8", errors="replace") as f:
        f.writelines(header1 + part1_lines)

    with open(part2_path, "w", encoding="utf-8", errors="replace") as f:
        f.writelines(header2 + part2_lines)
    
    # Get final file sizes
    final_part1_size = os.path.getsize(part1_path)
    final_part2_size = os.path.getsize(part2_path)
    final_total_size = final_part1_size + final_part2_size

    print(f"\n[OK] Files written successfully!")
    print(f"[INFO] Final Part 1 size: {final_part1_size:,} bytes ({final_part1_size*100//final_total_size}%)")
    print(f"[INFO] Final Part 2 size: {final_part2_size:,} bytes ({final_part2_size*100//final_total_size}%)")
    print(f"[INFO] Final size difference: {abs(final_part1_size - final_part2_size):,} bytes")
    
    # Final check
    final_ratio = max(final_part1_size, final_part2_size) / min(final_part1_size, final_part2_size) if min(final_part1_size, final_part2_size) > 0 else 0
    if final_ratio > 1.05:
        print(f"[WARN] Final size ratio is {final_ratio:.2f}:1")
        print(f"[INFO] The file has very uneven line sizes - this is the best equal split possible")
    else:
        print(f"[OK] Parts are approximately equal (ratio: {final_ratio:.2f}:1)")
    
    print("\n[DONE] You can now upload PART1 and PART2 separately to ChatGPT.")


if __name__ == "__main__":
    main()
