import os
import re
import json

TABS = [
    {"id": "decision-intel", "name": "Decision Intel", "file": "components/workspaces/DecisionIntelligence.tsx"},
    {"id": "truth", "name": "Truth Control", "file": "components/SystemTruthControl.tsx"},
    {"id": "genesis", "name": "Genesis Brain", "file": "components/GenesisTab.tsx"},
    {"id": "e2e-proof", "name": "E2E Proof", "file": "components/EndToEndProof.tsx"},
    {"id": "overview", "name": "Overview", "file": "components/Overview.tsx"},
    {"id": "sim-live", "name": "Sim Live", "file": "components/LiveSimulation.tsx"},
    {"id": "options-intel", "name": "Options Intel", "file": "components/workspaces/OptionsIntelligence.tsx"},
    {"id": "chain", "name": "Option Chain", "file": "components/OptionChain.tsx"},
    {"id": "signals", "name": "Signals", "file": "components/Signals.tsx"},
    {"id": "trade", "name": "Trade", "file": "components/TradeTab.tsx"},
    {"id": "paper", "name": "Paper Trades", "file": "components/PaperTrading.tsx"},
    {"id": "positions", "name": "Positions", "file": "components/Positions.tsx"},
    {"id": "risk-scenarios", "name": "Risk & Scenarios", "file": "components/workspaces/RiskAndScenarios.tsx"},
    {"id": "multibagger", "name": "Multibagger", "file": "components/workspaces/MultibaggerResearch.tsx"},
    {"id": "prediction-audit", "name": "Prediction Audit", "file": "components/workspaces/PredictionAudit.tsx"},
    {"id": "performance", "name": "Performance", "file": "components/PerformanceTab.tsx"},
    {"id": "ml", "name": "ML Model", "file": "components/MLPerformance.tsx"},
    {"id": "data-integrity", "name": "Data Integrity", "file": "components/workspaces/DataIntegrity.tsx"},
    {"id": "broker", "name": "Broker", "file": "components/BrokerProofPanel.tsx"},
    {"id": "alerts", "name": "Alerts", "file": "components/AlertsTab.tsx"},
    {"id": "system", "name": "System", "file": "components/SystemTab.tsx"},
    {"id": "system-readiness", "name": "System Readiness", "file": "components/SystemReadiness.tsx"},
    {"id": "gates", "name": "Live Gate", "file": "components/LiveTradingGate.tsx"},
    {"id": "layout-topbar", "name": "TopBar Layout", "file": "components/TopBar.tsx"},
    {"id": "layout-truthstrip", "name": "TruthStrip Layout", "file": "components/TruthStrip.tsx"},
    {"id": "layout-lifecycle", "name": "Pending Lifecycle Banner", "file": "components/PendingLifecycleBanner.tsx"},
    {"id": "layout-autobanner", "name": "Autonomous Loop Banner", "file": "components/AutonomousLoopBanner.tsx"},
]

def audit_tabs():
    base_dir = os.path.join("dashboard", "frontend", "src")
    report = []
    
    # Patterns that indicate honest paper/blocked/locked states
    honest_markers = [
        re.compile(r'PAPER', re.IGNORECASE),
        re.compile(r'BLOCKED', re.IGNORECASE),
        re.compile(r'LOCKED', re.IGNORECASE),
        re.compile(r'PENDING', re.IGNORECASE),
        re.compile(r'STANDBY', re.IGNORECASE),
        re.compile(r'INHIBITED', re.IGNORECASE),
    ]
    
    # Forbidden patterns
    fake_patterns = [
        re.compile(r'value=[\'"]ACTIVE[\'"]'),
        re.compile(r'Model Ensemble[\'"]?\s*value=[\'"]ACTIVE[\'"]'),
        re.compile(r'(?:\?\?|\|\|)\s*88(?:\.0)?\b'),
        re.compile(r'(?:\?\?|\|\|)\s*74(?:\.0)?\b'),
        re.compile(r'(?:\?\?|\|\|)\s*1\.85\b'),
        re.compile(r'ready_for_live\s*:\s*true\b'),
    ]
    
    for tab in TABS:
        full_path = os.path.join(base_dir, tab["file"])
        if not os.path.exists(full_path):
            report.append({
                "tab": tab["name"],
                "file": tab["file"],
                "status": "MISSING_FILE",
                "honest_markers": [],
                "violations": ["File not found"],
                "pass": False
            })
            continue
            
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        found_markers = []
        for m in honest_markers:
            matches = m.findall(content)
            if matches:
                found_markers.append(matches[0].upper())
                
        violations = []
        for pat in fake_patterns:
            matches = pat.findall(content)
            if matches:
                violations.extend(matches)
                
        # Check for trade execution claims
        if re.search(r'order_placement_allowed\s*[:=]\s*true\b', content, re.IGNORECASE):
            violations.append("order_placement_allowed true")
            
        is_pass = len(violations) == 0 and len(found_markers) > 0
        
        report.append({
            "tab": tab["name"],
            "file": tab["file"],
            "status": "PASS" if is_pass else "VIOLATION",
            "honest_markers": list(set(found_markers)),
            "violations": violations,
            "pass": is_pass
        })
        
    return report

if __name__ == "__main__":
    results = audit_tabs()
    out_dir = r"C:\Temp\Genesis_Forensic"
    os.makedirs(out_dir, exist_ok=True)
    
    json_path = os.path.join(out_dir, "05_27_TABS_AUDIT.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    txt_path = os.path.join(out_dir, "05_27_TABS_AUDIT.txt")
    lines = []
    lines.append("=== 27 TABS FORENSIC INTEGRITY AUDIT ===")
    lines.append(f"Total Tabs/Surfaces Audited: {len(results)}")
    lines.append("=" * 60)
    lines.append("")
    
    all_pass = True
    for r in results:
        status_symbol = "[PASS]" if r["pass"] else "[FAIL]"
        if not r["pass"]:
            all_pass = False
        markers_str = ", ".join(r["honest_markers"])
        lines.append(f"[{status_symbol}] {r['tab']:<25} ({r['file']})")
        lines.append(f"       Markers: {markers_str}")
        if r["violations"]:
            lines.append(f"       VIOLATIONS: {r['violations']}")
        lines.append("")
        
    lines.append("=" * 60)
    lines.append(f"FINAL AUDIT RESULT: {'ALL 27 TABS PASS - BLOCKED / PAPER / LOCKED / PENDING HONEST' if all_pass else 'FAILURES DETECTED'}")
    lines.append("=" * 60)
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"Audit completed: {'PASS' if all_pass else 'FAIL'}")
    print(f"JSON: {json_path}")
    print(f"TXT:  {txt_path}")
    print("\n".join(lines[:30]))
