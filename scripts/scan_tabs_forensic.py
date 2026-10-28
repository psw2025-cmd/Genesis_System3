import os
import re
import json

def scan_frontend():
    src_dir = os.path.join("dashboard", "frontend", "src")
    findings = []
    
    # Patterns to look for
    fake_patterns = [
        ("fake_profit_factor_1.85", re.compile(r'(?:\?\?|\|\||\b)\s*1\.85\b')),
        ("fake_pct_88", re.compile(r'(?:\?\?|\|\||\b)\s*88(?:\.0)?%?\b')),
        ("fake_pct_74", re.compile(r'(?:\?\?|\|\||\b)\s*74(?:\.0)?%?\b')),
        ("fake_active_literal", re.compile(r'value=[\'"]ACTIVE[\'"]|status=[\'"]ACTIVE[\'"]')),
    ]
    
    for root, _, files in os.walk(src_dir):
        for f in files:
            if not f.endswith((".ts", ".tsx")):
                continue
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                for idx, line in enumerate(fp, 1):
                    # Exclude comments or valid variable names / css
                    for name, pat in fake_patterns:
                        if pat.search(line):
                            findings.append({
                                "file": p.replace("\\", "/"),
                                "line": idx,
                                "type": name,
                                "content": line.strip()
                            })
                            
    return findings

if __name__ == "__main__":
    results = scan_frontend()
    print(f"Total findings: {len(results)}")
    for r in results:
        print(f"{r['file']}:{r['line']} [{r['type']}] {r['content']}")
