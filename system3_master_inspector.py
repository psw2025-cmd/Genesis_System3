"""
System3 Master Inspector - READ-ONLY Diagnostic Tool
====================================================

This script performs comprehensive READ-ONLY inspection of System3 project.
NO modifications are made to any existing files.

Generates 9 diagnostic reports:
1. SYSTEM3_DEEP_PROJECT_TREE.md
2. SYSTEM3_CODE_INDEX.md
3. SYSTEM3_SAFETY_AUDIT.md
4. SYSTEM3_SIGNAL_PIPELINE_AUDIT.md
5. SYSTEM3_PHASE_REFERENCES_AUDIT.md
6. SYSTEM3_MODEL_AUDIT.md
7. SYSTEM3_RUNTIME_AUDIT.md
8. SYSTEM3_DEPENDENCY_AUDIT.md
9. SYSTEM3_MASTER_INSPECTION_REPORT.md
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

ROOT = Path(r"C:\Genesis_System3")
SKIP_FOLDERS = {"venv", "logs", "storage", "__pycache__", ".git", ".mypy_cache", ".tmp.drivedownload", ".tmp.driveupload", "node_modules"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".log", ".csv", ".json", ".pkl", ".joblib", ".h5", ".hdf5"}

def safe_read(file_path, max_lines=10000):
    """Safely read file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line)
            return lines
    except Exception as e:
        return [f"ERROR: Could not read file: {e}"]

def get_file_header(file_path, lines=10):
    """Extract first N lines as header summary."""
    content = safe_read(file_path, max_lines=lines)
    return ''.join(content[:lines])

def count_lines(file_path):
    """Count lines in file."""
    try:
        content = safe_read(file_path)
        return len(content)
    except:
        return 0

def scan_tree():
    """Generate deep project tree."""
    print("📂 Scanning project tree...")
    tree = []
    tree.append(f"# System3 Deep Project Tree\n")
    tree.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    tree.append(f"**Root:** {ROOT}\n\n")
    tree.append("```\n")
    
    for root, dirs, files in os.walk(ROOT):
        # Skip excluded folders
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        
        level = root.replace(str(ROOT), '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root) or ROOT.name
        tree.append(f"{indent}{folder_name}/\n")
        
        sub_indent = '  ' * (level + 1)
        for file in sorted(files):
            tree.append(f"{sub_indent}{file}\n")
    
    tree.append("```\n")
    return ''.join(tree)

def scan_code_index():
    """Index all Python files."""
    print("🔍 Indexing Python files...")
    index = []
    index.append(f"# System3 Code Index\n")
    index.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    py_files = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                line_count = count_lines(file_path)
                header = get_file_header(file_path, lines=5)
                py_files.append((rel_path, line_count, header))
    
    index.append(f"## Total Python Files: {len(py_files)}\n\n")
    
    for rel_path, line_count, header in sorted(py_files):
        index.append(f"### {rel_path}\n")
        index.append(f"- **Lines:** {line_count}\n")
        index.append(f"- **Header:**\n```python\n{header}```\n\n")
    
    return ''.join(index)

def scan_safety():
    """Audit for live trading risks."""
    print("🛡️ Running safety audit...")
    audit = []
    audit.append(f"# System3 Safety Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    danger_patterns = [
        (r'LIVE_TRADING_ENABLED\s*=\s*True', 'CRITICAL: LIVE_TRADING_ENABLED=True'),
        (r'AUTO_EXECUTE_TRADES\s*=\s*True', 'CRITICAL: AUTO_EXECUTE_TRADES=True'),
        (r'USE_LIVE_EXECUTION_ENGINE\s*=\s*True', 'CRITICAL: USE_LIVE_EXECUTION_ENGINE=True'),
        (r'place_order\(', 'WARNING: place_order() call detected'),
        (r'execute_trade\(', 'WARNING: execute_trade() call detected'),
        (r'live\s*=\s*True', 'WARNING: live=True assignment'),
    ]
    
    findings = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                content = safe_read(file_path)
                
                for line_num, line in enumerate(content, 1):
                    for pattern, msg in danger_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings[msg].append(f"{rel_path}:{line_num} - {line.strip()}")
    
    if findings:
        audit.append("## ⚠️ SAFETY FINDINGS\n\n")
        for msg, occurrences in sorted(findings.items()):
            audit.append(f"### {msg}\n")
            audit.append(f"**Count:** {len(occurrences)}\n\n")
            for occ in occurrences[:20]:  # Limit to first 20
                audit.append(f"- {occ}\n")
            if len(occurrences) > 20:
                audit.append(f"- ... and {len(occurrences) - 20} more\n")
            audit.append("\n")
    else:
        audit.append("## ✅ NO CRITICAL SAFETY ISSUES DETECTED\n\n")
    
    return ''.join(audit)

def scan_signal_pipeline():
    """Audit signal pipeline references."""
    print("📊 Auditing signal pipeline...")
    audit = []
    audit.append(f"# System3 Signal Pipeline Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    signal_patterns = [
        (r'angel_index_ai_signals', 'angel_index_ai_signals'),
        (r'curated.*signal', 'curated signals'),
        (r'with_forward.*signal', 'with_forward signals'),
        (r'forward_return', 'forward returns'),
        (r'signal_engine', 'signal engine'),
        (r'generate_signal', 'signal generation'),
        (r'BUY.*SELL.*HOLD', 'signal decisions'),
    ]
    
    findings = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                content = safe_read(file_path)
                
                for line_num, line in enumerate(content, 1):
                    for pattern, label in signal_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings[label].append(f"{rel_path}:{line_num}")
    
    audit.append("## Signal Pipeline Components\n\n")
    for label, occurrences in sorted(findings.items()):
        audit.append(f"### {label}\n")
        audit.append(f"**References:** {len(occurrences)}\n\n")
        for occ in occurrences[:10]:
            audit.append(f"- {occ}\n")
        if len(occurrences) > 10:
            audit.append(f"- ... and {len(occurrences) - 10} more\n")
        audit.append("\n")
    
    return ''.join(audit)

def scan_phases():
    """Audit phase references."""
    print("🔢 Auditing phase references...")
    audit = []
    audit.append(f"# System3 Phase References Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    phase_refs = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                content = safe_read(file_path)
                
                for line_num, line in enumerate(content, 1):
                    # Match "Phase 123", "PHASE_123", "phase123", etc.
                    matches = re.findall(r'(?:phase|PHASE)[\s_]?(\d{1,3})', line, re.IGNORECASE)
                    for phase_num in matches:
                        phase_refs[int(phase_num)].append(f"{rel_path}:{line_num}")
    
    audit.append(f"## Detected Phases: {len(phase_refs)}\n\n")
    
    # Find gaps
    if phase_refs:
        min_phase = min(phase_refs.keys())
        max_phase = max(phase_refs.keys())
        all_phases = set(range(min_phase, max_phase + 1))
        found_phases = set(phase_refs.keys())
        missing = sorted(all_phases - found_phases)
        
        audit.append(f"**Range:** Phase {min_phase} - Phase {max_phase}\n")
        audit.append(f"**Found:** {len(found_phases)} phases\n")
        audit.append(f"**Missing:** {len(missing)} phases\n\n")
        
        if missing:
            audit.append(f"### ⚠️ Missing Phases\n")
            audit.append(f"{', '.join(map(str, missing[:50]))}\n")
            if len(missing) > 50:
                audit.append(f"... and {len(missing) - 50} more\n")
            audit.append("\n")
    
    audit.append("## Phase References by Number\n\n")
    for phase_num in sorted(phase_refs.keys())[:50]:  # First 50 phases
        refs = phase_refs[phase_num]
        audit.append(f"### Phase {phase_num}\n")
        audit.append(f"**References:** {len(refs)}\n")
        for ref in refs[:5]:
            audit.append(f"- {ref}\n")
        if len(refs) > 5:
            audit.append(f"- ... and {len(refs) - 5} more\n")
        audit.append("\n")
    
    return ''.join(audit)

def scan_models():
    """Audit ML/DL model references."""
    print("🤖 Auditing models...")
    audit = []
    audit.append(f"# System3 Model Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    model_patterns = [
        (r'load_model|joblib\.load|pickle\.load', 'Model Loading'),
        (r'fit\(|train\(', 'Training'),
        (r'predict\(|predict_proba\(', 'Prediction'),
        (r'feature.*extract|get_features', 'Feature Extraction'),
        (r'drift.*detect|model.*drift', 'Drift Detection'),
        (r'RandomForest|XGBoost|LightGBM|sklearn', 'ML Libraries'),
        (r'tensorflow|keras|torch|pytorch', 'DL Libraries'),
    ]
    
    findings = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                content = safe_read(file_path)
                
                for line_num, line in enumerate(content, 1):
                    for pattern, label in model_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings[label].append(f"{rel_path}:{line_num}")
    
    audit.append("## Model Components\n\n")
    for label, occurrences in sorted(findings.items()):
        audit.append(f"### {label}\n")
        audit.append(f"**References:** {len(occurrences)}\n\n")
        for occ in occurrences[:10]:
            audit.append(f"- {occ}\n")
        if len(occurrences) > 10:
            audit.append(f"- ... and {len(occurrences) - 10} more\n")
        audit.append("\n")
    
    return ''.join(audit)

def scan_runtime():
    """Audit runtime components."""
    print("⚙️ Auditing runtime...")
    audit = []
    audit.append(f"# System3 Runtime Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    runtime_patterns = [
        (r'watchdog', 'Watchdog'),
        (r'autorun|auto_run', 'Autorun'),
        (r'schedule|cron|trigger', 'Scheduling'),
        (r'heartbeat', 'Heartbeat'),
        (r'logging|logger', 'Logging'),
        (r'error.*handle|exception', 'Error Handling'),
        (r'market.*hours|trading.*hours', 'Market Hours'),
    ]
    
    findings = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith(('.py', '.bat', '.ps1')):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(ROOT)
                content = safe_read(file_path)
                
                for line_num, line in enumerate(content, 1):
                    for pattern, label in runtime_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings[label].append(f"{rel_path}:{line_num}")
    
    audit.append("## Runtime Components\n\n")
    for label, occurrences in sorted(findings.items()):
        audit.append(f"### {label}\n")
        audit.append(f"**References:** {len(occurrences)}\n\n")
        for occ in occurrences[:10]:
            audit.append(f"- {occ}\n")
        if len(occurrences) > 10:
            audit.append(f"- ... and {len(occurrences) - 10} more\n")
        audit.append("\n")
    
    return ''.join(audit)

def scan_dependencies():
    """Audit dependencies."""
    print("📦 Auditing dependencies...")
    audit = []
    audit.append(f"# System3 Dependency Audit\n")
    audit.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Read requirements.txt
    req_file = ROOT / "requirements.txt"
    if req_file.exists():
        audit.append("## requirements.txt\n\n")
        audit.append("```\n")
        content = safe_read(req_file)
        audit.append(''.join(content))
        audit.append("```\n\n")
    
    # Scan imports
    imports = defaultdict(int)
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                content = safe_read(file_path)
                
                for line in content:
                    # Match "import X" or "from X import Y"
                    match = re.match(r'^\s*(?:from\s+(\S+)|import\s+(\S+))', line)
                    if match:
                        module = match.group(1) or match.group(2)
                        base_module = module.split('.')[0]
                        imports[base_module] += 1
    
    audit.append("## Top 30 Imported Modules\n\n")
    sorted_imports = sorted(imports.items(), key=lambda x: x[1], reverse=True)
    for module, count in sorted_imports[:30]:
        audit.append(f"- **{module}**: {count} references\n")
    
    return ''.join(audit)

def generate_master_report():
    """Consolidate all findings."""
    print("📝 Generating master report...")
    report = []
    report.append(f"# System3 Master Inspection Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.append(f"## Executive Summary\n\n")
    report.append(f"**Project Root:** {ROOT}\n\n")
    
    # Count key metrics
    py_files = list(ROOT.rglob("*.py"))
    py_files = [f for f in py_files if not any(skip in f.parts for skip in SKIP_FOLDERS)]
    
    report.append(f"### Project Metrics\n")
    report.append(f"- **Python Files:** {len(py_files)}\n")
    report.append(f"- **Total Lines:** {sum(count_lines(f) for f in py_files)}\n\n")
    
    report.append("## Generated Reports\n\n")
    reports = [
        "SYSTEM3_DEEP_PROJECT_TREE.md",
        "SYSTEM3_CODE_INDEX.md",
        "SYSTEM3_SAFETY_AUDIT.md",
        "SYSTEM3_SIGNAL_PIPELINE_AUDIT.md",
        "SYSTEM3_PHASE_REFERENCES_AUDIT.md",
        "SYSTEM3_MODEL_AUDIT.md",
        "SYSTEM3_RUNTIME_AUDIT.md",
        "SYSTEM3_DEPENDENCY_AUDIT.md",
    ]
    
    for r in reports:
        report.append(f"- ✅ {r}\n")
    
    report.append("\n## Recommended Actions\n\n")
    report.append("1. Review SYSTEM3_SAFETY_AUDIT.md for live trading risks\n")
    report.append("2. Check SYSTEM3_PHASE_REFERENCES_AUDIT.md for missing phases\n")
    report.append("3. Validate SYSTEM3_SIGNAL_PIPELINE_AUDIT.md for signal flow\n")
    report.append("4. Inspect SYSTEM3_DEPENDENCY_AUDIT.md for outdated packages\n\n")
    
    report.append("## ⚠️ IMPORTANT\n\n")
    report.append("This inspection was READ-ONLY. No files were modified.\n")
    report.append("Review all reports before making any changes.\n\n")
    
    return ''.join(report)

def main():
    """Main inspection routine."""
    print("=" * 60)
    print("System3 Master Inspector")
    print("=" * 60)
    print(f"Root: {ROOT}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    if not ROOT.exists():
        print(f"❌ ERROR: Project root not found: {ROOT}")
        sys.exit(1)
    
    # Generate all reports
    reports = {
        "SYSTEM3_DEEP_PROJECT_TREE.md": scan_tree,
        "SYSTEM3_CODE_INDEX.md": scan_code_index,
        "SYSTEM3_SAFETY_AUDIT.md": scan_safety,
        "SYSTEM3_SIGNAL_PIPELINE_AUDIT.md": scan_signal_pipeline,
        "SYSTEM3_PHASE_REFERENCES_AUDIT.md": scan_phases,
        "SYSTEM3_MODEL_AUDIT.md": scan_models,
        "SYSTEM3_RUNTIME_AUDIT.md": scan_runtime,
        "SYSTEM3_DEPENDENCY_AUDIT.md": scan_dependencies,
    }
    
    for report_name, scan_func in reports.items():
        print(f"\n{'='*60}")
        content = scan_func()
        output_path = ROOT / report_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Generated: {report_name}")
    
    # Generate master report
    print(f"\n{'='*60}")
    master_content = generate_master_report()
    master_path = ROOT / "SYSTEM3_MASTER_INSPECTION_REPORT.md"
    with open(master_path, 'w', encoding='utf-8') as f:
        f.write(master_content)
    print(f"✅ Generated: SYSTEM3_MASTER_INSPECTION_REPORT.md")
    
    print("\n" + "=" * 60)
    print("✅ INSPECTION COMPLETE")
    print("=" * 60)
    print("\nAll reports generated successfully!")
    print("Review SYSTEM3_MASTER_INSPECTION_REPORT.md for summary.")
    print()

if __name__ == "__main__":
    main()
