#!/usr/bin/env python3
"""
Comprehensive Phase Integrity Check for Phases 1-380
Checks for syntax, imports, dependencies, naming conventions
"""

import os
import sys
import py_compile
import ast
import json
from pathlib import Path
from collections import defaultdict

# Add root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

class PhaseIntegrityChecker:
    def __init__(self):
        self.engine_dir = os.path.join(ROOT_DIR, "core", "engine")
        self.results = {
            "total_phases": 0,
            "syntax_errors": [],
            "import_errors": [],
            "naming_errors": [],
            "missing_main": [],
            "duplicate_phases": [],
            "dependency_issues": [],
            "phase_gaps": [],
            "coverage": {}
        }
        
    def check_syntax(self):
        """Check all phase files for Python syntax errors"""
        phase_files = [f for f in os.listdir(self.engine_dir) 
                      if f.startswith('system3_phase') and f.endswith('.py')]
        
        self.results["total_phases"] = len(phase_files)
        
        for phase_file in sorted(phase_files):
            filepath = os.path.join(self.engine_dir, phase_file)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                self.results["syntax_errors"].append({
                    "file": phase_file,
                    "error": str(e)[:200]
                })
    
    def check_imports(self):
        """Check for import statements and broken dependencies"""
        phase_files = [f for f in os.listdir(self.engine_dir) 
                      if f.startswith('system3_phase') and f.endswith('.py')]
        
        for phase_file in sorted(phase_files):
            filepath = os.path.join(self.engine_dir, phase_file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                # Check for imports
                imports = [node for node in ast.walk(tree) 
                          if isinstance(node, (ast.Import, ast.ImportFrom))]
                
                # Try to identify missing modules (basic check)
                for imp in imports:
                    if isinstance(imp, ast.ImportFrom):
                        if imp.module and 'core' in imp.module:
                            # Check if core module exists
                            module_path = imp.module.replace('.', os.sep)
                            expected_path = os.path.join(ROOT_DIR, module_path + '.py')
                            if not os.path.exists(expected_path):
                                self.results["import_errors"].append({
                                    "file": phase_file,
                                    "module": imp.module,
                                    "status": "module_not_found"
                                })
            except SyntaxError as e:
                # Already caught in syntax check
                pass
            except Exception as e:
                self.results["import_errors"].append({
                    "file": phase_file,
                    "error": str(e)[:100]
                })
    
    def check_naming_convention(self):
        """Check for proper naming convention: system3_phase{N}_{description}.py"""
        phase_files = [f for f in os.listdir(self.engine_dir) 
                      if f.startswith('system3_phase')]
        
        import re
        pattern = r'system3_phase(\d+)_(.+)\.py'
        
        for phase_file in phase_files:
            match = re.match(pattern, phase_file)
            if not match:
                self.results["naming_errors"].append({
                    "file": phase_file,
                    "issue": "does_not_match_naming_convention"
                })
    
    def check_main_function(self):
        """Check that each phase has a callable main or run_phaseN function"""
        phase_files = [f for f in os.listdir(self.engine_dir) 
                      if f.startswith('system3_phase') and f.endswith('.py')]
        
        import re
        
        for phase_file in sorted(phase_files):
            filepath = os.path.join(self.engine_dir, phase_file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Check for functions
                functions = [node.name for node in ast.walk(tree) 
                            if isinstance(node, ast.FunctionDef)]
                
                # Expected function names
                match = re.match(r'system3_phase(\d+)_', phase_file)
                phase_num = match.group(1) if match else None
                
                required_funcs = ['main', f'run_phase{phase_num}', 'run']
                has_callable = any(f in functions for f in required_funcs)
                
                if not has_callable:
                    self.results["missing_main"].append({
                        "file": phase_file,
                        "available_functions": functions[:5]
                    })
            except Exception as e:
                self.results["missing_main"].append({
                    "file": phase_file,
                    "error": str(e)[:100]
                })
    
    def check_coverage(self):
        """Check which phases 1-380 are covered"""
        phase_files = [f for f in os.listdir(self.engine_dir) 
                      if f.startswith('system3_phase') and f.endswith('.py')]
        
        import re
        pattern = r'system3_phase(\d+)_'
        
        present_phases = set()
        for phase_file in phase_files:
            match = re.search(pattern, phase_file)
            if match:
                present_phases.add(int(match.group(1)))
        
        # Check for gaps
        for i in range(1, 381):
            if i not in present_phases:
                self.results["phase_gaps"].append(i)
        
        self.results["coverage"] = {
            "phases_with_files": sorted(list(present_phases)),
            "total_present": len(present_phases),
            "total_expected": 380,
            "coverage_percentage": round(len(present_phases) / 380 * 100, 1)
        }
    
    def check_registries(self):
        """Check registry files for completeness"""
        registry_files = [f for f in os.listdir(self.engine_dir)
                         if 'registry' in f and f.endswith('.py')]
        
        registries = {}
        for reg_file in registry_files:
            filepath = os.path.join(self.engine_dir, reg_file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                functions = [node.name for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef)]
                
                registries[reg_file] = {
                    "functions": functions,
                    "count": len(functions)
                }
            except Exception as e:
                registries[reg_file] = {"error": str(e)[:100]}
        
        return registries
    
    def run_all_checks(self):
        """Run all integrity checks"""
        print("[1/5] Checking syntax...")
        self.check_syntax()
        
        print("[2/5] Checking imports...")
        self.check_imports()
        
        print("[3/5] Checking naming conventions...")
        self.check_naming_convention()
        
        print("[4/5] Checking main functions...")
        self.check_main_function()
        
        print("[5/5] Checking coverage and registries...")
        self.check_coverage()
        registries = self.check_registries()
        self.results["registries"] = registries
        
        return self.results
    
    def generate_summary(self):
        """Generate human-readable summary"""
        summary = {
            "total_phases_analyzed": self.results["total_phases"],
            "syntax_errors": len(self.results["syntax_errors"]),
            "import_errors": len(self.results["import_errors"]),
            "naming_errors": len(self.results["naming_errors"]),
            "missing_main_functions": len(self.results["missing_main"]),
            "phase_gaps": len(self.results["phase_gaps"]),
            "coverage": self.results["coverage"]
        }
        return summary

if __name__ == "__main__":
    checker = PhaseIntegrityChecker()
    print("Running Phase Integrity Check...")
    results = checker.run_all_checks()
    summary = checker.generate_summary()
    
    print("\n" + "="*60)
    print("INTEGRITY CHECK SUMMARY")
    print("="*60)
    print(f"Total phases analyzed: {summary['total_phases_analyzed']}")
    print(f"Syntax errors: {summary['syntax_errors']}")
    print(f"Import errors: {summary['import_errors']}")
    print(f"Naming errors: {summary['naming_errors']}")
    print(f"Missing main functions: {summary['missing_main_functions']}")
    print(f"Phase gaps (1-380): {summary['phase_gaps']}")
    print(f"\nCoverage: {summary['coverage']['coverage_percentage']}%")
    print(f"Phases with files: {summary['coverage']['total_present']}/380")
    
    # Save results to JSON
    results_file = os.path.join(ROOT_DIR, "phase_integrity_check_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
