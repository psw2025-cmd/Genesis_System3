import os
import re

def compare_implementations():
    print("=== DEEP COMPARISON OF KEY SUBSYSTEMS ===")

    # 1. Broker & Dhan implementation comparison
    print("\n--- 1. Dhan / Broker Implementation ---")
    with open('content/app/dhan_account_router.py', 'r', encoding='utf-8') as f:
        c_dhan = f.read()
    with open('content/app/verified_market.py', 'r', encoding='utf-8') as f:
        c_vm = f.read()
    with open('dashboard/backend/routers/broker.py', 'r', encoding='utf-8') as f:
        d_broker = f.read()
    with open('dashboard/backend/broker_truth_validator.py', 'r', encoding='utf-8') as f:
        d_truth = f.read()

    print(f"content/app dhan_account_router.py uses core/brokers/dhan/dhan_readonly: {'core.brokers.dhan.dhan_readonly' in c_dhan}")
    print(f"content/app verified_market.py has Dhan marketfeed quote API: {'marketfeed/quote' in c_vm}")
    print(f"dashboard/backend routers/broker.py has mock or real: {'mock' in d_broker.lower()}")
    print(f"dashboard/backend broker_truth_validator.py has zero-order check: {'orders' in d_truth.lower()}")

    # 2. Options Greeks and Chain comparison
    print("\n--- 2. Options Chain & Greeks Implementation ---")
    with open('content/app/app.py', 'r', encoding='utf-8') as f:
        c_app = f.read()
    with open('dashboard/backend/greeks_calculator.py', 'r', encoding='utf-8') as f:
        d_greeks = f.read()
    with open('dashboard/backend/routers/chain.py', 'r', encoding='utf-8') as f:
        d_chain = f.read()

    # Check Greeks calculation in content/app vs dashboard
    print("content/app _calc_bs_greeks in app.py:", '_calc_bs_greeks' in c_app)
    print("dashboard/backend greeks_calculator.py calculate_greeks:", 'calculate_greeks' in d_greeks)

    # 3. ML features comparison
    print("\n--- 3. ML Implementation ---")
    with open('dashboard/backend/routers/ml.py', 'r', encoding='utf-8') as f:
        d_ml = f.read()
    with open('dashboard/backend/ml_intelligence_service.py', 'r', encoding='utf-8') as f:
        d_ml_int = f.read()
    print("content/app ml routes:", 'ml_forecast_vs_actual' in c_app, 'ml_prediction_audit' in c_app, 'ml_benchmark' in c_app)
    print("dashboard/backend routers/ml.py endpoints:", len(re.findall(r'@router\.(?:get|post)', d_ml)))
    print("dashboard/backend ML intelligence service:", 'predict' in d_ml_int)

    # 4. Validation features comparison
    print("\n--- 4. Validation Implementation ---")
    with open('dashboard/backend/live_profit_validator.py', 'r', encoding='utf-8') as f:
        d_lpv = f.read()
    with open('dashboard/backend/multi_validation_audit.py', 'r', encoding='utf-8') as f:
        d_mva = f.read()
    with open('dashboard/backend/fo_eligibility_filter.py', 'r', encoding='utf-8') as f:
        d_foe = f.read()
    with open('dashboard/backend/option_strike_visibility_audit.py', 'r', encoding='utf-8') as f:
        d_osv = f.read()
    print("dashboard/backend live_profit_validator:", len(d_lpv))
    print("dashboard/backend multi_validation_audit:", len(d_mva))
    print("dashboard/backend fo_eligibility_filter:", len(d_foe))
    print("dashboard/backend option_strike_visibility_audit:", len(d_osv))

    # 5. Security features comparison
    print("\n--- 5. Security Implementation ---")
    with open('dashboard/backend/middleware/memory_guard.py', 'r', encoding='utf-8') as f:
        d_mg = f.read()
    with open('dashboard/backend/security_policy.py', 'r', encoding='utf-8') as f:
        d_sp = f.read()
    print("dashboard/backend memory_guard RSS monitoring:", 'rss' in d_mg.lower())
    print("dashboard/backend security_policy paper locks:", 'PAPER_MODE' in d_sp)

if __name__ == '__main__':
    compare_implementations()
