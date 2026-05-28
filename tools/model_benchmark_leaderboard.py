from pathlib import Path
from datetime import datetime, timezone
import json
import csv
import html
import os

ROOT = Path.cwd()
OUT_DIR = ROOT / "reports" / "model_benchmark_dashboard"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TRAINING_CSV = ROOT / "storage" / "training" / "angel_index_options_training.csv"
MODELS_DIR = ROOT / "core" / "models" / "angel_one"
AUTHORITY_MAP = ROOT / "reports" / "authority_map" / "system3_authority_runtime_map.json"

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

def file_status(path: Path):
    return {
        "path": str(path.relative_to(ROOT)) if path.exists() else str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat() if path.exists() else None,
    }

def csv_profile(path: Path, max_rows_scan=200000):
    result = {
        "exists": path.exists(),
        "rows_scanned": 0,
        "columns": [],
        "underlyings": {},
        "labels": {},
        "freshness_utc_min": None,
        "freshness_utc_max": None,
        "status": "missing",
    }
    if not path.exists():
        return result

    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            result["columns"] = reader.fieldnames or []
            for i, row in enumerate(reader, 1):
                if i > max_rows_scan:
                    break
                result["rows_scanned"] = i
                u = row.get("underlying", "UNKNOWN") or "UNKNOWN"
                result["underlyings"][u] = result["underlyings"].get(u, 0) + 1
                lab = row.get("label_3class") or row.get("label_used") or row.get("label") or "UNKNOWN"
                result["labels"][lab] = result["labels"].get(lab, 0) + 1
                ts = row.get("ts") or row.get("timestamp") or row.get("time")
                if ts:
                    if result["freshness_utc_min"] is None or ts < result["freshness_utc_min"]:
                        result["freshness_utc_min"] = ts
                    if result["freshness_utc_max"] is None or ts > result["freshness_utc_max"]:
                        result["freshness_utc_max"] = ts
        result["status"] = "present" if result["rows_scanned"] > 0 else "empty"
    except Exception as e:
        result["status"] = f"error: {e}"
    return result

def model_artifacts_profile():
    rows = []
    for u in UNDERLYINGS:
        model = MODELS_DIR / f"{u}_model.pkl"
        meta = MODELS_DIR / f"{u}_model_meta.json"
        meta_json = None
        if meta.exists():
            try:
                meta_json = json.loads(meta.read_text(encoding="utf-8", errors="ignore"))
            except Exception as e:
                meta_json = {"read_error": str(e)}
        rows.append({
            "underlying": u,
            "model": file_status(model),
            "meta": file_status(meta),
            "meta_json": meta_json,
            "artifact_pair_ok": model.exists() and meta.exists(),
            "test_accuracy": meta_json.get("test_accuracy") if isinstance(meta_json, dict) else None,
            "train_samples": meta_json.get("train_samples") if isinstance(meta_json, dict) else None,
            "test_samples": meta_json.get("test_samples") if isinstance(meta_json, dict) else None,
            "features_count": len(meta_json.get("features", [])) if isinstance(meta_json, dict) and isinstance(meta_json.get("features"), list) else None,
        })
    return rows

def readiness_score(training, artifacts):
    score = 0
    max_score = 100
    reasons = []

    if training["exists"] and training["rows_scanned"] > 0:
        score += 20
    else:
        reasons.append("training data missing/empty")

    if len(training.get("underlyings", {})) >= 2:
        score += 10
    else:
        reasons.append("not enough underlying diversity proven")

    if len(training.get("labels", {})) >= 2:
        score += 10
    else:
        reasons.append("not enough label diversity proven")

    ok_artifacts = sum(1 for a in artifacts if a["artifact_pair_ok"])
    score += min(20, ok_artifacts * 4)
    if ok_artifacts == 0:
        reasons.append("no model artifact pairs proven")

    acc_count = sum(1 for a in artifacts if isinstance(a.get("test_accuracy"), (int, float)))
    score += min(10, acc_count * 2)
    if acc_count == 0:
        reasons.append("no saved test accuracy metadata proven")

    # These are framework gates not yet implemented/proven
    reasons.append("walk-forward benchmark not yet implemented")
    reasons.append("cost/slippage P&L benchmark not yet implemented")
    reasons.append("dashboard runtime model-version API not yet proven")
    reasons.append("promotion gate not yet implemented")

    return {
        "score": score,
        "max_score": max_score,
        "percent": round(score / max_score * 100, 2),
        "reasons": reasons,
    }

def status_badge(ok, label_true="PASS", label_false="NOT PROVEN"):
    if ok:
        return f'<span class="badge pass">{label_true}</span>'
    return f'<span class="badge fail">{label_false}</span>'

training = csv_profile(TRAINING_CSV)
artifacts = model_artifacts_profile()
readiness = readiness_score(training, artifacts)

authority_exists = AUTHORITY_MAP.exists()

data = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Model Benchmark Leaderboard Dashboard; report-only; no trading logic changed.",
    "training_csv": file_status(TRAINING_CSV),
    "training_profile": training,
    "models_dir": file_status(MODELS_DIR),
    "model_artifacts": artifacts,
    "authority_map_present": authority_exists,
    "readiness": readiness,
    "next_required": [
        "Implement walk-forward validation runner",
        "Implement model comparison: baseline, gradient boosting, ensemble-ready slots",
        "Implement cost/slippage/spread-aware P&L benchmark",
        "Expose model version + benchmark score in dashboard backend",
        "Block promotion if benchmark proof missing"
    ],
}

json_path = OUT_DIR / "model_benchmark_leaderboard.json"
json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

artifact_rows = []
for a in artifacts:
    artifact_rows.append(f"""
<tr>
  <td>{html.escape(a['underlying'])}</td>
  <td>{status_badge(a['model']['exists'], 'FOUND', 'MISSING')}</td>
  <td>{status_badge(a['meta']['exists'], 'FOUND', 'MISSING')}</td>
  <td>{html.escape(str(a.get('test_accuracy')))}</td>
  <td>{html.escape(str(a.get('train_samples')))}</td>
  <td>{html.escape(str(a.get('test_samples')))}</td>
  <td>{html.escape(str(a.get('features_count')))}</td>
</tr>
""")

training_underlying_rows = []
for k, v in sorted(training.get("underlyings", {}).items(), key=lambda x: (-x[1], x[0])):
    training_underlying_rows.append(f"<tr><td>{html.escape(str(k))}</td><td>{v}</td></tr>")

label_rows = []
for k, v in sorted(training.get("labels", {}).items(), key=lambda x: (-x[1], x[0])):
    label_rows.append(f"<tr><td>{html.escape(str(k))}</td><td>{v}</td></tr>")

score = readiness["percent"]
score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"

html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>System3 Model Benchmark Leaderboard</title>
<style>
body {{
  margin: 0;
  font-family: Inter, Arial, sans-serif;
  background: #070b13;
  color: #e5e7eb;
}}
.wrap {{ padding: 28px; max-width: 1300px; margin: auto; }}
.hero {{
  background: linear-gradient(135deg, #111827, #1e3a8a, #312e81);
  border: 1px solid #334155;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(0,0,0,.35);
}}
h1 {{ margin: 0 0 8px; font-size: 34px; }}
.sub {{ color: #cbd5e1; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 20px; }}
.card {{
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 18px;
  padding: 18px;
}}
.metric {{ font-size: 30px; font-weight: 800; }}
.label {{ color: #94a3b8; font-size: 13px; margin-top: 6px; }}
.badge {{
  display: inline-block;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}}
.pass {{ background: rgba(34,197,94,.15); color: #86efac; border: 1px solid rgba(34,197,94,.4); }}
.fail {{ background: rgba(239,68,68,.15); color: #fca5a5; border: 1px solid rgba(239,68,68,.4); }}
.warn {{ background: rgba(245,158,11,.15); color: #fcd34d; border: 1px solid rgba(245,158,11,.4); }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
th, td {{ border-bottom: 1px solid #1f2937; padding: 10px; text-align: left; }}
th {{ color: #93c5fd; }}
.section {{ margin-top: 22px; }}
.bar-bg {{ background: #1f2937; border-radius: 999px; height: 18px; overflow: hidden; }}
.bar {{ width: {score}%; background: {score_color}; height: 18px; }}
.small {{ color: #94a3b8; font-size: 13px; }}
ul {{ line-height: 1.8; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>System3 Model Benchmark Leaderboard</h1>
    <div class="sub">Generated UTC: {html.escape(data['generated_at_utc'])}</div>
    <div class="sub">Report-only dashboard. No trading logic, .env, broker config, database, dashboard UI, or model artifacts changed.</div>

    <div class="grid">
      <div class="card"><div class="metric">{training.get('rows_scanned', 0)}</div><div class="label">Training rows scanned</div></div>
      <div class="card"><div class="metric">{len(training.get('underlyings', {}))}</div><div class="label">Underlyings in training CSV</div></div>
      <div class="card"><div class="metric">{sum(1 for a in artifacts if a['artifact_pair_ok'])}/{len(artifacts)}</div><div class="label">Model artifact pairs proven</div></div>
      <div class="card"><div class="metric">{score}%</div><div class="label">Benchmark readiness score</div></div>
    </div>
  </div>

  <div class="section card">
    <h2>Benchmark Readiness</h2>
    <div class="bar-bg"><div class="bar"></div></div>
    <ul>
      {''.join(f"<li>{html.escape(r)}</li>" for r in readiness['reasons'])}
    </ul>
  </div>

  <div class="section card">
    <h2>Model Artifacts</h2>
    <table>
      <tr><th>Underlying</th><th>Model PKL</th><th>Meta JSON</th><th>Test Accuracy</th><th>Train Samples</th><th>Test Samples</th><th>Features</th></tr>
      {''.join(artifact_rows)}
    </table>
  </div>

  <div class="section grid">
    <div class="card" style="grid-column: span 2;">
      <h2>Training Data by Underlying</h2>
      <table><tr><th>Underlying</th><th>Rows</th></tr>{''.join(training_underlying_rows) or '<tr><td colspan="2">No training rows proven</td></tr>'}</table>
    </div>
    <div class="card" style="grid-column: span 2;">
      <h2>Labels</h2>
      <table><tr><th>Label</th><th>Rows</th></tr>{''.join(label_rows) or '<tr><td colspan="2">No labels proven</td></tr>'}</table>
    </div>
  </div>

  <div class="section card">
    <h2>Next Required for Highest Accuracy</h2>
    <ul>
      {''.join(f"<li>{html.escape(x)}</li>" for x in data['next_required'])}
    </ul>
  </div>

  <div class="section card">
    <h2>Proof Links / Inputs</h2>
    <p>Training CSV: <code>{html.escape(str(TRAINING_CSV.relative_to(ROOT)))}</code> — {status_badge(training['exists'], 'FOUND', 'MISSING')}</p>
    <p>Models directory: <code>{html.escape(str(MODELS_DIR.relative_to(ROOT)))}</code> — {status_badge(MODELS_DIR.exists(), 'FOUND', 'MISSING')}</p>
    <p>Authority map: <code>{html.escape(str(AUTHORITY_MAP.relative_to(ROOT)))}</code> — {status_badge(authority_exists, 'FOUND', 'MISSING')}</p>
  </div>
</div>
</body>
</html>
"""

html_path = OUT_DIR / "index.html"
html_path.write_text(html_doc, encoding="utf-8")

md_path = ROOT / "docs" / "model_benchmark" / "MODEL_BENCHMARK_LEADERBOARD.md"
md_path.write_text(f"""# Model Benchmark Leaderboard Framework

Generated UTC: {data['generated_at_utc']}

## Purpose

This is the proof-first framework for selecting the highest-performing System3 prediction model.

It does **not** promote models by claim. It promotes only after benchmark evidence.

## Dashboard

Open:

`reports/model_benchmark_dashboard/index.html`

## Current readiness score

`{score}%`

## Current proof status

- Training rows scanned: `{training.get('rows_scanned', 0)}`
- Underlyings in training CSV: `{len(training.get('underlyings', {}))}`
- Model artifact pairs found: `{sum(1 for a in artifacts if a['artifact_pair_ok'])}/{len(artifacts)}`
- Authority map present: `{authority_exists}`

## Required before promotion

- Walk-forward validation
- Model family comparison
- P&L after costs
- Slippage/spread sensitivity
- Dashboard runtime model-version proof
- Promotion gate

## Safety

This PR is report/framework only.

No trading logic changed.
No secrets changed.
No .env changed.
No broker config changed.
No database changed.
No model artifacts changed.
""", encoding="utf-8")

print(json.dumps({
    "generated_at_utc": data["generated_at_utc"],
    "dashboard": str(html_path),
    "json": str(json_path),
    "docs": str(md_path),
    "readiness_percent": score,
    "training_rows_scanned": training.get("rows_scanned", 0),
    "artifact_pairs": sum(1 for a in artifacts if a["artifact_pair_ok"]),
}, indent=2))
