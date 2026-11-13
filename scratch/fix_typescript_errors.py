import json
from pathlib import Path

# 1. Update tsconfig.json to exclude test files that require vitest
tsconfig_path = Path("dashboard/frontend/tsconfig.json")
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))
tsconfig["exclude"] = ["node_modules", "dist", "**/*.test.ts", "**/*.test.tsx"]
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")
print("Updated tsconfig.json")

# 2. Update LiveInteractiveCharts.tsx
pnl_chart = Path("dashboard/frontend/src/components/LiveInteractiveCharts.tsx")
pnl_text = pnl_chart.read_text(encoding="utf-8")
pnl_old = "pnlHistory?: Array<{ date: string; pnl: number }>"
pnl_new = "pnlHistory?: Array<{ date: string; pnl: number; cumulative?: number }>"
if pnl_old in pnl_text:
    pnl_chart.write_text(pnl_text.replace(pnl_old, pnl_new, 1), encoding="utf-8")
    print("Updated LiveInteractiveCharts.tsx")
else:
    print("pnl_old not found")

# 3. Update Backtest.tsx
bt_path = Path("dashboard/frontend/src/components/Backtest.tsx")
bt_text = bt_path.read_text(encoding="utf-8")
bt_old = """type BacktestSummary = {
  status?: string
  passed?: boolean
  total_trades?: number
  win_rate?: number
  profit_factor?: number
  net_pnl?: number
  max_drawdown?: number
  generated_at?: string
  message?: string
  [key: string]: unknown
}"""
bt_new = """type BacktestSummary = {
  status?: string
  passed?: boolean
  total_trades?: number
  win_rate?: number
  profit_factor?: number
  net_pnl?: number
  max_drawdown?: number
  max_drawdown_pct?: number
  sharpe_ratio?: number | string
  avg_trade_expectancy?: number
  generated_at?: string
  message?: string
  [key: string]: unknown
}"""
if bt_old in bt_text:
    bt_path.write_text(bt_text.replace(bt_old, bt_new, 1), encoding="utf-8")
    print("Updated Backtest.tsx")
else:
    print("bt_old not found")

# 4. Update AdvancedCharts.tsx
adv_path = Path("dashboard/frontend/src/components/AdvancedCharts.tsx")
adv_text = adv_path.read_text(encoding="utf-8")
adv_text = adv_text.replace("useState<unknown>(null)", "useState<any>(null)")
adv_path.write_text(adv_text, encoding="utf-8")
print("Updated AdvancedCharts.tsx")

# 5. Update AgentConsole.tsx
ag_path = Path("dashboard/frontend/src/components/AgentConsole.tsx")
ag_text = ag_path.read_text(encoding="utf-8")
ag_text = ag_text.replace("useState<unknown>(null)", "useState<any>(null)")
ag_path.write_text(ag_text, encoding="utf-8")
print("Updated AgentConsole.tsx")

# 6. Update ChainAnalytics.tsx
chain_path = Path("dashboard/frontend/src/components/ChainAnalytics.tsx")
chain_text = chain_path.read_text(encoding="utf-8")
chain_text = chain_text.replace("useState<unknown>(null)", "useState<any>(null)")
chain_path.write_text(chain_text, encoding="utf-8")
print("Updated ChainAnalytics.tsx")

# 7. Update ControlPlane.tsx
cp_path = Path("dashboard/frontend/src/components/ControlPlane.tsx")
cp_text = cp_path.read_text(encoding="utf-8")
cp_text = cp_text.replace("useState<unknown>(null)", "useState<any>(null)")
cp_path.write_text(cp_text, encoding="utf-8")
print("Updated ControlPlane.tsx")

# 8. Update ModelBehavior.tsx
mb_path = Path("dashboard/frontend/src/components/ModelBehavior.tsx")
mb_text = mb_path.read_text(encoding="utf-8")
mb_text = mb_text.replace("useState<unknown>(null)", "useState<any>(null)")
mb_path.write_text(mb_text, encoding="utf-8")
print("Updated ModelBehavior.tsx")

# 9. Update Signals.tsx
sig_path = Path("dashboard/frontend/src/components/Signals.tsx")
sig_text = sig_path.read_text(encoding="utf-8")
sig_text = sig_text.replace("as unknown[]", "as any[]")
sig_text = sig_text.replace("useState<unknown>(null)", "useState<any>(null)")
sig_text = sig_text.replace("as unknown)?", "as any)?")
sig_path.write_text(sig_text, encoding="utf-8")
print("Updated Signals.tsx")
