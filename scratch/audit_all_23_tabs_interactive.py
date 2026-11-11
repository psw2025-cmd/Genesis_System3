import os, re, json

tabs = [
    ("decision-intel", "src/components/workspaces/DecisionIntelligence.tsx"),
    ("truth", "src/components/SystemTruthControl.tsx"),
    ("genesis", "src/components/GenesisTab.tsx"),
    ("e2e-proof", "src/components/EndToEndProof.tsx"),
    ("overview", "src/components/Overview.tsx"),
    ("sim-live", "src/components/LiveSimulation.tsx"),
    ("options-intel", "src/components/workspaces/OptionsIntelligence.tsx"),
    ("chain", "src/components/OptionChain.tsx"),
    ("signals", "src/components/Signals.tsx"),
    ("trade", "src/components/TradeTab.tsx"),
    ("paper", "src/components/PaperTrading.tsx"),
    ("positions", "src/components/Positions.tsx"),
    ("risk-scenarios", "src/components/workspaces/RiskAndScenarios.tsx"),
    ("multibagger", "src/components/workspaces/MultibaggerResearch.tsx"),
    ("prediction-audit", "src/components/workspaces/PredictionAudit.tsx"),
    ("performance", "src/components/PerformanceTab.tsx"),
    ("ml", "src/components/MLPerformance.tsx"),
    ("data-integrity", "src/components/workspaces/DataIntegrity.tsx"),
    ("broker", "src/components/BrokerProofPanel.tsx"),
    ("alerts", "src/components/AlertsTab.tsx"),
    ("system", "src/components/SystemTab.tsx"),
    ("gates", "src/components/LiveTradingGate.tsx"),
    ("system-readiness", "src/components/SystemReadiness.tsx"),
]

frontend_dir = os.path.join("dashboard", "frontend")
report = []

for tab_id, rel_path in tabs:
    full_path = os.path.join(frontend_dir, rel_path)
    if not os.path.exists(full_path):
        report.append({"tab": tab_id, "file": rel_path, "status": "FILE_NOT_FOUND"})
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        code = f.read()

    clicks = len(re.findall(r'onClick\s*=', code))
    has_chart = bool(re.search(r'(ResponsiveContainer|AreaChart|LineChart|BarChart|ComposedChart|PieChart|svg|canvas|<path)', code, re.IGNORECASE))
    has_filter = bool(re.search(r'(filter|selected|search|dropdown|<select|activeTab|category)', code, re.IGNORECASE))
    has_sort = bool(re.search(r'(sort|sortBy|sortOrder|sortDirection|order)', code, re.IGNORECASE))
    has_responsive = bool(re.search(r'(hidden\s+md:|flex\s+flex-col|grid-cols-|overflow-x-auto|w-full)', code))
    
    # Check if there are any raw PENDING strings that would render to users
    pending_matches = re.findall(r'[\'"`][^\'"`]*PENDING[^\'"`]*[\'"`]', code)

    report.append({
        "tab": tab_id,
        "component": os.path.basename(rel_path),
        "lines": len(code.splitlines()),
        "clicks_count": clicks,
        "has_chart_or_visual": has_chart,
        "has_filter_or_search": has_filter,
        "has_sort": has_sort,
        "has_responsive_classes": has_responsive,
        "pending_occurrences": len(pending_matches),
    })

print(f"{'TAB':<18} | {'COMP':<26} | {'LINES':<5} | {'CLICKS':<6} | {'CHART':<5} | {'FILTER':<6} | {'SORT':<5} | {'RESP':<5}")
print("-" * 90)
for r in report:
    print(f"{r['tab']:<18} | {r['component']:<26} | {r['lines']:<5} | {r['clicks_count']:<6} | {str(r['has_chart_or_visual']):<5} | {str(r['has_filter_or_search']):<6} | {str(r['has_sort']):<5} | {str(r['has_responsive_classes']):<5}")
