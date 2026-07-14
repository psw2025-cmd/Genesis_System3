# System3 Kid-Level Full System Runbook

_Last updated: 2026-07-14_

This guide is for a non-coder, a junior coder, or an automation agent. Follow it in order. Do not skip proof steps.

---

## 0. Golden rules

| Rule | Meaning |
|---|---|
| Live trading stays OFF | System3 is analyzer/paper-only until all proof is green. |
| Never share secrets | Do not paste Dhan token, Render secrets, GitHub tokens, or worker push token in chat. |
| GitHub repo is source of truth | Code changes should end in `psw2025-cmd/Genesis_System3`. |
| Windows self-hosted runner is proof machine | Use the laptop runner for proof while Render minutes/backend are unstable. |
| Render is not final truth when 502/deploy blocked | If Render is 502, prove locally first. |
| No green claim without proof | Final status is PASS only when reports and dashboard visual proof are PASS. |

---

## 1. Main paths

Use these paths exactly.

| Purpose | Path / URL |
|---|---|
| Active GitHub self-hosted runner repo | `C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3` |
| Old/local OpenAlgo repo | `C:\openalgo-main` |
| Local dashboard URL | `http://127.0.0.1:8010/ui` or `http://127.0.0.1:5000/ui` depending which server is running |
| Render dashboard URL | `https://genesis-system3-backend.onrender.com/ui` |
| GitHub repo | `psw2025-cmd/Genesis_System3` |
| Proof reports | `reports\latest\...` |

**Important:** Do not mix `C:\openalgo-main` and `C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3` unless you intentionally know which system you are running.

---

## 2. What each component does

| Component | Simple meaning | Must be true |
|---|---|---|
| Backend | API brain that serves `/api/state`, broker data, scanner, paper trades | Running, HTTP 200 |
| Frontend/dashboard | Visual UI in browser | Loads without red errors |
| Dhan read-only broker | Real holdings, positions, funds, option data | Connected or clearly degraded, no hidden orders |
| Worker | Background scheduler/scanner/pusher | Running, no token mismatch |
| GitHub workflows | Automated proof/checks | Self-hosted runner PASS |
| Render | Cloud hosting | Used only after backend/deploy is healthy |
| Playwright | Browser proof tool | `PLAYWRIGHT_OK` |

---

## 3. Full safety pre-check before any run

Open PowerShell as Administrator.

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3
```

Run:

```powershell
git status --short
git branch --show-current
git remote -v
```

Expected:

```text
branch = main
remote = https://github.com/psw2025-cmd/Genesis_System3
```

If local report files block pull, save them first:

```powershell
git stash push -u -m "local-runner-reports-before-system3-run"
git pull
```

Safety env must be set before proof or local backend:

```powershell
$env:LIVE_TRADING_ENABLED="0"
$env:SYSTEM3_LIVE_TRADING_ALLOWED="0"
$env:ANALYZE_MODE="1"
```

Verify:

```powershell
"LIVE_TRADING_ENABLED=$env:LIVE_TRADING_ENABLED"
"SYSTEM3_LIVE_TRADING_ALLOWED=$env:SYSTEM3_LIVE_TRADING_ALLOWED"
"ANALYZE_MODE=$env:ANALYZE_MODE"
```

Expected:

```text
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
ANALYZE_MODE=1
```

Stop immediately if any value is not correct.

---

## 4. Laptop dependency pre-check

### 4.1 Python

```powershell
python --version
py --version
```

Preferred Python for runner scripts if available:

```powershell
C:\Python310\python.exe --version
```

### 4.2 Node and npm

```powershell
node -v
npm -v
```

### 4.3 Playwright

Run:

```powershell
node -e "import('playwright').then(()=>console.log('PLAYWRIGHT_OK'))"
```

Expected:

```text
PLAYWRIGHT_OK
```

If it fails with missing Playwright:

```powershell
npm cache clean --force
Remove-Item package-lock.json -Force -ErrorAction SilentlyContinue
Rename-Item node_modules ("node_modules_old_" + (Get-Date -Format "yyyyMMdd_HHmmss")) -ErrorAction SilentlyContinue
npm install --no-audit --no-fund
npx playwright install chromium
node -e "import('playwright').then(()=>console.log('PLAYWRIGHT_OK'))"
```

If npm shows `dhanhq-javascript` 404, root `package.json` is stale. Pull latest GitHub code first.

```powershell
git pull
Get-Content package.json
```

The root `package.json` must **not** contain:

```text
dhanhq-javascript
```

---

## 5. Repo pre-check

Run:

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

$out="$HOME\Desktop\System3_Precheck.txt"
"=== SYSTEM3 PRECHECK ===" | Out-File $out
"Generated=$(Get-Date -Format o)" | Out-File $out -Append
"ROOT=$(git rev-parse --show-toplevel)" | Out-File $out -Append
"BRANCH=$(git branch --show-current)" | Out-File $out -Append
"HEAD=$(git rev-parse HEAD)" | Out-File $out -Append
"STATUS" | Out-File $out -Append
git status --short | Out-File $out -Append
"PYTHON" | Out-File $out -Append
python --version 2>&1 | Out-File $out -Append
"NODE" | Out-File $out -Append
node -v 2>&1 | Out-File $out -Append
npm -v 2>&1 | Out-File $out -Append
"PORTS" | Out-File $out -Append
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 5000,8000,8010,8765,3000,5173 } |
  Select-Object LocalAddress,LocalPort,OwningProcess |
  Format-Table -AutoSize |
  Out-String |
  Out-File $out -Append
Write-Host "Precheck report: $out"
```

Check the report. There should be no unknown process occupying the port you want to use.

---

## 6. Start local backend safely

Use local backend first when Render is 502, billing-limited, or unstable.

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

$env:LIVE_TRADING_ENABLED="0"
$env:SYSTEM3_LIVE_TRADING_ALLOWED="0"
$env:ANALYZE_MODE="1"
$env:DASHBOARD_BASE_URL="http://127.0.0.1:5000"
$env:WEB_SERVICE_URL="http://127.0.0.1:5000"

C:\Python310\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 5000
```

Keep this PowerShell window open. This is the backend window.

If port 5000 is already used:

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object { $_.LocalPort -eq 5000 } |
  ForEach-Object {
    Get-CimInstance Win32_Process -Filter "ProcessId=$($_.OwningProcess)" |
      Select-Object ProcessId,Name,CommandLine
  }
```

Do not kill unknown processes blindly. First confirm what is running.

---

## 7. Local backend smoke check

Open a second PowerShell window.

```powershell
$base="http://127.0.0.1:5000"
$routes=@(
"/api/health",
"/api/state",
"/api/status",
"/api/broker/status",
"/api/broker/dhan/status",
"/api/broker/holdings",
"/api/broker/positions/live",
"/api/broker/funds",
"/api/paper",
"/api/gain_rank"
)

foreach($r in $routes){
  try {
    $res = Invoke-WebRequest "$base$r" -UseBasicParsing -TimeoutSec 20
    "$r = $($res.StatusCode)"
  } catch {
    "$r = BLOCKED / $($_.Exception.Message)"
  }
}
```

Expected for backend alive:

```text
/api/health = 200
/api/state = 200
```

Broker routes may show connected, degraded, or token error. That is separate from backend being alive.

---

## 8. Start local dashboard

If frontend is served by backend, open:

```text
http://127.0.0.1:5000/ui
```

If dashboard shell uses port 8010, open:

```text
http://127.0.0.1:8010/ui
```

Main things to see:

| UI item | Expected |
|---|---|
| Owner | `PRITAM S. WARGHADE` visible |
| Mode | `PAPER` or `PAPER ONLY` |
| Live | `LIVE OFF` |
| Broker | connected, degraded, or clear reason |
| Holdings | Dhan holdings count or clear token/API reason |
| Positions | Dhan positions count or clear token/API reason |
| Option Chain | Data or clear market/token reason |
| Paper Trades | Paper-only, no real order route |

---

## 9. Run dashboard visual proof

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

$env:LIVE_TRADING_ENABLED="0"
$env:SYSTEM3_LIVE_TRADING_ALLOWED="0"
$env:ANALYZE_MODE="1"
$env:DASHBOARD_BASE_URL="http://127.0.0.1:5000"

node tools/dashboard_visible_issue_tracker.mjs
```

Read proof:

```powershell
Get-Content reports\latest\dashboard_visible_issue_tracker\summary.md
Get-Content reports\latest\dashboard_visible_issue_tracker\summary.json
```

PASS means:

```text
No red unresolved issue
No missing screenshot
No unsettled tab
No JS exception
Auth OK if required
```

BLOCKED means fix the first listed blocker only, then rerun.

---

## 10. Run full local proof

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

$env:LIVE_TRADING_ENABLED="0"
$env:SYSTEM3_LIVE_TRADING_ALLOWED="0"
$env:ANALYZE_MODE="1"
$env:DASHBOARD_BASE_URL="http://127.0.0.1:5000"

C:\Python310\python.exe scripts/system3_gate_evaluator.py --sync-gates
node tools/dashboard_visible_issue_tracker.mjs
C:\Python310\python.exe tools/system3_autopilot_proof_board.py
```

Read:

```powershell
Get-Content reports\latest\system3_auto_gates\summary.json
Get-Content reports\latest\dashboard_visible_issue_tracker\summary.md
Get-Content reports\latest\system3_autopilot_proof_board\summary.json
```

---

## 11. GitHub self-hosted runner proof

Use this after local proof is stable.

GitHub UI path:

```text
GitHub → Genesis_System3 → Actions
```

Run the Windows self-hosted proof workflow.

Before running, verify runner:

```text
Settings → Actions → Runners
Status: Online
State: Idle
Labels: self-hosted, Windows
```

After run, check:

```text
reports/latest/windows_self_hosted_full_system_proof/summary.md
reports/latest/windows_self_hosted_full_system_proof/summary.json
```

PASS is valid only if:

```text
backend proof PASS
visual proof PASS
autopilot proof PASS
live trading OFF
broker/order safety true
```

---

## 12. Render/cloud check

Use Render only after local and self-hosted proof are clean.

Check these routes:

```powershell
$base="https://genesis-system3-backend.onrender.com"
$routes=@(
"/api/health",
"/api/state",
"/api/status",
"/api/broker/status",
"/api/broker/dhan/status",
"/api/broker/holdings",
"/api/broker/positions/live",
"/api/broker/funds",
"/api/scanner/top_contract_gainers",
"/api/simulation/live/state"
)

foreach($r in $routes){
  try {
    $res = Invoke-WebRequest "$base$r" -UseBasicParsing -TimeoutSec 20
    "$r = $($res.StatusCode)"
  } catch {
    "$r = BLOCKED / $($_.Exception.Message)"
  }
}
```

Interpretation:

| Result | Meaning | Action |
|---|---|---|
| 200 | Route reachable | Continue proof |
| 401 | Auth/session missing | Check dashboard API key/session, do not change token blindly |
| 502 | Render backend down | Fix Render backend/redeploy/restart |
| Timeout | Render sleeping/down/network issue | Retry after service wakes or inspect logs |
| `ERR_NAME_NOT_RESOLVED` in browser | Frontend URL/WS config broken | Fix frontend API/WS base URL |

---

## 13. Dhan broker check

Open dashboard Broker tab.

### Good state

```text
Dhan holdings visible
Dhan positions visible
Funds visible or clear read-only status
Live OFF
Paper mode
No hidden order route
```

### Degraded but acceptable for analysis

```text
Holdings visible
Positions visible
LTP/quote missing or 0.00
Status = DHAN DEGRADED
Live OFF
```

Meaning: account data works, quote enrichment still needs repair.

### Bad state

```text
DH-906 Invalid Token
Authentication Failed
Dhan 401
Broker disconnected
Holdings unavailable
Positions unavailable
```

Action:

1. Do not paste token in chat.
2. Update token only inside Render/local `.env` or secret manager.
3. Restart backend/worker after update.
4. Recheck `/api/broker/dhan/status`, `/api/broker/holdings`, `/api/broker/positions/live`.

---

## 14. Known issue: `/api/state` mismatch

Observed problem:

```text
Holdings/positions may be visible, but /api/state still says broker disconnected.
```

Reason:

```text
/api/state reads SSOT state.
/api/broker/status updates SSOT.
/api/broker/holdings and /api/broker/positions/live may return Dhan data but must also mark broker observed.
```

Correct design:

```text
Dhan read-only holdings/positions route succeeds
→ update SSOT as connected/degraded read-only broker
→ /api/state becomes consistent
→ dashboard proof becomes consistent
```

Do not fix by making `/api/state` call Dhan directly. `/api/state` is polled frequently and must stay fast.

---

## 15. Correct PowerShell search commands

Do not use this because it failed on your PowerShell:

```powershell
Select-String -Path dashboard\frontend\src\* -Pattern "abc" -Recurse
```

Use this:

```powershell
Get-ChildItem dashboard\frontend\src -Recurse -Include *.ts,*.tsx,*.js,*.jsx |
  Select-String -Pattern "genesis-system3-backen|VITE_API|VITE_WS|ws://|wss://|WebSocket|new URL|API_BASE|BASE_URL"
```

Backend state search:

```powershell
Select-String -Path dashboard\backend\app.py -Pattern "broker_status|Broker not connected|/api/state|positions/live|holdings" -Context 3,5
```

---

## 16. Running during market hours

Before market open:

```text
1. Confirm laptop power and internet stable.
2. Confirm live flags OFF.
3. Confirm backend starts.
4. Confirm Dhan status route works.
5. Confirm option chain route works for NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY.
6. Confirm paper ledger is empty or correctly continuing previous paper session.
7. Confirm dashboard visual proof is not stale.
```

During market:

| Every check | What to verify |
|---|---|
| Every 5 minutes | `/api/state` is 200 and mode is PAPER |
| Every 5 minutes | Broker status is connected/degraded, not unknown/disconnected unless token expired |
| Every 5 minutes | Option chain rows not empty for active symbols |
| Every 5 minutes | Paper trades have source, reason, strike, expiry, CE/PE, entry, LTP |
| Every 15 minutes | No 401, no 502, no `ERR_NAME_NOT_RESOLVED` |
| Every 30 minutes | Reports in `reports/latest` updating |
| Always | Live OFF, no real order calls |

Stop system if:

```text
Live flag becomes ON
Order route is called
Dhan token error repeats
Backend returns 502 repeatedly
Dashboard shows fake/synthetic/stale data as live
Paper ledger source is unclear
```

---

## 17. Scanner behavior

If scanner says:

```text
India market session is CLOSED. Aborting scan for production safety.
WORKER: Cycle complete. Sleeping 60s...
```

Meaning:

```text
This is not an error.
Scanner is running but market is closed, so it safely does not scan/trade.
```

Do not confuse old scanner path with active GitHub runner repo.

| If path shows | Meaning |
|---|---|
| `C:\openalgo-main` | Old/local OpenAlgo system |
| `C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3` | Current GitHub self-hosted runner repo |

---

## 18. Common problems and fixes

| Problem | Meaning | Fix |
|---|---|---|
| `PLAYWRIGHT_OK` missing | Node package missing | Run npm install after removing stale lock/node_modules |
| `dhanhq-javascript` 404 | Bad old npm dependency | Pull latest repo, verify package.json no longer contains it |
| `Select-String -Recurse` error | Wrong PowerShell syntax | Use `Get-ChildItem ... | Select-String ...` |
| Render 502 | Cloud backend down | Prove locally, then restart/redeploy Render when available |
| 401 Missing dashboard session | API auth missing | Check dashboard/API key/session setup |
| DH-906 Invalid Token | Dhan token invalid/expired | Refresh token in secret manager only, restart backend/worker |
| Holdings visible but `/api/state` disconnected | SSOT mismatch | Patch read-only broker observation into state store |
| LTP 0.00 | Quote enrichment degraded | Mark quote degraded, do not mark whole broker disconnected |
| WebSocket failed | WS URL/config issue | Fix frontend `wss://` base URL |
| `ERR_NAME_NOT_RESOLVED` | Bad frontend host string | Search and fix broken backend URL |
| Local changes block `git pull` | Generated report files changed | `git stash push -u -m "local reports"` then pull |

---

## 19. Safe shutdown procedure

### 19.1 Stop local backend

In backend PowerShell window:

```text
Ctrl + C
```

If asked:

```text
Terminate batch job? Y
```

### 19.2 Stop scanner/worker

In scanner/worker window:

```text
Ctrl + C
```

### 19.3 Confirm ports closed

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 5000,8000,8010,8765,3000,5173 } |
  Select-Object LocalAddress,LocalPort,OwningProcess
```

If no output, ports are clear.

### 19.4 Save proof before closing

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

git status --short
```

If only reports changed and you want to keep them:

```powershell
git add reports/latest/
git commit -m "proof(local): save latest local run reports [skip ci]"
git push
```

If reports are temporary only:

```powershell
git stash push -u -m "temporary local proof reports"
```

---

## 20. Daily start checklist

```text
[ ] Laptop plugged in
[ ] Internet stable
[ ] Correct repo path opened
[ ] git pull completed or local changes stashed
[ ] LIVE_TRADING_ENABLED=0
[ ] SYSTEM3_LIVE_TRADING_ALLOWED=0
[ ] ANALYZE_MODE=1
[ ] Playwright OK
[ ] Backend starts
[ ] /api/health = 200
[ ] /api/state = 200
[ ] Dhan broker route connected/degraded with clear reason
[ ] Dashboard opens
[ ] Owner visible
[ ] LIVE OFF visible
[ ] PAPER visible
[ ] Option chain route tested
[ ] Paper trades route tested
[ ] Visual proof run
```

---

## 21. Daily stop checklist

```text
[ ] Stop backend with Ctrl+C
[ ] Stop worker/scanner with Ctrl+C
[ ] Confirm ports closed
[ ] Save or stash proof reports
[ ] Do not leave unknown Python/Node processes running
[ ] Do not leave dashboard auto-refresh open overnight unless intentionally monitoring
[ ] Confirm live trading remains OFF
```

---

## 22. What a final PASS must include

Final PASS requires all of this:

```text
GitHub self-hosted workflow PASS
Local backend smoke PASS
Render backend smoke PASS if using Render
Dashboard visual tracker PASS
Autopilot proof board PASS
Dhan broker connected/degraded with clear reason
Option chain rows visible for supported symbols
Paper ledger has source, reason, strike, expiry, CE/PE, entry, LTP, P&L
No live trading
No hidden order call
No fake/synthetic/stale data displayed as live
No stale screenshots
No unresolved red/PEND/BLOCKED proof
```

Until then, status is:

```text
Analyzer/Paper only
Not production money-ready
Not live-trading ready
```

---

## 23. One-command quick status pack

Run this when asking for help:

```powershell
cd C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3

$out="$HOME\Desktop\System3_Quick_Status.txt"
"=== SYSTEM3 QUICK STATUS ===" | Out-File $out
"Generated=$(Get-Date -Format o)" | Out-File $out -Append
"ROOT=$(git rev-parse --show-toplevel)" | Out-File $out -Append
"BRANCH=$(git branch --show-current)" | Out-File $out -Append
"HEAD=$(git rev-parse HEAD)" | Out-File $out -Append
"STATUS" | Out-File $out -Append
git status --short | Out-File $out -Append
"ENV SAFETY" | Out-File $out -Append
"LIVE_TRADING_ENABLED=$env:LIVE_TRADING_ENABLED" | Out-File $out -Append
"SYSTEM3_LIVE_TRADING_ALLOWED=$env:SYSTEM3_LIVE_TRADING_ALLOWED" | Out-File $out -Append
"ANALYZE_MODE=$env:ANALYZE_MODE" | Out-File $out -Append
"NODE PLAYWRIGHT" | Out-File $out -Append
node -e "import('playwright').then(()=>console.log('PLAYWRIGHT_OK')).catch(e=>console.log('PLAYWRIGHT_FAIL',e.message))" 2>&1 | Out-File $out -Append
"PORTS" | Out-File $out -Append
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 5000,8000,8010,8765,3000,5173 } |
  Select-Object LocalAddress,LocalPort,OwningProcess |
  Format-Table -AutoSize |
  Out-String |
  Out-File $out -Append
"LATEST REPORTS" | Out-File $out -Append
Get-ChildItem reports\latest -Directory -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 20 Name,LastWriteTime |
  Format-Table -AutoSize |
  Out-String |
  Out-File $out -Append
Write-Host "Created: $out"
```

Send `System3_Quick_Status.txt` when exact diagnosis is needed.
