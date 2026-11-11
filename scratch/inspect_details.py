import os
import re

def inspect_details():
    print("=== DEEP FILE DETAILS ===")
    
    # 1. Check verified_market.py
    with open('content/app/verified_market.py', 'r', encoding='utf-8') as f:
        vm_text = f.read()
    print("verified_market.py functions:", re.findall(r'def\s+([a-zA-Z0-9_]+)', vm_text))

    # 2. Check dhan_account_router.py
    with open('content/app/dhan_account_router.py', 'r', encoding='utf-8') as f:
        dar_text = f.read()
    print("dhan_account_router.py endpoints:", re.findall(r'@router\.(?:get|post)\(["\']([^"\']+)["\']', dar_text))

    # 3. Check memory_guard.py
    with open('dashboard/backend/middleware/memory_guard.py', 'r', encoding='utf-8') as f:
        mg_text = f.read()
    print("memory_guard.py functions:", re.findall(r'def\s+([a-zA-Z0-9_]+)', mg_text))

    # 4. Check broker_truth_validator.py
    with open('dashboard/backend/broker_truth_validator.py', 'r', encoding='utf-8') as f:
        btv_text = f.read()
    print("broker_truth_validator.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', btv_text))

    # 5. Check live_profit_validator.py
    with open('dashboard/backend/live_profit_validator.py', 'r', encoding='utf-8') as f:
        lpv_text = f.read()
    print("live_profit_validator.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', lpv_text))

    # 6. Check greeks_calculator.py
    with open('dashboard/backend/greeks_calculator.py', 'r', encoding='utf-8') as f:
        gc_text = f.read()
    print("greeks_calculator.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', gc_text))

    # 7. Check security_policy.py
    with open('dashboard/backend/security_policy.py', 'r', encoding='utf-8') as f:
        sp_text = f.read()
    print("security_policy.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', sp_text))

    # 8. Check cloud_paper_engine.py
    with open('dashboard/backend/cloud_paper_engine.py', 'r', encoding='utf-8') as f:
        cpe_text = f.read()
    print("cloud_paper_engine.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', cpe_text))

    # 9. Check firestore_state_backend.py
    with open('dashboard/backend/firestore_state_backend.py', 'r', encoding='utf-8') as f:
        fs_text = f.read()
    print("firestore_state_backend.py functions/classes:", re.findall(r'(?:class|def)\s+([a-zA-Z0-9_]+)', fs_text))

if __name__ == '__main__':
    inspect_details()
