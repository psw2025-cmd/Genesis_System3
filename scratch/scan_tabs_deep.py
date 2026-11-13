import os
import re
import json

components_dir = "dashboard/frontend/src/components"
tab_components = {
    "decision-intel": "workspaces/DecisionIntelligence.tsx",
    "options-intel": "workspaces/OptionsIntelligence.tsx",
    "multibagger": "workspaces/MultibaggerResearch.tsx",
    "risk-scenarios": "workspaces/RiskAndScenarios.tsx",
    "data-integrity": "workspaces/DataIntegrity.tsx",
    "prediction-audit": "workspaces/PredictionAudit.tsx",
    "truth": "SystemTruthControl.tsx",
    "overview": "Overview.tsx",
    "trade": "TradeTab.tsx",
    "positions": "Positions.tsx",
    "chain": "OptionChain.tsx",
    "signals": "Signals.tsx",
    "paper": "PaperTrading.tsx",
    "performance": "PerformanceTab.tsx",
    "ml": "MLPerformance.tsx",
    "system-readiness": "SystemReadiness.tsx",
    "genesis": "GenesisTab.tsx",
    "e2e-proof": "EndToEndProof.tsx",
    "broker": "BrokerProofPanel.tsx",
    "alerts": "AlertsTab.tsx",
    "system": "SystemTab.tsx",
    "gates": "LiveTradingGate.tsx",
    "sim-live": "LiveSimulation.tsx",
}

tab_analysis = {}

for tab_id, comp_rel in tab_components.items():
    comp_path = os.path.join(components_dir, comp_rel)
    if not os.path.exists(comp_path):
        print(f"MISSING: {comp_path}")
        continue
    with open(comp_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Find endpoints
    endpoints = set(re.findall(r'[\'"`](/(?:api|ws)/[^\'"`\s]+)[\'"`]', content))
    
    # Also find charts / graphs
    charts = []
    if "ResponsiveContainer" in content or "LineChart" in content or "BarChart" in content or "AreaChart" in content:
        charts.append("Recharts")
    if "canvas" in content or ("Chart" in content and "lucide" not in content):
        charts.append("Canvas/Chart.js")
    if "svg" in content and not charts:
        charts.append("Inline SVG/D3")
    
    # Find filters
    filters = []
    if "<select" in content:
        filters.append("Select dropdown")
    if "filter" in content.lower():
        filters.append("Filter logic/controls")
    
    # Find sort
    sorts = []
    if "sort" in content.lower():
        sorts.append("Sort logic/controls")
        
    # Find buttons
    buttons = len(re.findall(r'<button', content))
    
    tab_analysis[tab_id] = {
        "file": comp_rel,
        "endpoints": sorted(list(endpoints)),
        "charts": charts,
        "filters": filters,
        "sorts": sorts,
        "button_count": buttons,
        "lines": len(content.splitlines()),
    }

with open("scratch/tab_deep_analysis.json", "w") as f:
    json.dump(tab_analysis, f, indent=2)

print(f"Scanned {len(tab_analysis)} tab components successfully.")
for tid, info in tab_analysis.items():
    print(f"[{tid}] {info['file']} | {info['lines']} lines | {info['button_count']} buttons | Charts: {info['charts']} | Endpoints: {len(info['endpoints'])}")
