import os
import re
import json

src_dir = "dashboard/frontend/src"

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Imported components
    imports = re.findall(r'import\s+(?:\{[^}]+\}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', content)
    
    # Interactive elements:
    # 1. Buttons and their onClick
    buttons = re.findall(r'<button([^>]*)>(.*?)</button>', content, re.DOTALL)
    button_details = []
    for b_attrs, b_text in buttons:
        has_click = "onClick" in b_attrs
        text_clean = re.sub(r'<[^>]+>', '', b_text).strip()[:40]
        disabled = "disabled" in b_attrs
        button_details.append({
            "text": text_clean or "Icon/Element",
            "has_click": has_click,
            "disabled": disabled,
        })
    
    # 2. Selects / Dropdowns
    selects = re.findall(r'<select([^>]*)>(.*?)</select>', content, re.DOTALL)
    select_details = []
    for s_attrs, s_body in selects:
        options = re.findall(r'<option[^>]*value=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</option>', s_body)
        if not options:
            options = re.findall(r'<option[^>]*>(.*?)</option>', s_body)
        select_details.append({
            "options_count": len(options),
            "options_sample": options[:5],
            "has_change": "onChange" in s_attrs
        })
    
    # 3. Tables and table headers (Sortable?)
    th_tags = re.findall(r'<th([^>]*)>(.*?)</th>', content, re.DOTALL)
    headers = []
    for th_attrs, th_text in th_tags:
        sortable = "onClick" in th_attrs or "cursor" in th_attrs or "sort" in th_attrs.lower()
        clean_text = re.sub(r'<[^>]+>', '', th_text).strip()[:30]
        if clean_text:
            headers.append({"text": clean_text, "sortable": sortable})
            
    # 4. Charts
    charts = []
    if "ResponsiveContainer" in content:
        charts.append("Recharts ResponsiveContainer")
    if "LineChart" in content:
        charts.append("Recharts LineChart")
    if "BarChart" in content:
        charts.append("Recharts BarChart")
    if "AreaChart" in content:
        charts.append("Recharts AreaChart")
    if "PieChart" in content:
        charts.append("Recharts PieChart")
    if "<canvas" in content:
        charts.append("HTML5 Canvas")
        
    # 5. Inputs (Search/Filter/Text)
    inputs = re.findall(r'<input([^>]*)>', content)
    input_details = []
    for inp in inputs:
        inp_type = "text"
        m_type = re.search(r'type=[\'"]([^\'"]+)[\'"]', inp)
        if m_type:
            inp_type = m_type.group(1)
        input_details.append({
            "type": inp_type,
            "has_change": "onChange" in inp,
            "placeholder": re.search(r'placeholder=[\'"]([^\'"]+)[\'"]', inp).group(1) if "placeholder=" in inp else ""
        })

    return {
        "lines": len(content.splitlines()),
        "imports": imports,
        "buttons": button_details,
        "selects": select_details,
        "table_headers": headers,
        "charts": charts,
        "inputs": input_details,
    }

components = [
    "workspaces/DecisionIntelligence.tsx",
    "workspaces/OptionsIntelligence.tsx",
    "workspaces/MultibaggerResearch.tsx",
    "workspaces/RiskAndScenarios.tsx",
    "workspaces/DataIntegrity.tsx",
    "workspaces/PredictionAudit.tsx",
    "SystemTruthControl.tsx",
    "Overview.tsx",
    "TradeTab.tsx",
    "Positions.tsx",
    "OptionChain.tsx",
    "Signals.tsx",
    "PaperTrading.tsx",
    "PerformanceTab.tsx",
    "MLPerformance.tsx",
    "SystemReadiness.tsx",
    "GenesisTab.tsx",
    "EndToEndProof.tsx",
    "BrokerProofPanel.tsx",
    "AlertsTab.tsx",
    "SystemTab.tsx",
    "LiveTradingGate.tsx",
    "LiveSimulation.tsx",
    "AdvancedCharts.tsx",
    "ChainAnalytics.tsx",
    "MarketTopCePeTable.tsx",
    "TopBar.tsx",
    "TruthStrip.tsx",
    "Sidebar.tsx",
]

report = {}
for c in components:
    p = os.path.join(src_dir, "components", c)
    if os.path.exists(p):
        report[c] = analyze_file(p)

with open("scratch/ui_interactivity_audit.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"Analyzed {len(report)} files.")
for name, data in report.items():
    print(f"[{name}] {len(data['buttons'])} buttons, {len(data['selects'])} selects, {len(data['inputs'])} inputs, {len(data['table_headers'])} th, Charts: {data['charts']}")
