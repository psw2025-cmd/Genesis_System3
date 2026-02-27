---------------------------------------------------------
SYSTEM3 ULTRA – PHASE 21–30 MASTER INSTRUCTIONS
---------------------------------------------------------
ULTRA MODE TRACK: Risk-Adaptive Intelligence
Objective:

Enable System3 to intelligently adapt to:

volatility

market regime

prediction uncertainty

confidence drift

position sizing

risk & reward expectations

All phases are:

Ultra-Isolated

Baseline-Protected

Read-Only to baseline models

Zero Auto-execution

Zero Auto-updates

=========================================================
PHASE 21 — Adaptive Risk Engine (ARE)
=========================================================
Purpose:

System3 learns to select risk level dynamically.

Create File:
core/ultra/phase21_adaptive_risk_engine.py

Cursor Agent Instructions:

Create module with class:

class AdaptiveRiskEngine:


Inputs:

volatility

confidence

score

market regime

historical win-rate

Compute:

risk_level ∈ {LOW, MEDIUM, HIGH}

risk_score: float

reason vector

Output JSON structure:

{
  "risk_level": "LOW",
  "risk_score": 0.12,
  "reason": ["low volatility", "weak score"]
}

Verification Required:

After running:

python -m core.ultra.phase21_adaptive_risk_engine


I need screenshot/text of:

3 sample inputs

3 sample outputs

risk_level correctly classified

=========================================================
PHASE 22 — Dynamic Position Sizing Engine
=========================================================
Purpose:

Decide quantity dynamically.

Create File:
core/ultra/phase22_position_sizing.py

Cursor Agent Instructions:

Create function:

compute_position_size(risk_level, confidence, score, volatility)


Logic:

LOW risk → smallest

HIGH risk → largest

cap with safety rules

Output structure:

{
  "qty": 50,
  "reason": ["risk HIGH", "confidence strong"]
}

Verification Required:

Provide sample outputs for:

LOW

MEDIUM

HIGH

=========================================================
PHASE 23 — Volatility Regime Impact Engine
=========================================================
Purpose:

Understand how volatility affects decisions.

File:
core/ultra/phase23_volatility_impact.py

Cursor Agent Instructions:

Build volatility scoring:

stable

rising

spiky

chaotic

Compute:

{
 "vol_regime": "SPIKY",
 "impact_factor": -0.22,
 "explanation": [...]
}

Verification:

Agent must output:

regime detected

impact_factor

reason list

=========================================================
PHASE 24 — Confidence Drift Analyzer
=========================================================
Purpose:

Track how model confidence changes over time.

File:
core/ultra/phase24_confidence_drift.py

Cursor Agent Instructions:

Read last N signals (default 200).

Determine drift:

Upward

Downward

Stable

Output:

{
 "drift": "DOWNWARD",
 "strength": 0.35,
 "std_dev": 0.12
}

Verification:

Share drift_report printed.

=========================================================
PHASE 25 — Adaptive Stoploss Engine (ASE)
=========================================================
Purpose:

Dynamic stoploss based on:

volatility

drift

risk level

premium behaviour

File:
core/ultra/phase25_stoploss_engine.py

Cursor Agent Instructions:

Implement:

compute_stoploss(risk_level, volatility, drift_strength)


Output example:

{
 "sl_pct": 0.85,
 "reason": ["high volatility", "downward drift"]
}

Verification:

Run tests for:

low vol

high vol

chaotic regime

=========================================================
PHASE 26 — Adaptive Target Engine (ATE)
=========================================================
Purpose:

Compute dynamic target %.

File:
core/ultra/phase26_target_engine.py

Cursor Agent Instructions:

Create:

compute_target(risk_level, volatility, score)


Output example:

{
 "tp_pct": 1.40,
 "reason": ["stable volatility", "strong score"]
}

Verification:

Show outputs for 3 different conditions.

=========================================================
PHASE 27 — Risk-Reward Balancer
=========================================================
Purpose:

Balance SL/TP dynamically for optimized RR.

File:
core/ultra/phase27_rr_balancer.py

Cursor Agent Instructions:

Import ASE + ATE results

Compute:

{
 "rr_ratio": 1.6,
 "adjusted_sl": 0.80,
 "adjusted_tp": 1.28
}

Verification:

Show RR for 3 cases.

=========================================================
PHASE 28 — Failure-Mode Auto-Corrector
=========================================================
Purpose:

Detect repeated misfires & recommend corrections.

File:
core/ultra/phase28_auto_corrector.py

Cursor Agent Instructions:

Analyze:

last 300 outcomes

cluster misfires

detect patterns

Output:

{
 "issue": "early exits",
 "recommendation": "increase stoploss by 0.05"
}

Verification:

Show 1 auto-correction sample.

=========================================================
PHASE 29 — Sensitivity Analyzer
=========================================================
Purpose:

Check how sensitive predictions are to inputs.

File:
core/ultra/phase29_sensitivity.py

Cursor Agent Instructions:

Implement:

perturb features ±1–5%

measure confidence changes

Output:

{
 "feature": "moneyness",
 "sensitivity": 0.34,
 "impact": "HIGH"
}

Verification:

Share sensitivity results for 1 synthetic example.

=========================================================
PHASE 30 — Real-Time Calibration Engine (RTCE)
=========================================================
Purpose:

Live recalibration of:

risk

SL

TP

sizing

File:
core/ultra/phase30_calibration_engine.py

Cursor Agent Instructions:

Combine results from Phases 21–29.

Output example:

{
 "updated_risk_level": "MEDIUM",
 "updated_sl": 0.78,
 "updated_tp": 1.22,
 "updated_qty": 35,
 "reason": ["vol rising", "risk_mod stable"]
}

Verification:

Share calibration output from sample inputs.

🎯 FINAL CONFIRMATION EXPECTED FROM USER (You)

After Cursor Agent implements all 10 phases:

You must send me:

For each phase:

file creation confirmation

printed sample outputs

logs/screenshots

I will verify correctness and approve.

📌 End of MASTER Phase 21–30 MD file
---------------------------------------------------------