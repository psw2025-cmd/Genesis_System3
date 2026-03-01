"""
setup_live_system.py — FIXED (handles _env and .env both)
==========================================================
Run: .venv\Scripts\python.exe setup_live_system.py
"""

import os, sys, json, subprocess, datetime

BASE_DIR    = r"C:\Genesis_System3"
CONFIG_DIR  = os.path.join(BASE_DIR, "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "angel_config.json")
PIP         = os.path.join(BASE_DIR, ".venv", "Scripts", "pip.exe")

os.makedirs(CONFIG_DIR, exist_ok=True)

REQUIRED_PACKAGES = [
    "smartapi-python", "websocket-client",
    "pyotp", "pytz", "xgboost",
    "scikit-learn", "pandas", "numpy",
]

# ── 1. READ .env / _env (tries both) ─────────────────────────────────────────
def read_env():
    # Try all possible env file locations/names
    candidates = [
        os.path.join(BASE_DIR, ".env"),
        os.path.join(BASE_DIR, "_env"),
        os.path.join(BASE_DIR, "config", ".env"),
        os.path.join(BASE_DIR, "config", "_env"),
    ]

    found_path = None
    for path in candidates:
        if os.path.exists(path):
            found_path = path
            break

    if not found_path:
        print(f"[ERROR] No .env or _env file found. Checked:")
        for p in candidates:
            print(f"  - {p}")
        return None

    print(f"  [✓] Found env file: {found_path}")

    # Read with UTF-8-SIG to handle BOM, splitlines() handles CRLF/LF
    with open(found_path, 'rb') as f:
        raw = f.read()
    content = raw.decode('utf-8-sig')

    env = {}
    for line in content.splitlines():
        line = line.strip()
        if '=' in line and not line.startswith('#') and line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

    print(f"  [✓] Parsed {len(env)} keys: {list(env.keys())}")

    required = ['ANGELONE_API_KEY', 'ANGELONE_CLIENT_ID', 'ANGELONE_TOTP']
    missing  = [k for k in required if not env.get(k)]
    if missing:
        print(f"  [ERROR] Still missing: {missing}")
        print(f"  Keys found: {list(env.keys())}")
        return None

    print(f"  [✓] Client  : {env['ANGELONE_CLIENT_ID']}")
    print(f"  [✓] API Key : {env['ANGELONE_API_KEY'][:4]}****")
    print(f"  [✓] TOTP    : {env['ANGELONE_TOTP'][:6]}****")
    return env


# ── 2. INSTALL PACKAGES ───────────────────────────────────────────────────────
def install_packages():
    print("\n[2/4] Installing packages...")
    for pkg in REQUIRED_PACKAGES:
        r = subprocess.run([PIP, "install", pkg, "--quiet"],
                           capture_output=True, text=True)
        print(f"  {'✓' if r.returncode==0 else '✗'} {pkg}")


# ── 3. WRITE angel_config.json ────────────────────────────────────────────────
def write_config(env):
    password = env.get('ANGELONE_PIN') or env.get('ANGELONE_PASSWORD', '')
    cfg = {
        "api_key":     env['ANGELONE_API_KEY'],
        "client_id":   env['ANGELONE_CLIENT_ID'],
        "password":    password,
        "totp_secret": env['ANGELONE_TOTP'],
        "_source":     "auto-generated from env file"
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)
    print(f"\n[3/4] Config written → {CONFIG_PATH}")
    return cfg


# ── 4. VALIDATE CONNECTION ────────────────────────────────────────────────────
def validate(cfg):
    print("\n[4/4] Testing Angel Broking connection...")
    try:
        from SmartApi import SmartConnect
        import pyotp

        obj  = SmartConnect(api_key=cfg['api_key'])
        totp = pyotp.TOTP(cfg['totp_secret']).now()
        data = obj.generateSession(cfg['client_id'], cfg['password'], totp)

        if not data['status']:
            print(f"  [✗] Login failed: {data.get('message', '')}")
            return False, None

        profile = obj.getProfile(data['data']['refreshToken'])
        name    = profile['data'].get('name', 'Unknown')
        print(f"  [✓] CONNECTED — {name} ({cfg['client_id']})")

        # Test live NIFTY candle fetch
        now    = datetime.datetime.now()
        params = {
            "exchange": "NSE", "symboltoken": "99926000",
            "interval": "ONE_HOUR",
            "fromdate": (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "todate":   now.strftime("%Y-%m-%d %H:%M"),
        }
        candles = obj.getCandleData(params)
        if candles['status'] and candles['data']:
            last = candles['data'][-1]
            print(f"  [✓] Live NIFTY last close: {last[4]:.2f}")
        else:
            print(f"  [!] Candle fetch: {candles.get('message', 'no data')}")

        return True, obj

    except ImportError:
        print("  [!] SmartAPI not installed yet — will be ready after step 2")
        return False, None
    except Exception as e:
        print(f"  [✗] Connection error: {e}")
        return False, None


# ── MAIN ──────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  GENESIS SYSTEM3 — SMART SETUP")
print("=" * 65)

print("\n[1/4] Reading env credentials...")
env = read_env()
if not env:
    print("\n[MANUAL FIX] Run this in PowerShell to check your env file:")
    print(f"  Get-Content C:\\Genesis_System3\\.env")
    print(f"  Get-Content C:\\Genesis_System3\\_env")
    sys.exit(1)

install_packages()
cfg = write_config(env)
connected, _ = validate(cfg)

print("\n" + "=" * 65)
if connected:
    print("""
  ✅ FULLY CONNECTED — Ready to run live pipeline

  RUN ORDER:
  ─────────────────────────────────────────────────────
  Full auto (every hour, 09:15-15:30 IST):
    .venv\\Scripts\\python.exe genesis_scheduler.py

  Manual one-shot test:
    .venv\\Scripts\\python.exe angel_data_fetcher.py
    .venv\\Scripts\\python.exe live_train_and_rank.py

  Top 5 output → storage\\signals\\top5_LATEST.json
  ─────────────────────────────────────────────────────
""")
else:
    print("""
  ⚠️  Packages installed but connection needs retry.
  Re-run: .venv\\Scripts\\python.exe setup_live_system.py
""")
print("=" * 65)
