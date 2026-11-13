import os
import re

def inspect_subsystems():
    print("=== INSPECTING SUBSYSTEMS ===")
    
    # 1. Broker features in dashboard/backend
    print("\n--- Dashboard Broker Files ---")
    broker_files = [
        'dashboard/backend/broker/dhan_auth.py',
        'dashboard/backend/routers/broker.py',
        'dashboard/backend/broker_truth_validator.py',
        'dashboard/backend/order_management.py',
        'dashboard/backend/position_reconciliation.py',
        'dashboard/backend/portfolio_truth_service.py',
        'dashboard/backend/broker_alert_deduplicator.py',
    ]
    for bf in broker_files:
        if os.path.exists(bf):
            with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l for l in f if l.strip() and not l.strip().startswith('#') and not 'OWNER' in l and not 'Policy' in l]
            print(f"  {bf}: {len(lines)} non-comment lines")

    # 2. Broker features in content/app
    print("\n--- Content Broker Files ---")
    c_broker_files = [
        'content/app/dhan_account_router.py',
        'content/app/verified_market.py',
        'content/app/probe_dhan_credentials.py',
    ]
    for bf in c_broker_files:
        if os.path.exists(bf):
            with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l for l in f if l.strip() and not l.strip().startswith('#') and not 'OWNER' in l and not 'Policy' in l]
            print(f"  {bf}: {len(lines)} non-comment lines")

    # 3. ML features in dashboard/backend
    print("\n--- Dashboard ML Files ---")
    ml_files = [
        'dashboard/backend/routers/ml.py',
        'dashboard/backend/ml_intelligence_service.py',
        'dashboard/backend/ml_performance_tracking.py',
        'dashboard/backend/ml_evidence_store.py',
        'dashboard/backend/genesis_ml_health.py',
        'dashboard/backend/accuracy_trend_service.py',
        'dashboard/backend/performance_predictor.py',
        'dashboard/backend/greeks_calculator.py',
        'dashboard/backend/synthetic_data_generator.py',
    ]
    for mf in ml_files:
        if os.path.exists(mf):
            with open(mf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l for l in f if l.strip() and not l.strip().startswith('#') and not 'OWNER' in l and not 'Policy' in l]
            print(f"  {mf}: {len(lines)} non-comment lines")

    # 4. Validation features in dashboard/backend
    print("\n--- Dashboard Validation Files ---")
    val_files = [
        'dashboard/backend/broker_truth_validator.py',
        'dashboard/backend/live_profit_validator.py',
        'dashboard/backend/multi_validation_audit.py',
        'dashboard/backend/fo_eligibility_filter.py',
        'dashboard/backend/option_strike_visibility_audit.py',
        'dashboard/backend/paper_ledger_guard.py',
        'dashboard/backend/paper_feed_admission.py',
        'dashboard/backend/signal_plan_audit.py',
        'dashboard/backend/continuous_closure_service.py',
        'dashboard/backend/proof_ledger_service.py',
    ]
    for vf in val_files:
        if os.path.exists(vf):
            with open(vf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l for l in f if l.strip() and not l.strip().startswith('#') and not 'OWNER' in l and not 'Policy' in l]
            print(f"  {vf}: {len(lines)} non-comment lines")

    # 5. Security features in dashboard/backend
    print("\n--- Dashboard Security Files ---")
    sec_files = [
        'dashboard/backend/security_policy.py',
        'dashboard/backend/secure_app.py',
        'dashboard/backend/middleware/memory_guard.py',
        'dashboard/backend/auto_gates_service.py',
        'dashboard/backend/risk_management.py',
    ]
    for sf in sec_files:
        if os.path.exists(sf):
            with open(sf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l for l in f if l.strip() and not l.strip().startswith('#') and not 'OWNER' in l and not 'Policy' in l]
            print(f"  {sf}: {len(lines)} non-comment lines")

if __name__ == '__main__':
    inspect_subsystems()
