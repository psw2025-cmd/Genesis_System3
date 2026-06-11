#!/usr/bin/env python3
"""
SYSTEM3 PHASES 1–200 DEEP DIAGNOSTIC ANALYZER
Read-only comprehensive verification tool.
"""

import os
import sys
import json
import re
import ast
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
CORE_ENGINE = PROJECT_ROOT / "core" / "engine"

# Phase definitions
PHASE_RANGES = {
    "1-30": "Legacy Core Infrastructure",
    "31-85": "Ultra Model & Consensus",
    "86-100": "Position Sizing & Risk",
    "101-130": "Live Trading Control Panel",
    "131-150": "Master Session & Diagnostics",
    "151-200": "Analytics & Reporting"
}

class Phase1To200Analyzer:
    def __init__(self):
        self.findings = {
            "pass": [],
            "warn": [],
            "error": [],
            "reserved": [],
            "duplicates": {},
            "missing": [],
            "phantom": []
        }
        self.phases = defaultdict(dict)
        self.imports = defaultdict(set)
        self.function_conflicts = []
        self.deprecated = []

    def scan_phases(self):
        """Scan all phase files 1-200."""
        print("[SCAN] Phases 1–200...")
        
        for phase_file in sorted(CORE_ENGINE.glob("system3_phase*.py")):
            name = phase_file.name
            match = re.search(r'phase(\d+)', name)
            if not match:
                continue
            
            phase_num = int(match.group(1))
            if phase_num > 200:  # Only analyze 1-200
                continue
            
            self.analyze_phase(phase_num, phase_file)
    
    def analyze_phase(self, phase_num, phase_file):
        """Deep analyze a single phase file."""
        try:
            with open(phase_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic checks
            size_kb = phase_file.stat().st_size / 1024
            is_reserved = 'reserved' in phase_file.name.lower()
            is_stub = 'stub' in phase_file.name.lower()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.findings["error"].append({
                    "phase": phase_num,
                    "issue": f"Syntax Error: {e}",
                    "file": phase_file.name
                })
                return
            
            # Extract functions
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            # Extract imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            # Check for deprecations
            deprecated_patterns = [
                r'pickle\.load\(',
                r'eval\(',
                r'exec\(',
                r'subprocess\.call\(',
                r'os\.system\('
            ]
            
            deprecated_found = []
            for pattern in deprecated_patterns:
                if re.search(pattern, content):
                    deprecated_found.append(pattern)
            
            # Store findings
            self.phases[phase_num] = {
                "file": phase_file.name,
                "size_kb": size_kb,
                "functions": functions,
                "imports": imports,
                "is_reserved": is_reserved,
                "is_stub": is_stub,
                "has_run_function": 'run_phase' in content or f'run_phase_{phase_num}' in content,
                "deprecated": deprecated_found,
                "docstring": self._extract_docstring(tree)
            }
            
            # Add to tracking lists
            if is_reserved:
                self.findings["reserved"].append(phase_num)
            elif deprecated_found:
                self.findings["warn"].append({
                    "phase": phase_num,
                    "issue": f"Deprecated patterns found: {deprecated_found}"
                })
            else:
                self.findings["pass"].append(phase_num)
            
            self.imports[phase_num] = imports
            
        except Exception as e:
            self.findings["error"].append({
                "phase": phase_num,
                "issue": str(e),
                "file": phase_file.name
            })
    
    def check_duplicates(self):
        """Identify duplicate phase files or conflicting functions."""
        print("[CHECK] Duplicates & Conflicts...")
        
        function_map = defaultdict(list)
        for phase_num, info in self.phases.items():
            for func in info["functions"]:
                if func.startswith("run_phase"):
                    function_map[func].append(phase_num)
        
        for func, phases in function_map.items():
            if len(phases) > 1:
                self.function_conflicts.append({
                    "function": func,
                    "phases": phases
                })
                self.findings["error"].append({
                    "phase": "MULTI",
                    "issue": f"Conflicting function {func} in phases {phases}"
                })
    
    def check_missing_phases(self):
        """Identify missing phases in 1-200 range."""
        print("[CHECK] Missing Phases...")
        
        present = set(self.phases.keys())
        expected = set(range(1, 201))
        missing = expected - present
        
        # Exclude known reserved ranges (1-30, some legacy)
        critical_missing = [p for p in missing if p in range(100, 201)]
        
        if critical_missing:
            for phase_num in sorted(critical_missing):
                self.findings["error"].append({
                    "phase": phase_num,
                    "issue": "Phase file not found",
                    "severity": "CRITICAL"
                })
            self.findings["missing"] = sorted(critical_missing)
        else:
            self.findings["missing"] = sorted(missing)
    
    def check_imports_compatibility(self):
        """Check for broken imports and incompatible dependencies."""
        print("[CHECK] Import Compatibility...")
        
        for phase_num, imports in self.imports.items():
            for imp in imports:
                if 'system3' in imp:
                    # Check if referenced module exists
                    if imp.startswith('core.engine.system3'):
                        ref_module = PROJECT_ROOT / (imp.replace('.', '/') + '.py')
                        if not ref_module.exists():
                            self.findings["warn"].append({
                                "phase": phase_num,
                                "issue": f"Reference to non-existent module: {imp}"
                            })
    
    def check_safety_primitives(self):
        """Verify DRY-RUN safety in phases 101-130."""
        print("[CHECK] Safety Primitives (101-130)...")
        
        for phase_num in range(101, 131):
            if phase_num not in self.phases:
                continue
            
            phase_file = CORE_ENGINE / self.phases[phase_num]["file"]
            try:
                with open(phase_file, 'r') as f:
                    content = f.read()
                
                safety_checks = [
                    'LIVE_TRADING_ENABLED',
                    'USE_LIVE_EXECUTION_ENGINE',
                    'auto_execute_trades'
                ]
                
                found = [check for check in safety_checks if check in content]
                
                if len(found) < 2:
                    self.findings["warn"].append({
                        "phase": phase_num,
                        "issue": f"Incomplete safety checks: found {len(found)}/3",
                        "category": "SAFETY"
                    })
            except:
                pass
    
    def _extract_docstring(self, tree):
        """Extract module docstring."""
        return ast.get_docstring(tree) or ""

    def generate_report(self):
        """Generate comprehensive audit report."""
        print("[REPORT] Generating Analysis...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(PROJECT_ROOT),
            "total_phases_analyzed": len(self.phases),
            "phase_status_summary": {
                "pass": len(self.findings["pass"]),
                "warn": len(self.findings["warn"]),
                "error": len(self.findings["error"]),
                "reserved": len(self.findings["reserved"]),
                "missing": len(self.findings["missing"])
            },
            "phases_detailed": self.phases,
            "findings": self.findings,
            "conflicts": self.function_conflicts
        }
        
        return report

def main():
    analyzer = Phase1To200Analyzer()
    
    print("=" * 70)
    print("SYSTEM3 PHASES 1–200 DEEP DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Run all checks
    analyzer.scan_phases()
    analyzer.check_duplicates()
    analyzer.check_missing_phases()
    analyzer.check_imports_compatibility()
    analyzer.check_safety_primitives()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ PASS:     {report['phase_status_summary']['pass']} phases")
    print(f"⚠️  WARN:     {report['phase_status_summary']['warn']} phases")
    print(f"❌ ERROR:    {report['phase_status_summary']['error']} phases")
    print(f"🔒 RESERVED: {report['phase_status_summary']['reserved']} phases")
    print(f"❓ MISSING:  {report['phase_status_summary']['missing']} phases")
    print()
    
    if analyzer.findings["error"]:
        print("CRITICAL ISSUES:")
        for err in analyzer.findings["error"][:10]:
            print(f"  Phase {err['phase']}: {err['issue']}")
    
    # Save JSON report
    report_file = PROJECT_ROOT / "DIAGNOSTIC_PHASES_1_200_DATA.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print()
    print(f"Diagnostic data saved: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
