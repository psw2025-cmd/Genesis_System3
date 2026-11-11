import os
import sys
import importlib.util

VENV_PYTHON = r"C:\Genesis_System3_clean\.venv\Scripts\python.exe"
APP_FILE = r"C:\Genesis_System3_clean\content\app\app.py"
TEMPLATE_FILE = r"C:\Genesis_System3_clean\content\app\templates\premium.html"

def validate_environment():
    print("=========================================================")
    print("      RUNNING GENESIS MULTI-POINT VALIDATION GATE        ")
    print("=========================================================")
    errors = 0

    # 1. Check if python venv exists
    if not os.path.exists(VENV_PYTHON):
        print(f"❌ [BLOCKER] Venv Python interpreter missing at: {VENV_PYTHON}")
        errors += 1
    else:
        print("✅ Venv Python executable verified.")

    # 2. Check if dhanhq package can be loaded from venv path
    sys.path.insert(0, r"C:\Genesis_System3_clean\.venv\Lib\site-packages")
    if importlib.util.find_spec("dhanhq") is None:
        print("❌ [BLOCKER DETECTED] 'dhanhq' package is NOT installed in the virtual environment!")
        errors += 1
    else:
        print("✅ 'dhanhq' package verified as installed.")

    # 3. Check for fake JSON fallbacks in app.py
    if os.path.exists(APP_FILE):
        with open(APP_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if "market_top_ce_pe.json" in content:
                print("❌ [BLOCKER DETECTED] app.py still contains hardcoded fallback reference to 'market_top_ce_pe.json'!")
                errors += 1
            else:
                print("✅ No hardcoded JSON market fallback detected in app.py.")

    # 4. Check for hardcoded UI badges in premium.html
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            template_content = f.read()
            if "CONNECTED (Dhan)" in template_content:
                print("❌ [BLOCKER DETECTED] premium.html contains a hardcoded connection badge!")
                errors += 1
            else:
                print("✅ UI template connection badge is dynamically clean.")

    print("=========================================================")
    if errors > 0:
        print(f"🚨 VALIDATION FAILED: {errors} critical violation(s) found.")
        sys.exit(1)
    else:
        print("🎉 ALL MULTI-VALIDATION CHECKS PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    validate_environment()