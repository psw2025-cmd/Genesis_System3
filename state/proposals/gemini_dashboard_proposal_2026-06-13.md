# Gemini Dashboard Expansion Proposal — 3 New Tabs
> Date: 2026-06-13 | Agent: Gemini (running as Claude agent per SYSTEM_STATE.md protocol)
> Status: PROPOSAL — requesting Codex cross-verification
> Files investigated: dashboard/index.html (287 lines), dashboard/app.js (334 lines), dashboard/backend/app.py (4025 lines), dashboard/style.css

---

## Problem

Dashboard item #10 in SYSTEM_STATE.md PENDING TASKS:
> "Dashboard: Spearman rho trend chart, gain rank table, datasource health widget, retrain alert banner"

The existing dashboard has 6 tabs (Overview, Latency, Risk, Greeks, Option Chain, Live Trades) but is completely missing:
- Gain Rank predictions table
- Accuracy (Spearman rho) trend
- System Health (token, datasource, scheduler)

---

## Investigation Findings

### Dashboard Architecture (confirmed from code)
- Vue3 via CDN (vue.global.prod.js), no build step needed
- `tabs` array in `setup()` drives the sidebar nav — just append new entries
- `activeTab` ref drives v-if conditionals in the content area
- CSS classes: `metric-card`, `metric-grid`, `panel`, `table-container`, `chain-table`, `tab-content`
- Dark theme: background #0a0a0a, sidebar #1a1a1a, card/panel #1a1a1a, accent #00ff88
- Polling: `updateAll()` runs every 5 seconds via `setInterval`

### State File Schemas (verified with real data)
- `state/gain_rank_history.json`: list of `{date, time, predictions: [{rank, underlying, gain_score, expected_move_pct, recommendation}]}`
- `state/market_validations/market_validation_YYYY-MM-DD.json`: `{date, spearman_correlation OR rank_correlation_spearman, hit_rate, top_n_evaluated, retrain_signal, status, predicted_ranking, actual_ranking}`
- `state/datasource_health.json`: does NOT exist yet (first run at 08:00 IST); endpoint must handle missing file gracefully
- `state/retrain_signal.json`: does NOT currently exist (was cleared after prior retrain cycle); endpoint must use `os.path.exists()`
- `logs/dhan_watchdog.log` last line: `2026-06-13 15:09:55,572 [Watchdog] INFO Token OK — 3.85h remaining`
- `config/system3_job_scheduler.json`: 7 jobs with schedule_time fields

### Key Dual-Key Discovery (Critical)
The `spearman_correlation` field exists in `market_validation_2026-06-12.json` (new schema). However CHANGE_LOG states old files use `rank_correlation_spearman`. The backend endpoint MUST handle both. The JavaScript must also handle both via `val.spearman_correlation ?? val.rank_correlation_spearman`.

---

## Proposed Solution

### Part 1: 3 FastAPI Endpoints (dashboard/backend/app.py additions)

#### Endpoint 1: GET /api/gain_rank
```python
@app.get("/api/gain_rank")
async def get_gain_rank():
    """Today's latest gain rank predictions from state/gain_rank_history.json"""
    try:
        history_file = ROOT_DIR / "state" / "gain_rank_history.json"
        if not history_file.exists():
            return {"date": None, "time": None, "predictions": [], "total_entries": 0}
        
        history = json.loads(history_file.read_text())
        if not history:
            return {"date": None, "time": None, "predictions": [], "total_entries": 0}
        
        # Return the LATEST entry (last in list = most recent run)
        today = datetime.now(IST).strftime("%Y-%m-%d")
        # Filter for today first, else fall back to most recent overall
        today_entries = [e for e in history if e.get("date") == today]
        latest = today_entries[-1] if today_entries else history[-1]
        
        return {
            "date": latest.get("date"),
            "time": latest.get("time"),
            "predictions": latest.get("predictions", []),
            "total_entries": len(history),
            "is_today": latest.get("date") == today
        }
    except Exception as e:
        return {"date": None, "time": None, "predictions": [], "error": str(e)[:200]}
```

#### Endpoint 2: GET /api/accuracy_trend
```python
@app.get("/api/accuracy_trend")
async def get_accuracy_trend():
    """Spearman rho trend from state/market_validations/*.json, plus retrain alert"""
    try:
        validations_dir = ROOT_DIR / "state" / "market_validations"
        retrain_signal_file = ROOT_DIR / "state" / "retrain_signal.json"
        
        retrain_needed = retrain_signal_file.exists()
        
        trend = []
        if validations_dir.exists():
            files = sorted(validations_dir.glob("market_validation_*.json"))
            for f in files[-14:]:  # Last 14 days
                try:
                    val = json.loads(f.read_text())
                    # Handle BOTH old key (rank_correlation_spearman) and new key (spearman_correlation)
                    rho = val.get("spearman_correlation") or val.get("rank_correlation_spearman")
                    trend.append({
                        "date": val.get("date"),
                        "spearman_rho": rho,
                        "hit_rate": val.get("hit_rate"),
                        "status": val.get("status"),
                        "retrain_signal": val.get("retrain_signal", False),
                        "top_n_evaluated": val.get("top_n_evaluated")
                    })
                except Exception:
                    continue
        
        latest_rho = trend[-1]["spearman_rho"] if trend else None
        avg_rho = round(sum(t["spearman_rho"] for t in trend if t["spearman_rho"] is not None) / len(trend), 4) if trend else None
        
        return {
            "trend": trend,
            "retrain_needed": retrain_needed,
            "latest_rho": latest_rho,
            "avg_rho": avg_rho,
            "total_validations": len(trend)
        }
    except Exception as e:
        return {"trend": [], "retrain_needed": False, "latest_rho": None, "avg_rho": None, "error": str(e)[:200]}
```

#### Endpoint 3: GET /api/system_health
```python
@app.get("/api/system_health")
async def get_system_health():
    """System health: datasource, token watchdog, job scheduler status"""
    try:
        result = {}
        
        # 1. Datasource health (may not exist — first run at 08:00 IST)
        ds_health_file = ROOT_DIR / "state" / "datasource_health.json"
        if ds_health_file.exists():
            result["datasource"] = json.loads(ds_health_file.read_text())
        else:
            result["datasource"] = {"status": "not_run_yet", "message": "Health check runs daily at 08:00 IST"}
        
        # 2. Token watchdog status — read last line of logs/dhan_watchdog.log
        watchdog_log = ROOT_DIR / "logs" / "dhan_watchdog.log"
        result["token"] = {"status": "unknown", "last_line": None}
        if watchdog_log.exists():
            try:
                # Read last line efficiently
                with open(watchdog_log, "rb") as f:
                    f.seek(-2, 2)
                    while f.read(1) != b"\n":
                        f.seek(-2, 1)
                    last_line = f.readline().decode("utf-8", errors="replace").strip()
                result["token"]["last_line"] = last_line
                # Parse status from last line
                if "Token OK" in last_line:
                    result["token"]["status"] = "OK"
                    # Extract remaining time if present: "Token OK — 3.85h remaining"
                    import re
                    match = re.search(r"(\d+\.?\d*)h remaining", last_line)
                    if match:
                        result["token"]["hours_remaining"] = float(match.group(1))
                elif "REFRESH" in last_line.upper() or "RENEW" in last_line.upper():
                    result["token"]["status"] = "REFRESHING"
                elif "ERROR" in last_line.upper() or "FAIL" in last_line.upper():
                    result["token"]["status"] = "ERROR"
            except Exception as ex:
                result["token"]["error"] = str(ex)[:100]
        
        # 3. Job scheduler config and status
        scheduler_cfg = ROOT_DIR / "config" / "system3_job_scheduler.json"
        result["scheduler"] = {"jobs": [], "total_jobs": 0}
        if scheduler_cfg.exists():
            cfg = json.loads(scheduler_cfg.read_text())
            jobs = cfg.get("jobs", [])
            result["scheduler"]["total_jobs"] = len(jobs)
            result["scheduler"]["enabled_jobs"] = sum(1 for j in jobs if j.get("enabled", True))
            result["scheduler"]["jobs"] = [
                {
                    "id": j.get("id"),
                    "name": j.get("name"),
                    "schedule_time": j.get("schedule_time"),
                    "enabled": j.get("enabled", True),
                    "weekdays_only": j.get("weekdays_only", False)
                }
                for j in jobs
            ]
        
        return result
    except Exception as e:
        return {"datasource": {}, "token": {}, "scheduler": {}, "error": str(e)[:200]}
```

---

### Part 2: Vue3 Template HTML (additions to dashboard/index.html)

Add these 3 blocks INSIDE the `<div class="content">` element, after the Live Trades tab block (after line 280, before `</div></div>`):

```html
                <!-- Gain Rank Tab -->
                <div v-if="activeTab === 'gainrank'" class="tab-content">
                    <h2>Gain Rank — Today's Predictions</h2>
                    
                    <div v-if="gainRankData.predictions && gainRankData.predictions.length > 0">
                        <!-- Run metadata -->
                        <div class="metric-grid">
                            <div class="metric-card green">
                                <div class="metric-label">Run Date</div>
                                <div class="metric-value">{{ gainRankData.date || 'N/A' }}</div>
                                <div class="metric-change">{{ gainRankData.is_today ? 'TODAY' : 'PREV SESSION' }}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Run Time</div>
                                <div class="metric-value">{{ gainRankData.time || 'N/A' }}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Ranked Underlyings</div>
                                <div class="metric-value">{{ gainRankData.predictions.length }}</div>
                            </div>
                            <div class="metric-card" :class="getTopRecClass(gainRankData.predictions[0])">
                                <div class="metric-label">Top Pick</div>
                                <div class="metric-value">{{ gainRankData.predictions[0]?.underlying || 'N/A' }}</div>
                                <div class="metric-change">Score: {{ gainRankData.predictions[0]?.gain_score?.toFixed(2) || 'N/A' }}</div>
                            </div>
                        </div>

                        <!-- Predictions table -->
                        <div class="panel">
                            <h3>Predicted Rankings</h3>
                            <div class="table-container">
                                <table class="chain-table">
                                    <thead>
                                        <tr>
                                            <th>Rank</th>
                                            <th>Underlying</th>
                                            <th>Gain Score</th>
                                            <th>Expected Move %</th>
                                            <th>Recommendation</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="pred in gainRankData.predictions" :key="pred.rank">
                                            <td>{{ pred.rank }}</td>
                                            <td>{{ pred.underlying }}</td>
                                            <td>{{ pred.gain_score?.toFixed(2) }}</td>
                                            <td>{{ (pred.expected_move_pct * 100).toFixed(3) }}%</td>
                                            <td :class="pred.recommendation === 'TRADE' ? 'green' : 'yellow'">
                                                {{ pred.recommendation }}
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <div v-else class="panel">
                        <p style="color:#888; padding: 20px;">No gain rank data available. Run: <code>python scripts/daily_gain_rank_and_validate.py --mode rank</code></p>
                    </div>
                </div>

                <!-- Accuracy Tab -->
                <div v-if="activeTab === 'accuracy'" class="tab-content">
                    <h2>Model Accuracy — Spearman rho Trend</h2>
                    
                    <!-- Retrain alert banner -->
                    <div v-if="accuracyData.retrain_needed" class="alert-banner retrain-alert">
                        RETRAIN NEEDED — state/retrain_signal.json exists. Run: <code>python scripts/auto_retrain.py</code>
                    </div>
                    
                    <!-- Summary metrics -->
                    <div class="metric-grid">
                        <div class="metric-card" :class="getRhoClass(accuracyData.latest_rho)">
                            <div class="metric-label">Latest Spearman rho</div>
                            <div class="metric-value">{{ accuracyData.latest_rho !== null ? accuracyData.latest_rho?.toFixed(4) : 'N/A' }}</div>
                            <div class="metric-change">Target: &gt;= 0.70</div>
                        </div>
                        <div class="metric-card" :class="getRhoClass(accuracyData.avg_rho)">
                            <div class="metric-label">14-Day Avg rho</div>
                            <div class="metric-value">{{ accuracyData.avg_rho !== null ? accuracyData.avg_rho?.toFixed(4) : 'N/A' }}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Validations</div>
                            <div class="metric-value">{{ accuracyData.total_validations || 0 }}</div>
                        </div>
                        <div class="metric-card" :class="accuracyData.retrain_needed ? 'red' : 'green'">
                            <div class="metric-label">Retrain Signal</div>
                            <div class="metric-value">{{ accuracyData.retrain_needed ? 'NEEDED' : 'CLEAR' }}</div>
                        </div>
                    </div>
                    
                    <!-- Trend table -->
                    <div class="panel">
                        <h3>Daily Validation History</h3>
                        <div v-if="accuracyData.trend && accuracyData.trend.length > 0" class="table-container">
                            <table class="chain-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Spearman rho</th>
                                        <th>Hit Rate</th>
                                        <th>Top N</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="entry in accuracyData.trend.slice().reverse()" :key="entry.date">
                                        <td>{{ entry.date }}</td>
                                        <td :class="getRhoClass(entry.spearman_rho)">
                                            {{ entry.spearman_rho !== null ? entry.spearman_rho?.toFixed(4) : 'N/A' }}
                                        </td>
                                        <td>{{ entry.hit_rate !== null ? (entry.hit_rate * 100).toFixed(1) + '%' : 'N/A' }}</td>
                                        <td>{{ entry.top_n_evaluated ?? 'N/A' }}</td>
                                        <td :class="entry.status === 'RETRAIN_NEEDED' ? 'red' : 'green'">
                                            {{ entry.status || 'OK' }}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div v-else style="color:#888; padding: 20px;">
                            No validation data yet. Run: <code>python scripts/daily_gain_rank_and_validate.py --mode validate</code>
                        </div>
                    </div>
                </div>

                <!-- System Health Tab -->
                <div v-if="activeTab === 'syshealth'" class="tab-content">
                    <h2>System Health</h2>
                    
                    <div class="metric-grid">
                        <!-- Token status card -->
                        <div class="metric-card" :class="getTokenClass(systemHealth.token)">
                            <div class="metric-label">Dhan Token</div>
                            <div class="metric-value">{{ systemHealth.token?.status || 'UNKNOWN' }}</div>
                            <div class="metric-change" v-if="systemHealth.token?.hours_remaining">
                                {{ systemHealth.token.hours_remaining?.toFixed(2) }}h remaining
                            </div>
                        </div>
                        <!-- Datasource status card -->
                        <div class="metric-card" :class="getDsClass(systemHealth.datasource)">
                            <div class="metric-label">Data Sources</div>
                            <div class="metric-value">{{ systemHealth.datasource?.overall_status || systemHealth.datasource?.status || 'NOT RUN' }}</div>
                        </div>
                        <!-- Scheduler card -->
                        <div class="metric-card green">
                            <div class="metric-label">Scheduled Jobs</div>
                            <div class="metric-value">{{ systemHealth.scheduler?.enabled_jobs || 0 }} / {{ systemHealth.scheduler?.total_jobs || 0 }}</div>
                            <div class="metric-change">enabled</div>
                        </div>
                        <!-- Overall health -->
                        <div class="metric-card" :class="getOverallHealthClass()">
                            <div class="metric-label">Overall Health</div>
                            <div class="metric-value">{{ getOverallHealthLabel() }}</div>
                        </div>
                    </div>
                    
                    <!-- Token detail panel -->
                    <div class="panel">
                        <h3>Token / Watchdog Status</h3>
                        <div class="status-grid">
                            <div class="status-item">
                                <span class="status-label">Status:</span>
                                <span class="status-value" :class="systemHealth.token?.status === 'OK' ? 'green' : 'red'">
                                    {{ systemHealth.token?.status || 'UNKNOWN' }}
                                </span>
                            </div>
                            <div class="status-item">
                                <span class="status-label">Hours Remaining:</span>
                                <span class="status-value">{{ systemHealth.token?.hours_remaining?.toFixed(2) || 'N/A' }}</span>
                            </div>
                            <div class="status-item">
                                <span class="status-label">Watchdog Last Log:</span>
                                <span class="status-value watchdog-log">{{ systemHealth.token?.last_line || 'N/A' }}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Datasource health panel -->
                    <div class="panel">
                        <h3>Data Source Health</h3>
                        <div v-if="systemHealth.datasource?.status === 'not_run_yet' || !systemHealth.datasource?.sources">
                            <p style="color:#888; padding: 10px;">{{ systemHealth.datasource?.message || 'Health check runs daily at 08:00 IST. No data yet.' }}</p>
                        </div>
                        <div v-else class="table-container">
                            <table class="chain-table">
                                <thead>
                                    <tr>
                                        <th>Priority</th>
                                        <th>Source</th>
                                        <th>Status</th>
                                        <th>Latency (ms)</th>
                                        <th>Note</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(src, idx) in systemHealth.datasource.sources" :key="idx">
                                        <td>P{{ idx }}</td>
                                        <td>{{ src.name }}</td>
                                        <td :class="src.status === 'OK' ? 'green' : 'red'">{{ src.status }}</td>
                                        <td>{{ src.latency_ms !== undefined ? src.latency_ms : 'N/A' }}</td>
                                        <td>{{ src.note || '' }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Job scheduler panel -->
                    <div class="panel">
                        <h3>Job Scheduler ({{ systemHealth.scheduler?.enabled_jobs }}/{{ systemHealth.scheduler?.total_jobs }} enabled)</h3>
                        <div class="table-container">
                            <table class="chain-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Schedule (IST)</th>
                                        <th>Weekdays Only</th>
                                        <th>Enabled</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="job in systemHealth.scheduler?.jobs || []" :key="job.id">
                                        <td>{{ job.id }}</td>
                                        <td>{{ job.name }}</td>
                                        <td>{{ job.schedule_time || 'anytime' }}</td>
                                        <td>{{ job.weekdays_only ? 'Yes' : 'No' }}</td>
                                        <td :class="job.enabled ? 'green' : 'red'">{{ job.enabled ? 'YES' : 'NO' }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
```

---

### Part 3: JavaScript additions to dashboard/app.js

#### 3a. Add 3 new tabs to the `tabs` array (append after existing 6 entries):

```javascript
{ id: 'gainrank', label: 'Gain Rank', icon: '🏆' },
{ id: 'accuracy', label: 'Accuracy', icon: '📐' },
{ id: 'syshealth', label: 'System Health', icon: '🖥️' },
```

#### 3b. Add new reactive refs (after `const liveTrades = ref([]);`):

```javascript
const gainRankData = ref({ date: null, time: null, predictions: [], total_entries: 0, is_today: false });
const accuracyData = ref({ trend: [], retrain_needed: false, latest_rho: null, avg_rho: null, total_validations: 0 });
const systemHealth = ref({ datasource: {}, token: {}, scheduler: { jobs: [], total_jobs: 0, enabled_jobs: 0 } });
```

#### 3c. Add 3 new fetch functions (after `fetchGreeksStatus`):

```javascript
const fetchGainRank = async () => {
    try {
        const response = await fetch(`${API_BASE}/api/gain_rank`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        gainRankData.value = data;
    } catch (error) {
        console.error('Error fetching gain rank:', error);
    }
};

const fetchAccuracyTrend = async () => {
    try {
        const response = await fetch(`${API_BASE}/api/accuracy_trend`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        accuracyData.value = data;
    } catch (error) {
        console.error('Error fetching accuracy trend:', error);
    }
};

const fetchSystemHealth = async () => {
    try {
        const response = await fetch(`${API_BASE}/api/system_health`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        systemHealth.value = data;
    } catch (error) {
        console.error('Error fetching system health:', error);
    }
};
```

#### 3d. Add 4 new helper methods (after `getRiskClass`):

```javascript
const getRhoClass = (rho) => {
    if (rho === null || rho === undefined) return '';
    if (rho >= 0.70) return 'green';
    if (rho >= 0.40) return 'yellow';
    return 'red';
};

const getTopRecClass = (pred) => {
    if (!pred) return '';
    return pred.recommendation === 'TRADE' ? 'green' : 'yellow';
};

const getTokenClass = (tokenInfo) => {
    if (!tokenInfo) return '';
    if (tokenInfo.status === 'OK') return 'green';
    if (tokenInfo.status === 'REFRESHING') return 'yellow';
    return 'red';
};

const getDsClass = (dsInfo) => {
    if (!dsInfo) return '';
    const status = (dsInfo.overall_status || dsInfo.status || '').toUpperCase();
    if (status === 'OK' || status === 'HEALTHY') return 'green';
    if (status === 'DEGRADED' || status === 'LOW') return 'yellow';
    if (status === 'NOT_RUN_YET' || status === 'NOT RUN') return '';
    return 'red';
};

const getOverallHealthClass = () => {
    const tokenOk = systemHealth.value.token?.status === 'OK';
    const dsOk = systemHealth.value.datasource?.status !== 'CRITICAL';
    if (tokenOk && dsOk) return 'green';
    if (tokenOk || dsOk) return 'yellow';
    return 'red';
};

const getOverallHealthLabel = () => {
    const tokenOk = systemHealth.value.token?.status === 'OK';
    const dsOk = systemHealth.value.datasource?.status !== 'CRITICAL';
    if (tokenOk && dsOk) return 'HEALTHY';
    if (!tokenOk) return 'TOKEN ISSUE';
    return 'DATA ISSUE';
};
```

#### 3e. Update `updateAll()` to include new fetches (and tab-aware polling):

Replace the `updateAll` function body to add:
```javascript
// Inside the try block in updateAll, add:
await Promise.all([
    fetchHealth(),
    fetchPerformance(),
    fetchPnL(),
    fetchPositions(),
    fetchGainRank(),        // ADD
    fetchAccuracyTrend(),   // ADD
    fetchSystemHealth()     // ADD (lightweight file reads, safe to poll)
]);
```

Also extend the tab-change watcher inside `onMounted`:
```javascript
Vue.watch(() => activeTab.value, async (newTab) => {
    if (newTab === 'options' || newTab === 'greeks') {
        await fetchChainData(selectedUnderlying.value);
    }
    // Refresh new tabs on switch for freshest data
    if (newTab === 'gainrank') await fetchGainRank();
    if (newTab === 'accuracy') await fetchAccuracyTrend();
    if (newTab === 'syshealth') await fetchSystemHealth();
});
```

#### 3f. Add new refs and functions to the `return` block:

```javascript
// Add to return {...}:
gainRankData,
accuracyData,
systemHealth,
fetchGainRank,
fetchAccuracyTrend,
fetchSystemHealth,
getRhoClass,
getTopRecClass,
getTokenClass,
getDsClass,
getOverallHealthClass,
getOverallHealthLabel,
```

---

### Part 4: CSS Additions (dashboard/style.css)

Add these rules at the end of style.css:

```css
/* Retrain alert banner */
.alert-banner {
    padding: 12px 20px;
    margin-bottom: 20px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 14px;
}

.retrain-alert {
    background: rgba(255, 68, 68, 0.15);
    border: 1px solid #ff4444;
    color: #ff8888;
}

/* Watchdog log line — monospace for readability */
.watchdog-log {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #aaa;
    word-break: break-all;
}
```

---

## Existing CSS Classes Used (no changes needed)

| Class | Usage |
|---|---|
| `tab-content` | Outer wrapper for each tab pane |
| `metric-grid` | 4-column grid of metric cards |
| `metric-card` | Individual KPI card |
| `metric-card.green` | Green-highlighted card |
| `metric-card.yellow` | Yellow-highlighted card |
| `metric-card.red` | Red-highlighted card |
| `metric-label` | Label row inside metric-card |
| `metric-value` | Primary value row inside metric-card |
| `metric-change` | Secondary/change row inside metric-card |
| `panel` | Content panel with subtle border |
| `table-container` | Scroll wrapper for tables |
| `chain-table` | Styled data table (thead + tbody) |
| `status-grid` | Grid for status key:value pairs |
| `status-item`, `.status-label`, `.status-value` | Status row pattern |
| `green`, `yellow`, `red` | Inline color utility classes on `<td>` or `<span>` |

---

## Risk Assessment

| Risk | Mitigation |
|---|---|
| `state/datasource_health.json` missing | Endpoint returns `{"status": "not_run_yet"}`, frontend shows graceful message |
| `state/retrain_signal.json` missing | `os.path.exists()` check, `retrain_needed=False` default |
| Old vs new `spearman_correlation` key | Backend reads both: `val.get("spearman_correlation") or val.get("rank_correlation_spearman")` |
| Watchdog log empty or unreadable | Try/except around file seek, fallback to `{"status": "unknown"}` |
| Tab addition breaking existing tabs | All changes are purely additive (new v-if blocks, new tab entries appended) |

---

## Success Metrics

1. Gain Rank tab shows today's latest predicted ranking table with score, move %, recommendation
2. Accuracy tab shows Spearman rho trend table for all available validation days; red RETRAIN banner appears when `retrain_signal.json` exists
3. System Health tab shows token status with hours remaining (from watchdog log), datasource health (or "not run yet"), all 7 scheduler jobs with times
4. All 3 endpoints return 200 with empty/fallback data when state files are missing (no 500 errors)
5. No changes to existing 6 tabs — purely additive

---

## Implementation Order (for Codex)

1. Add 3 endpoints to `dashboard/backend/app.py` (at the end, before WebSocket section ~line 516)
2. Add CSS rules to `dashboard/style.css`
3. Add tab entries + refs + fetch functions + helpers to `dashboard/app.js`
4. Add 3 new tab HTML blocks to `dashboard/index.html` (inside content div, after line 280)
5. Verify: `curl http://localhost:8000/api/gain_rank` returns predictions list
6. Verify: `curl http://localhost:8000/api/accuracy_trend` returns trend with spearman_rho
7. Verify: `curl http://localhost:8000/api/system_health` returns token+datasource+scheduler
