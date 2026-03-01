# Dashboard Inspection Checklist

Use this checklist to verify Console, Elements, Source, and Network when inspecting the React dashboard at http://localhost:3000.

---

## 1. CONSOLE (F12 → Console tab)

### Expected on load
- `API_BASE configured as: http://localhost:8000`
- `Window location: http://localhost:3000/`
- No red errors

### Common errors to fix
| Error | Cause | Fix |
|-------|-------|-----|
| `Failed to fetch` / `Network Error` | Backend not running | Start backend: `uvicorn dashboard.backend.app:app --port 8000` |
| `CORS policy` blocked | Backend CORS misconfigured | Backend uses `allow_origins=["*"]` – verify it's running |
| `Cannot read property of undefined` | Null/undefined access | Check component for optional chaining `?.` |
| `404` for assets | Wrong base path | Vite uses `base: './'` for relative paths |

### Console noise (config.ts)
- **Production**: Set `VITE_DEBUG=0` to suppress API_BASE logs
- **Development**: Logs help verify API_BASE resolution

---

## 2. ELEMENTS (F12 → Elements tab)

### Structure to verify
```
#root
  └── div.min-h-screen (dark/light)
        └── nav (System3 Ultra Dashboard)
        └── main.p-6
              └── ErrorBoundary
                    └── BackendConnectivityBanner
                    └── Routes (Overview, Chain, etc.)
```

### Accessibility
- Nav links: Overview, Chain, Signals, Trading, Alerts, Risk, Charts, ML, Model, Control, Agent
- Select elements in AdvancedCharts: Add `aria-label` if missing
- Buttons: Should have discernible text

### Data attributes
- `data-cursor-element-id` on #root (Cursor IDE)
- No broken `:class` or `v-for` (Vue) – this is React, not Vue

---

## 3. SOURCE (F12 → Sources tab, or View Page Source)

### HTML (index.html)
- `<!doctype html>`
- `<div id="root"></div>` – React mount point
- `<script type="module" src="/src/main.tsx">` – Vite entry

### Loaded scripts
- `main.tsx` → App.tsx → route components
- Chunks: `vendor-react-*.js`, `vendor-charts-*.js`, `vendor-utils-*.js`

### Meta tags
- `charset="UTF-8"`
- `viewport` for mobile
- `title`: System3 Ultra Dashboard

---

## 4. NETWORK (F12 → Network tab)

### Filter: XHR or Fetch

### On Overview load
| Request | Method | Expected | Status |
|---------|--------|----------|--------|
| `/api/health` | GET | 200 | JSON |
| `/api/state` | GET | 200 | JSON |
| `/api/perf` | GET | 200 | JSON |

### Per-tab requests
| Tab | Endpoints |
|-----|-----------|
| Chain | `/api/chain/NIFTY` |
| Signals | `/api/state`, `/api/signal/top`, `/api/qc` |
| Trading | `/api/state`, `/api/pnl` |
| Alerts | `/api/state` or `/api/alerts/recent` |
| Risk | `/api/state`, `/api/risk/check-limits` |
| Charts | `/api/charting/heatmap/NIFTY`, etc. |
| ML | `/api/ml/performance`, `/api/ml/compare` |
| Model | `/api/logs/tail`, `/api/audit/secrets`, `/api/qc` |
| Control | `/api/runner/status`, `/api/learning/status`, etc. |
| Agent | `/api/agent/memory`, `/api/agent/issues` |

### Failure indicators
- **404**: Endpoint not found – check backend routes
- **500**: Server error – check backend logs
- **CORS error**: Backend not allowing origin
- **Pending forever**: Backend not running or timeout

---

## 5. Quick verification script

Run in browser console (F12):

```javascript
// 1. Check API connectivity
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(d => console.log('✅ Backend OK:', d.status))
  .catch(e => console.error('❌ Backend:', e.message));

// 2. Check root mount
console.log('Root mounted:', !!document.getElementById('root')?.children?.length);

// 3. List failed requests (run after page load)
performance.getEntriesByType('resource')
  .filter(r => r.responseStatus >= 400)
  .forEach(r => console.warn('Failed:', r.name, r.responseStatus));
```

---

## 6. Known issues (addressed)

| Issue | Status |
|-------|--------|
| config.ts verbose logs | Optional: use VITE_DEBUG env |
| Select aria-label | AdvancedCharts – 3 selects |
| Empty ML comparison | Bootstrap + EmptyState |
| Chain/Charts no data | Run `populate_demo_data_for_dashboard.ps1` |
