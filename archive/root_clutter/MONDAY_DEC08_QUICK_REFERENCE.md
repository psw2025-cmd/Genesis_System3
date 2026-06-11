# MONDAY DEC 08 - QUICK REFERENCE CARD
**Print this and keep at your desk during market hours**

---

## 🎯 KEY NUMBERS TO REMEMBER

```
APPROVAL RATE: 63.1% (416/659)
DAILY P&L: 600 (0.5% edge assumption)

BY UNDERLYING:
  NIFTY: 100% (208/208) ✅ STRONG
  SENSEX: 97% (112/115) ✅ STRONG
  BANKNIFTY: 67% (96/144) ⚠️ MODERATE
  FINNIFTY: 0% (0/96) ❌ NEEDS FIX
  MIDCPNIFTY: 0% (0/96) ❌ NEEDS FIX

THRESHOLD: 0.12 absolute value
```

---

## 📋 STARTUP SEQUENCE (9:00 AM - 9:30 AM)

```
1️⃣ 9:00 AM:  Verify .env file (LIVE_TRADING_ENABLED=False)
2️⃣ 9:05 AM:  Run heartbeat_maintenance.bat
3️⃣ 9:10 AM:  Run run_premarket_health_check.bat
4️⃣ 9:15 AM:  Check FINNIFTY/MIDCPNIFTY signals (decide threshold)
5️⃣ 9:20 AM:  Run run_phases_301_310_diagnostics.bat
6️⃣ 9:25 AM:  Final verification (models loaded? CSV writable?)
7️⃣ 9:30 AM:  START_AUTORUN_AND_WATCHDOG.bat ← MAIN LAUNCHER
```

---

## 🚨 IF SOMETHING GOES WRONG

### System Freezes (No Watchdog)
```
taskkill /F /IM python.exe
cd C:\Genesis_System3
START_AUTORUN_AND_WATCHDOG.bat
```

### CSV Corrupted
```
copy C:\Genesis_System3\storage\backup\angel_virtual_orders.csv.backup ^
     C:\Genesis_System3\storage\live\angel_virtual_orders.csv
START_AUTORUN_AND_WATCHDOG.bat
```

### Approval Rate Drops < 50%
```
STOP TRADING
Run: run_comprehensive_validation.bat
Check logs for "SCORE_TOO_LOW" patterns
Investigate model drift
```

### Watchdog Not Spawning
```
Manually start: 
  python core/watchdog.py
Or restart full system:
  START_AUTORUN_AND_WATCHDOG.bat
```

---

## ✅ FIRST HOUR CHECKPOINT (10:00 AM)

Look for these signs of healthy operation:

```
✅ Approval rate >= 60% (same as Saturday baseline)
✅ NIFTY approval >= 95%
✅ System3_Watchdog window still open
✅ New orders appearing in angel_virtual_orders.csv every 30-45 sec
✅ No error messages in logs
✅ Heartbeat.json timestamp < 5 min old
```

If ANY red flags appear → Investigate immediately.

---

## 🎯 FINNIFTY/MIDCPNIFTY DECISION TREE

```
First snapshot shows FINNIFTY/MIDCPNIFTY scores?

├─ YES, scores 0.11+:
│  └─ Try lowering threshold to 0.10
│     └─ Monitor 1 hour
│        └─ If working: Keep it
│        └─ If not: Revert to 0.12 + disable
│
└─ NO, all rejections (scores < 0.12):
   └─ DISABLE FINNIFTY/MIDCPNIFTY
      └─ Trade only NIFTY/SENSEX/BANKNIFTY
         └─ Monitor daily P&L (expect ~360-450 instead of 600)
```

---

## 📊 DAILY PROFIT TARGETS

```
Conservative (0.5% per order):
  Daily: 600
  Weekly: 3,000
  Stop-loss: -200 (3 bad days)

Optimistic (1.0% per order):
  Daily: 1,200
  Weekly: 6,000
  Stop-loss: -400

Baseline (December 6 Saturday):
  416 approved orders
  63.1% approval rate
  Compare Monday to this
```

---

## 🚫 DO NOT DO THESE

```
❌ Do NOT enable LIVE_TRADING_ENABLED=True
   (System must stay in DRY-RUN mode)

❌ Do NOT reduce approval threshold below 0.08
   (Too loose, increases noise)

❌ Do NOT ignore FINNIFTY/MIDCPNIFTY failures
   (Decide: adjust or disable by 10:00 AM)

❌ Do NOT manually edit batch files without backup
   (We fixed the issues already)

❌ Do NOT delete CSV files during market hours
   (Archive instead: backup/ folder)
```

---

## 📞 RECOVERY CONTACTS & SCRIPTS

```
QUICK RESTART:        START_AUTORUN_AND_WATCHDOG.bat
DEEP HEALTH CHECK:    run_comprehensive_validation.bat
MODELS REVALIDATE:    run_phases_301_310_diagnostics.bat
SIGNAL ANALYSIS:      run_signal_distribution_analysis.bat
CSV AUDIT:            run_csv_audit.bat
FULL VALIDATION:      system3_full_validation.bat
```

---

## ⏰ TIME ZONES (If Needed)

```
IST (India):  15:30 - 23:00 (3:30 PM - 11:00 PM)
UTC:          09:00 - 17:30 (9:00 AM - 5:30 PM)
EST:          04:00 - 12:30 (4:00 AM - 12:30 PM)
```

---

## 📈 SUCCESS METRICS (Track These)

```
✅ Approval rate >= 60%          (baseline: 63.1%)
✅ NIFTY approval >= 95%         (baseline: 100%)
✅ No critical log errors         (< 10 per hour)
✅ CSV files updated regularly   (every 30-45 sec)
✅ Watchdog uptime >= 99%        (no crashes)
✅ Daily P&L >= 300               (even pessimistic case)
```

---

## 🎪 SHOW-STOPPER ISSUES (Stop Immediately)

```
🔴 Approval rate < 30%           (System malfunction)
🔴 NIFTY approval < 75%          (Major model drift)
🔴 CSV files > 20 min old        (Data pipeline broken)
🔴 Watchdog crashed & won't restart (Process control failed)
🔴 > 5 models missing           (Cannot run)
🔴 Broker connection error       (Can't place orders)
```

---

## 📋 DAILY CHECKLIST

```
□ 9:00 AM:  Pre-market checks
□ 9:30 AM:  START_AUTORUN_AND_WATCHDOG.bat
□ 10:00 AM: First checkpoint (approval rate >= 60%?)
□ 11:00 AM: Monitor FINNIFTY/MIDCPNIFTY (decide threshold)
□ 12:00 PM: Mid-day health check (spot check CSV)
□ 1:00 PM:  Afternoon checkpoint (running smooth?)
□ 2:00 PM:  Pre-close verification (all systems up?)
□ 3:30 PM:  Run post_close_audit.bat
□ 4:00 PM:  Review daily log
```

---

## 🟢 GO/NO-GO DECISION AT 10:00 AM

```
GO CRITERIA:
  ✅ Approval rate >= 60%
  ✅ NIFTY approval >= 95%
  ✅ No critical errors in logs
  ✅ CSV files fresh (< 5 min old)
  ✅ Watchdog stable
  → CONTINUE TRADING

NO-GO CRITERIA:
  ❌ Approval rate < 40%
  ❌ NIFTY approval < 75%
  ❌ Broker connection lost
  ❌ CSV files > 20 min old
  ❌ Watchdog crashed
  → STOP TRADING, INVESTIGATE
```

---

**Print this card. Keep it visible during trading hours.**  
**Reference the full analysis files for detailed explanations.**  
**Questions? Check MONDAY_DEC08_EXECUTIVE_BRIEF.md first.**
