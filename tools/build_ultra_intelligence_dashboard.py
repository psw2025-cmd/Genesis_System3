import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "reports" / "model_benchmark_dashboard"
OUT.mkdir(parents=True, exist_ok=True)

leaderboard_json = OUT / "model_benchmark_leaderboard.json"
data = {}
if leaderboard_json.exists():
    try:
        data = json.loads(leaderboard_json.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        data = {}

generated_at = datetime.now(timezone.utc).isoformat()

artifacts = data.get("model_artifacts", [])
training_profile = data.get("training_profile", {})
readiness = data.get("readiness", {})
score = readiness.get("percent", 0)

model_rows = []
for a in artifacts:
    u = a.get("underlying", "UNKNOWN")
    acc = a.get("test_accuracy")
    train = a.get("train_samples")
    test = a.get("test_samples")
    feats = a.get("features_count")
    ok = a.get("artifact_pair_ok")
    model_rows.append(
        {
            "underlying": u,
            "accuracy": acc if isinstance(acc, (int, float)) else None,
            "train": train,
            "test": test,
            "features": feats,
            "artifact_ok": bool(ok),
            "risk": "HIGH" if training_profile.get("rows_scanned", 0) == 0 else "MEDIUM",
        }
    )

payload = {
    "generated_at": generated_at,
    "readiness_score": score,
    "training_rows": training_profile.get("rows_scanned", 0),
    "underlying_count": len(training_profile.get("underlyings", {})),
    "label_count": len(training_profile.get("labels", {})),
    "artifact_pairs": sum(1 for x in model_rows if x["artifact_ok"]),
    "models": model_rows,
    "truth_gates": [
        {"name": "Training data present", "status": training_profile.get("rows_scanned", 0) > 0},
        {"name": "Underlying diversity", "status": len(training_profile.get("underlyings", {})) >= 2},
        {"name": "Label diversity", "status": len(training_profile.get("labels", {})) >= 2},
        {"name": "Model artifact pairs", "status": sum(1 for x in model_rows if x["artifact_ok"]) >= 5},
        {"name": "Walk-forward validation", "status": False},
        {"name": "Cost/slippage P&L", "status": False},
        {"name": "Live option-chain tracking", "status": False},
        {"name": "Promotion gate", "status": False},
    ],
}

json_blob = json.dumps(payload, indent=2)

html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>System3 Ultra Intelligence Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg:#030712;
  --panel:#07111f;
  --panel2:#0b1220;
  --border:#1f3b57;
  --text:#e5f2ff;
  --muted:#8aa4bd;
  --cyan:#22d3ee;
  --blue:#3b82f6;
  --green:#22c55e;
  --red:#ef4444;
  --amber:#f59e0b;
  --violet:#8b5cf6;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0;
  font-family:Inter,Segoe UI,Arial,sans-serif;
  background:
    radial-gradient(circle at 20% 0%, rgba(34,211,238,.16), transparent 30%),
    radial-gradient(circle at 80% 10%, rgba(139,92,246,.18), transparent 30%),
    linear-gradient(180deg, #020617 0%, #030712 100%);
  color:var(--text);
}}
.wrap {{ max-width:1600px; margin:auto; padding:22px; }}
.hero {{
  border:1px solid var(--border);
  background:linear-gradient(135deg, rgba(2,6,23,.92), rgba(15,23,42,.88));
  border-radius:28px;
  padding:26px;
  box-shadow:0 28px 90px rgba(0,0,0,.45);
  position:relative;
  overflow:hidden;
}}
.hero:after {{
  content:"";
  position:absolute;
  inset:-80px;
  background:conic-gradient(from 180deg, transparent, rgba(34,211,238,.12), transparent, rgba(139,92,246,.12), transparent);
  animation:spin 18s linear infinite;
  pointer-events:none;
}}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}
.hero-content {{ position:relative; z-index:2; }}
h1 {{ margin:0; font-size:42px; letter-spacing:-.03em; }}
.subtitle {{ color:var(--muted); margin-top:8px; font-size:15px; }}
.pill {{
  display:inline-flex; gap:8px; align-items:center;
  padding:8px 12px; border-radius:999px;
  border:1px solid rgba(34,211,238,.35);
  background:rgba(34,211,238,.08);
  color:#a5f3fc; font-weight:700; font-size:12px;
  margin-top:14px;
}}
.grid {{ display:grid; gap:16px; }}
.kpis {{ grid-template-columns:repeat(6,1fr); margin-top:20px; }}
.card {{
  border:1px solid var(--border);
  background:linear-gradient(180deg, rgba(15,23,42,.92), rgba(2,6,23,.92));
  border-radius:22px;
  padding:18px;
  box-shadow:0 16px 45px rgba(0,0,0,.25);
}}
.metric {{ font-size:32px; font-weight:900; letter-spacing:-.03em; }}
.label {{ color:var(--muted); font-size:12px; margin-top:7px; }}
.main {{ grid-template-columns:1.25fr .9fr .85fr; margin-top:16px; align-items:stretch; }}
.section-title {{ display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:12px; }}
.section-title h2 {{ margin:0; font-size:18px; }}
.badge {{ display:inline-flex; align-items:center; padding:5px 9px; border-radius:999px; font-size:11px; font-weight:900; }}
.pass {{ background:rgba(34,197,94,.14); color:#86efac; border:1px solid rgba(34,197,94,.35); }}
.fail {{ background:rgba(239,68,68,.14); color:#fca5a5; border:1px solid rgba(239,68,68,.35); }}
.warn {{ background:rgba(245,158,11,.14); color:#fcd34d; border:1px solid rgba(245,158,11,.35); }}
canvas {{ width:100%; height:260px; background:rgba(2,6,23,.35); border-radius:18px; border:1px solid rgba(148,163,184,.12); }}
table {{ width:100%; border-collapse:collapse; }}
th,td {{ padding:10px 8px; border-bottom:1px solid rgba(148,163,184,.13); text-align:left; font-size:13px; }}
th {{ color:#93c5fd; font-size:12px; text-transform:uppercase; letter-spacing:.06em; }}
.small {{ font-size:12px; color:var(--muted); }}
.modules {{ grid-template-columns:repeat(4,1fr); margin-top:16px; }}
.module {{
  min-height:150px;
  position:relative;
  overflow:hidden;
}}
.module h3 {{ margin:0 0 10px; font-size:15px; }}
.module p {{ color:var(--muted); font-size:12px; line-height:1.55; }}
.module:before {{
  content:"";
  position:absolute;
  inset:auto -20px -30px auto;
  width:110px; height:110px; border-radius:50%;
  background:rgba(34,211,238,.08);
}}
.heatmap {{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }}
.heat {{
  border-radius:14px; padding:12px 8px;
  background:linear-gradient(135deg, rgba(59,130,246,.18), rgba(139,92,246,.12));
  border:1px solid rgba(59,130,246,.22);
  min-height:70px;
}}
.truth-list {{ display:flex; flex-direction:column; gap:8px; }}
.truth-item {{ display:flex; justify-content:space-between; gap:8px; padding:9px; border-radius:14px; background:rgba(15,23,42,.7); border:1px solid rgba(148,163,184,.12); }}
@media(max-width:1200px) {{
  .kpis {{ grid-template-columns:repeat(3,1fr); }}
  .main,.modules {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <div class="hero-content">
      <h1>System3 Ultra Intelligence Dashboard</h1>
      <div class="subtitle">Future-proof benchmark cockpit for options AI, model readiness, truth gates, and promotion control.</div>
      <div class="pill">TRUTH-FIRST MODE · ANALYZER/PAPER SAFE · NO LIVE TRADE CHANGE</div>
      <div class="grid kpis">
        <div class="card"><div class="metric" id="kpiReadiness">--</div><div class="label">Benchmark readiness</div></div>
        <div class="card"><div class="metric" id="kpiRows">--</div><div class="label">Training rows proven</div></div>
        <div class="card"><div class="metric" id="kpiArtifacts">--</div><div class="label">Artifact pairs</div></div>
        <div class="card"><div class="metric" id="kpiUnderlyings">--</div><div class="label">Training underlyings</div></div>
        <div class="card"><div class="metric" id="kpiLabels">--</div><div class="label">Label classes</div></div>
        <div class="card"><div class="metric" id="kpiGates">--</div><div class="label">Truth gates passed</div></div>
      </div>
    </div>
  </div>

  <div class="grid main">
    <div class="card">
      <div class="section-title"><h2>Model Accuracy Leaderboard</h2><span class="badge warn">metadata only</span></div>
      <canvas id="accuracyChart" width="800" height="300"></canvas>
      <div class="small">Shows saved test accuracy metadata. Walk-forward validation still required before promotion.</div>
    </div>

    <div class="card">
      <div class="section-title"><h2>Truth Gate Radar</h2><span class="badge fail">not promotion-ready</span></div>
      <canvas id="radarChart" width="600" height="300"></canvas>
    </div>

    <div class="card">
      <div class="section-title"><h2>Option Chain Intelligence Shell</h2><span class="badge fail">live data not connected</span></div>
      <div class="heatmap" id="heatmap"></div>
      <div class="small" style="margin-top:10px;">Future module: CE/PE OI, IV rank, GEX, spread, liquidity, gamma risk, expiry pressure.</div>
    </div>
  </div>

  <div class="grid modules">
    <div class="card module">
      <h3>Walk-Forward Validation</h3>
      <p>Compares model families across rolling time windows. Prevents overfitting and fake static accuracy.</p>
      <span class="badge fail">NOT IMPLEMENTED</span>
    </div>
    <div class="card module">
      <h3>Cost + Slippage P&L Proof</h3>
      <p>Scores models after brokerage, spread, slippage, liquidity, and entry/exit delay.</p>
      <span class="badge fail">NOT IMPLEMENTED</span>
    </div>
    <div class="card module">
      <h3>Live Market Signal Quality</h3>
      <p>Future live/analyzer layer: option-chain movement, IV expansion, OI shift, breadth, and regime alignment.</p>
      <span class="badge fail">NOT CONNECTED</span>
    </div>
    <div class="card module">
      <h3>Promotion Gate</h3>
      <p>Blocks model promotion unless benchmark, P&L, drift, and dashboard truth are all proven.</p>
      <span class="badge fail">NOT IMPLEMENTED</span>
    </div>
  </div>

  <div class="grid main">
    <div class="card" style="grid-column:span 2;">
      <div class="section-title"><h2>Model Artifact Table</h2><span class="badge pass">artifact proof</span></div>
      <table id="modelTable">
        <thead><tr><th>Underlying</th><th>Accuracy</th><th>Train</th><th>Test</th><th>Features</th><th>Risk</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="card">
      <div class="section-title"><h2>Truth Gates</h2><span class="badge warn">evidence map</span></div>
      <div class="truth-list" id="truthList"></div>
    </div>
  </div>
</div>

<script>
const DATA = {json_blob};

function setText(id, value) {{ document.getElementById(id).textContent = value; }}

function initKPIs() {{
  setText("kpiReadiness", DATA.readiness_score + "%");
  setText("kpiRows", DATA.training_rows);
  setText("kpiArtifacts", DATA.artifact_pairs + "/5");
  setText("kpiUnderlyings", DATA.underlying_count);
  setText("kpiLabels", DATA.label_count);
  const passed = DATA.truth_gates.filter(g => g.status).length;
  setText("kpiGates", passed + "/" + DATA.truth_gates.length);
}}

function drawBars() {{
  const canvas = document.getElementById("accuracyChart");
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle = "#07111f"; ctx.fillRect(0,0,w,h);
  const models = DATA.models || [];
  const max = 1.0;
  const gap = 22;
  const barW = (w - 80 - gap*(models.length-1)) / Math.max(models.length,1);
  models.forEach((m,i) => {{
    const acc = m.accuracy || 0;
    const x = 45 + i*(barW+gap);
    const bh = (h-80) * (acc/max);
    const y = h-42-bh;
    const grad = ctx.createLinearGradient(0,y,0,h);
    grad.addColorStop(0,"#22d3ee");
    grad.addColorStop(1,"#2563eb");
    ctx.fillStyle = grad;
    ctx.fillRect(x,y,barW,bh);
    ctx.fillStyle = "#e5f2ff";
    ctx.font = "bold 14px Arial";
    ctx.fillText((acc*100).toFixed(1)+"%", x, y-8);
    ctx.save();
    ctx.translate(x+barW/2, h-20);
    ctx.rotate(-0.35);
    ctx.textAlign="center";
    ctx.fillStyle="#8aa4bd";
    ctx.font="12px Arial";
    ctx.fillText(m.underlying, 0, 0);
    ctx.restore();
  }});
}}

function drawRadar() {{
  const canvas = document.getElementById("radarChart");
  const ctx = canvas.getContext("2d");
  const w = canvas.width, h = canvas.height;
  const cx = w/2, cy = h/2+10, r = Math.min(w,h)*0.34;
  const gates = DATA.truth_gates || [];
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#07111f"; ctx.fillRect(0,0,w,h);
  for(let ring=1; ring<=4; ring++) {{
    ctx.beginPath();
    gates.forEach((g,i)=> {{
      const a = -Math.PI/2 + i*2*Math.PI/gates.length;
      const rr = r*ring/4;
      const x = cx + Math.cos(a)*rr;
      const y = cy + Math.sin(a)*rr;
      i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    }});
    ctx.closePath();
    ctx.strokeStyle="rgba(148,163,184,.18)";
    ctx.stroke();
  }}
  ctx.beginPath();
  gates.forEach((g,i)=> {{
    const a = -Math.PI/2 + i*2*Math.PI/gates.length;
    const rr = g.status ? r : r*0.18;
    const x = cx + Math.cos(a)*rr;
    const y = cy + Math.sin(a)*rr;
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  }});
  ctx.closePath();
  ctx.fillStyle="rgba(34,211,238,.20)";
  ctx.fill();
  ctx.strokeStyle="#22d3ee";
  ctx.lineWidth=2;
  ctx.stroke();
  gates.forEach((g,i)=> {{
    const a = -Math.PI/2 + i*2*Math.PI/gates.length;
    const x = cx + Math.cos(a)*(r+30);
    const y = cy + Math.sin(a)*(r+30);
    ctx.fillStyle = g.status ? "#86efac" : "#fca5a5";
    ctx.font="11px Arial";
    ctx.textAlign = x < cx ? "right" : "left";
    ctx.fillText(g.name.split(" ").slice(0,2).join(" "), x, y);
  }});
}}

function fillHeatmap() {{
  const el = document.getElementById("heatmap");
  const items = ["OI Shift","IV Rank","GEX","Spread","Liquidity","Expiry","Trend","Momentum","Regime","Risk"];
  el.innerHTML = items.map((x,i)=>`<div class="heat"><b>${{x}}</b><br><span class="small">not connected</span></div>`).join("");
}}

function fillTable() {{
  const body = document.querySelector("#modelTable tbody");
  body.innerHTML = (DATA.models||[]).map(m => `
    <tr>
      <td><b>${{m.underlying}}</b></td>
      <td>${{m.accuracy === null ? "N/A" : (m.accuracy*100).toFixed(2)+"%"}}</td>
      <td>${{m.train ?? "N/A"}}</td>
      <td>${{m.test ?? "N/A"}}</td>
      <td>${{m.features ?? "N/A"}}</td>
      <td><span class="badge fail">${{m.risk}}</span></td>
    </tr>
  `).join("");
}}

function fillGates() {{
  const el = document.getElementById("truthList");
  el.innerHTML = (DATA.truth_gates||[]).map(g => `
    <div class="truth-item">
      <span>${{g.name}}</span>
      <span class="badge ${{g.status ? "pass" : "fail"}}">${{g.status ? "PASS" : "NOT PROVEN"}}</span>
    </div>
  `).join("");
}}

initKPIs();
drawBars();
drawRadar();
fillHeatmap();
fillTable();
fillGates();
</script>
</body>
</html>
"""

(OUT / "ultra.html").write_text(html_doc, encoding="utf-8")

doc = ROOT / "docs" / "model_benchmark" / "ULTRA_INTELLIGENCE_DASHBOARD.md"
doc.write_text(
    f"""# System3 Ultra Intelligence Dashboard

Generated UTC: {generated_at}

## Open

`reports/model_benchmark_dashboard/ultra.html`

## Purpose

This is the visual cockpit shell for the future highest-accuracy System3 model benchmark and options intelligence workflow.

## Included visual modules

- Model accuracy leaderboard chart
- Truth-gate radar chart
- Option-chain intelligence shell
- Model artifact table
- Training/artifact KPIs
- Promotion gate status
- Walk-forward readiness panel
- Cost/slippage P&L readiness panel

## Important truth

This dashboard does not fake missing live data.

Items not yet connected are displayed as `NOT PROVEN`.

## Safety

No trading logic changed.
No .env changed.
No broker config changed.
No database changed.
No model artifacts changed.
""",
    encoding="utf-8",
)

print(
    json.dumps(
        {
            "generated_at": generated_at,
            "ultra_dashboard": "reports/model_benchmark_dashboard/ultra.html",
            "doc": "docs/model_benchmark/ULTRA_INTELLIGENCE_DASHBOARD.md",
            "models": len(model_rows),
            "readiness_score": score,
        },
        indent=2,
    )
)
