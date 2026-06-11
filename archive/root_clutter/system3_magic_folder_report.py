import os
import sys
import hashlib
import datetime
from pathlib import Path
import ast
import textwrap

# -------- Config --------
EXCLUDED_DIRS = {".git", "__pycache__", ".mypy_cache", "venv", ".idea"}
# file types for which we also show small previews
TEXT_LIKE_EXT = {".md", ".json", ".yaml", ".yml", ".ini", ".cfg", ".txt", ".bat", ".ps1"}
PY_PREVIEW_LINES = 30
OTHER_PREVIEW_LINES = 15

# keywords we care about (trading / safety / automation flags)
KEYWORDS = [
    "LIVE_TRADING_ENABLED",
    "AUTO_EXECUTE",
    "AUTO_EXECUTION",
    "DRY_RUN",
    "ULTRA_MODE",
    "ULTRA",
    "SAFE_MODE",
    "RISK_LIMIT",
    "KILL_SWITCH",
    "MAX_TRADES_PER_DAY",
    "MAX_TRADES_PER_UNDERLYING",
    "ANGELONE_API_KEY",
    "BROKER",
    "ANGEL",
    "SYSTEM3",
]


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def make_tree(root: Path) -> str:
    """Return a simple text tree of the directory structure."""
    lines = []
    root = root.resolve()
    prefix_map = {}

    def walk(dir_path: Path, prefix: str = ""):
        entries = [e for e in sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))]
        entries = [e for e in entries if e.name not in EXCLUDED_DIRS]
        total = len(entries)
        for i, entry in enumerate(entries):
            connector = "└── " if i == total - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                new_prefix = prefix + ("    " if i == total - 1 else "│   ")
                walk(entry, new_prefix)

    lines.append(root.name)
    walk(root)
    return "\n".join(lines)


def analyze_python_file(path: Path) -> dict:
    info = {
        "path": str(path),
        "rel_path": str(path.relative_to(Path.cwd())),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_of_file(path),
        "num_lines": 0,
        "imports": [],
        "functions": [],
        "classes": [],
        "flags_found": [],
        "preview": "",
        "ast_ok": True,
        "ast_error": None,
    }

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        info["ast_ok"] = False
        info["ast_error"] = f"ERROR reading file: {e}"
        return info

    lines = text.splitlines()
    info["num_lines"] = len(lines)
    preview = "\n".join(lines[:PY_PREVIEW_LINES])
    info["preview"] = preview

    # keyword scan
    found = []
    upper_text = text.upper()
    for kw in KEYWORDS:
        if kw.upper() in upper_text:
            found.append(kw)
    info["flags_found"] = sorted(set(found))

    # AST parse for imports, functions, classes
    try:
        tree = ast.parse(text, filename=str(path))
    except Exception as e:
        info["ast_ok"] = False
        info["ast_error"] = f"AST parse error: {e}"
        return info

    imports = set()
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.FunctionDef):
            functions.append((node.name, node.lineno))
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append((f"async {node.name}", node.lineno))
        elif isinstance(node, ast.ClassDef):
            classes.append((node.name, node.lineno))

    info["imports"] = sorted(imports)
    info["functions"] = sorted(functions, key=lambda x: x[1])
    info["classes"] = sorted(classes, key=lambda x: x[1])

    return info


def analyze_text_like_file(path: Path) -> dict:
    info = {
        "path": str(path),
        "rel_path": str(path.relative_to(Path.cwd())),
        "size_bytes": path.stat().st_size,
        "preview": "",
    }
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        info["preview"] = "\n".join(lines[:OTHER_PREVIEW_LINES])
    except Exception as e:
        info["preview"] = f"ERROR reading file: {e}"
    return info


def split_report_into_3_parts(report_path: Path):
    """Split the report file into 3 approximately equal parts by size."""
    part1_path = report_path.parent / "SYSTEM3_FOLDER_DEEP_REPORT_PART1.md"
    part2_path = report_path.parent / "SYSTEM3_FOLDER_DEEP_REPORT_PART2.md"
    part3_path = report_path.parent / "SYSTEM3_FOLDER_DEEP_REPORT_PART3.md"
    
    # Read file to calculate sizes
    with report_path.open("r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        lines = content.splitlines(keepends=True)
    
    total_lines = len(lines)
    if total_lines == 0:
        print("[ERROR] Report file is empty.")
        return
    
    # Calculate cumulative byte sizes for each line
    print("[INFO] Calculating line sizes...")
    line_sizes = []
    for line in lines:
        line_sizes.append(len(line.encode('utf-8')))
    
    total_size = sum(line_sizes)
    target_size_per_part = total_size // 3
    
    print(f"[INFO] Total size: {total_size:,} bytes")
    print(f"[INFO] Target size per part: {target_size_per_part:,} bytes")
    
    # Find split points for 3 parts
    print("[INFO] Finding optimal split points...")
    
    # Find first split point (1/3)
    cumulative = 0
    split1 = 0
    best_diff1 = total_size
    
    for i in range(total_lines):
        cumulative += line_sizes[i]
        diff = abs(cumulative - target_size_per_part)
        if diff < best_diff1:
            best_diff1 = diff
            split1 = i + 1
    
    # Find second split point (2/3)
    cumulative = 0
    split2 = split1
    best_diff2 = total_size
    
    for i in range(split1, total_lines):
        cumulative += line_sizes[i]
        diff = abs(cumulative - target_size_per_part)
        if diff < best_diff2:
            best_diff2 = diff
            split2 = i + 1
    
    # Calculate sizes for each part
    part1_size = sum(line_sizes[:split1])
    part2_size = sum(line_sizes[split1:split2])
    part3_size = sum(line_sizes[split2:])
    
    print(f"[INFO] Split points: Part1 ends at line {split1}, Part2 ends at line {split2}")
    print(f"[INFO] Part 1 size: {part1_size:,} bytes ({part1_size*100//total_size}%)")
    print(f"[INFO] Part 2 size: {part2_size:,} bytes ({part2_size*100//total_size}%)")
    print(f"[INFO] Part 3 size: {part3_size:,} bytes ({part3_size*100//total_size}%)")
    
    # Create headers for each part
    header1 = [
        "# SYSTEM3 FOLDER DEEP REPORT - PART 1\n",
        "_Original file: SYSTEM3_FOLDER_DEEP_REPORT.md_\n",
        "_This is part 1 of 3_\n\n",
    ]
    header2 = [
        "# SYSTEM3 FOLDER DEEP REPORT - PART 2\n",
        "_Original file: SYSTEM3_FOLDER_DEEP_REPORT.md_\n",
        "_This is part 2 of 3_\n\n",
    ]
    header3 = [
        "# SYSTEM3 FOLDER DEEP REPORT - PART 3\n",
        "_Original file: SYSTEM3_FOLDER_DEEP_REPORT.md_\n",
        "_This is part 3 of 3_\n\n",
    ]
    
    # Write parts
    print("[INFO] Writing part files...")
    with part1_path.open("w", encoding="utf-8", errors="replace") as f:
        f.writelines(header1 + lines[:split1])
    
    with part2_path.open("w", encoding="utf-8", errors="replace") as f:
        f.writelines(header2 + lines[split1:split2])
    
    with part3_path.open("w", encoding="utf-8", errors="replace") as f:
        f.writelines(header3 + lines[split2:])
    
    # Get final file sizes
    final_part1_size = part1_path.stat().st_size
    final_part2_size = part2_path.stat().st_size
    final_part3_size = part3_path.stat().st_size
    final_total_size = final_part1_size + final_part2_size + final_part3_size
    
    print(f"\n[OK] Report split into 3 parts:")
    print(f"[INFO] Part 1: {final_part1_size:,} bytes ({final_part1_size*100//final_total_size}%)")
    print(f"[INFO] Part 2: {final_part2_size:,} bytes ({final_part2_size*100//final_total_size}%)")
    print(f"[INFO] Part 3: {final_part3_size:,} bytes ({final_part3_size*100//final_total_size}%)")
    
    # Check size ratios
    sizes = [final_part1_size, final_part2_size, final_part3_size]
    max_size = max(sizes)
    min_size = min(sizes)
    ratio = max_size / min_size if min_size > 0 else 0
    
    if ratio > 1.1:
        print(f"[WARN] Size ratio is {ratio:.2f}:1 - parts are not perfectly equal")
        print(f"[INFO] This may be due to very uneven line sizes in the source file")
    else:
        print(f"[OK] Parts are approximately equal (max ratio: {ratio:.2f}:1)")
    
    print(f"[OK] Part files created:")
    print(f"  - {part1_path.name}")
    print(f"  - {part2_path.name}")
    print(f"  - {part3_path.name}")


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = root / "SYSTEM3_FOLDER_DEEP_REPORT.md"

    py_files = []
    other_files = []
    extension_counts = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(root)
            ext = p.suffix.lower()
            extension_counts[ext] = extension_counts.get(ext, 0) + 1

            if ext == ".py":
                py_files.append(p)
            elif ext in TEXT_LIKE_EXT:
                other_files.append(p)

    # Build directory tree text
    tree_text = make_tree(root)

    # Analyze python files
    py_infos = [analyze_python_file(p) for p in sorted(py_files, key=lambda x: str(x).lower())]

    # Analyze other text-like files
    other_infos = [analyze_text_like_file(p) for p in sorted(other_files, key=lambda x: str(x).lower())]

    # Write report
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# SYSTEM3 FOLDER DEEP REPORT\n\n")
        f.write(f"- Generated at: **{timestamp}**\n")
        f.write(f"- Root folder: `{root}`\n\n")

        # Extension summary
        f.write("## 1. File-type summary\n\n")
        f.write("| Extension | Count |\n")
        f.write("|-----------|-------|\n")
        for ext, cnt in sorted(extension_counts.items(), key=lambda x: (x[0] or "")):
            label = ext if ext else "(no extension)"
            f.write(f"| `{label}` | {cnt} |\n")
        f.write("\n")

        # Directory tree
        f.write("## 2. Directory tree\n\n")
        f.write("```text\n")
        f.write(tree_text)
        f.write("\n```\n\n")

        # Python file analysis
        f.write("## 3. Python files (detailed)\n\n")
        for info in py_infos:
            f.write(f"### {info['rel_path']}\n\n")
            f.write(f"- Size: **{info['size_bytes']} bytes**\n")
            f.write(f"- Lines: **{info['num_lines']}**\n")
            f.write(f"- SHA256: `{info['sha256']}`\n")

            if not info["ast_ok"]:
                f.write(f"- AST status: **ERROR** – {info['ast_error']}\n\n")
            else:
                f.write(f"- AST status: OK\n")
                f.write(f"- Imports: `{', '.join(info['imports']) if info['imports'] else '(none)'}`\n")

                if info["classes"]:
                    cls_str = ", ".join([f"{name}@{lineno}" for name, lineno in info["classes"]])
                    f.write(f"- Classes: {cls_str}\n")
                else:
                    f.write(f"- Classes: (none)\n")

                if info["functions"]:
                    fn_str = ", ".join([f"{name}@{lineno}" for name, lineno in info["functions"]])
                    f.write(f"- Functions: {fn_str}\n")
                else:
                    f.write(f"- Functions: (none)\n")

            if info["flags_found"]:
                f.write(f"- Flags / keywords found: `{', '.join(sorted(set(info['flags_found'])))}`\n")
            else:
                f.write(f"- Flags / keywords found: (none)\n")

            f.write("\n#### Preview (first "
                    f"{PY_PREVIEW_LINES} lines)\n\n")
            f.write("```python\n")
            f.write(info["preview"])
            f.write("\n```\n\n")

        # Other text-like files
        f.write("## 4. Other important text files (brief)\n\n")
        for info in other_infos:
            f.write(f"### {info['rel_path']}\n\n")
            f.write(f"- Size: **{info['size_bytes']} bytes**\n\n")
            f.write(f"#### Preview (first {OTHER_PREVIEW_LINES} lines)\n\n")
            f.write("```text\n")
            f.write(info["preview"])
            f.write("\n```\n\n")

        f.write("---\n\n")
        f.write("End of report.\n")

    print(f"Report generated: {report_path}")
    
    # Automatically split the report into 3 equal parts
    print("\n[INFO] Splitting report into 3 equal parts...")
    split_report_into_3_parts(report_path)


if __name__ == "__main__":
    main()
