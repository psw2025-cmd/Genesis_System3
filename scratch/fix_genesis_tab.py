from pathlib import Path

p = Path("dashboard/frontend/src/components/GenesisTab.tsx")
content = p.read_text(encoding="utf-8")

old_block = """  const profitRaw = data.brain?.profit_factor ?? effectiveSystem?.profit_factor ?? paper?.summary?.profit_factor ?? 'N/A - NO_PREDICTION'
  const profitFactor = profitRaw == null || profitRaw === '' || profitRaw === 'N/A - NO_PREDICTION' ? null : Number(profitRaw)
  const profitDisplay = profitRaw === 'N/A - NO_PREDICTION' ? 'N/A - NO_PREDICTION' : showNum(profitFactor)
  const driftRaw = data.brain?.drift_psi ?? data.brain?.psi ?? data.truth?.drift_psi
  const drift = driftRaw == null || driftRaw === '' ? null : Number(driftRaw)
  const showPct = (value: number | null) => value == null || !Number.isFinite(value) ? 'N/A' : `${value.toFixed(1)}%`
  const showNum = (value: number | null, digits = 2) => value == null || !Number.isFinite(value) ? 'N/A - NO_PREDICTION' : value.toFixed(digits)"""

new_block = """  const showPct = (value: number | null) => value == null || !Number.isFinite(value) ? 'N/A' : `${value.toFixed(1)}%`
  const showNum = (value: number | null, digits = 2) => value == null || !Number.isFinite(value) ? 'N/A - NO_PREDICTION' : value.toFixed(digits)
  const profitRaw = data.brain?.profit_factor ?? effectiveSystem?.profit_factor ?? paper?.summary?.profit_factor ?? 'N/A - NO_PREDICTION'
  const profitFactor = profitRaw == null || profitRaw === '' || profitRaw === 'N/A - NO_PREDICTION' ? null : Number(profitRaw)
  const profitDisplay = profitRaw === 'N/A - NO_PREDICTION' ? 'N/A - NO_PREDICTION' : showNum(profitFactor)
  const driftRaw = data.brain?.drift_psi ?? data.brain?.psi ?? data.truth?.drift_psi
  const drift = driftRaw == null || driftRaw === '' ? null : Number(driftRaw)"""

if old_block in content:
    p.write_text(content.replace(old_block, new_block, 1), encoding="utf-8")
    print("Fixed GenesisTab.tsx")
else:
    print("old_block not found in GenesisTab.tsx")
