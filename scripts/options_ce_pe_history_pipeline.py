"""
CE/PE Historical Options ML Pipeline
===================================

Analyzer-only pipeline for Indian index options.

Modes:
  download  - collect historical CE/PE candles from a configured online source
  build     - build a supervised dataset from stored candles
  train     - train/evaluate CE/PE model from the dataset
  full      - download + build + train

Safety rules:
  - No live orders, no order endpoints, no synthetic rows.
  - If data source credentials/contracts are missing, write BLOCKED proof.
  - Supports Dhan historical chart API when security IDs are supplied.
  - Supports import of licensed/user-provided CSV history via --import-dir.

Required contract CSV for Dhan download:
  state/options_history/contracts.csv
Columns:
  underlying,expiry,strike,option_type,security_id,exchange_segment,instrument

Example:
  python scripts/options_ce_pe_history_pipeline.py --mode full --source dhan --from-date 2026-07-01 --to-date 2026-07-10
  python scripts/options_ce_pe_history_pipeline.py --mode full --source csv --import-dir data/options_history_csv
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
HIST_DIR = STATE_DIR / "options_history"
RAW_DIR = HIST_DIR / "raw"
DATASET_DIR = HIST_DIR / "dataset"
MODEL_DIR = STATE_DIR / "models"
REPORT_DIR = ROOT / "reports" / "latest" / "options_ml_training"
CONTRACTS_CSV = HIST_DIR / "contracts.csv"
DATASET_CSV = DATASET_DIR / "ce_pe_dataset.csv"
MODEL_FILE = MODEL_DIR / "options_ce_pe_model.joblib"

FORBIDDEN_WORDS = ("fake", "mock", "synthetic", "fixture", "yahoo", "bhavcopy", "csv_fallback")


@dataclass
class Contract:
    underlying: str
    expiry: str
    strike: float
    option_type: str
    security_id: str
    exchange_segment: str = "NSE_FNO"
    instrument: str = "OPTIDX"


def ensure_dirs() -> None:
    for d in (HIST_DIR, RAW_DIR, DATASET_DIR, MODEL_DIR, REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)


def write_proof(status: str, reason: str, extra: Optional[dict] = None) -> None:
    ensure_dirs()
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "reason": reason,
        "pipeline": "options_ce_pe_history_pipeline",
        "live_trading_enabled": False,
        "broker_order_endpoints_called": False,
        "synthetic_rows_allowed": False,
        "raw_dir": str(RAW_DIR),
        "dataset_csv": str(DATASET_CSV),
        "model_file": str(MODEL_FILE),
    }
    if extra:
        payload.update(extra)
    (REPORT_DIR / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# CE/PE Options ML Training Proof",
        "",
        f"- Generated UTC: `{payload['generated_at']}`",
        f"- Status: **{status}**",
        f"- Reason: {reason}",
        "- Live trading: `OFF`",
        "- Broker order endpoints called: `false`",
        "- Synthetic/fake rows allowed: `false`",
        "",
        "## Paths",
        f"- Raw history: `{payload['raw_dir']}`",
        f"- Dataset: `{payload['dataset_csv']}`",
        f"- Model: `{payload['model_file']}`",
    ]
    if extra:
        lines += ["", "## Details"]
        for k, v in extra.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                lines.append(f"- {k}: `{v}`")
    (REPORT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_contracts() -> List[Contract]:
    if not CONTRACTS_CSV.exists():
        return []
    rows: List[Contract] = []
    with CONTRACTS_CSV.open("r", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                opt = str(r.get("option_type", "")).upper().strip()
                if opt not in ("CE", "PE"):
                    continue
                rows.append(Contract(
                    underlying=str(r.get("underlying", "")).upper().strip(),
                    expiry=str(r.get("expiry", "")).strip(),
                    strike=float(r.get("strike", 0)),
                    option_type=opt,
                    security_id=str(r.get("security_id", "")).strip(),
                    exchange_segment=str(r.get("exchange_segment", "NSE_FNO")).strip() or "NSE_FNO",
                    instrument=str(r.get("instrument", "OPTIDX")).strip() or "OPTIDX",
                ))
            except Exception:
                continue
    return [c for c in rows if c.underlying and c.security_id]


def dhan_headers() -> Dict[str, str]:
    token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    client = os.environ.get("DHAN_CLIENT_ID", "")
    return {
        "Content-Type": "application/json",
        "access-token": token,
        "client-id": client,
    }


def post_json(url: str, payload: dict, headers: Dict[str, str], timeout: int = 45) -> dict:
    req = request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
        return json.loads(text) if text else {}


def normalize_dhan_candles(resp: dict, c: Contract) -> List[dict]:
    data = resp.get("data", resp)
    if not isinstance(data, dict):
        return []
    opens = data.get("open") or data.get("o") or []
    highs = data.get("high") or data.get("h") or []
    lows = data.get("low") or data.get("l") or []
    closes = data.get("close") or data.get("c") or []
    volumes = data.get("volume") or data.get("v") or []
    timestamps = data.get("timestamp") or data.get("time") or data.get("t") or []
    oi = data.get("open_interest") or data.get("oi") or []
    n = min(len(opens), len(highs), len(lows), len(closes), len(timestamps))
    rows = []
    for i in range(n):
        rows.append({
            "timestamp": timestamps[i],
            "underlying": c.underlying,
            "expiry": c.expiry,
            "strike": c.strike,
            "option_type": c.option_type,
            "security_id": c.security_id,
            "exchange_segment": c.exchange_segment,
            "instrument": c.instrument,
            "open": opens[i],
            "high": highs[i],
            "low": lows[i],
            "close": closes[i],
            "volume": volumes[i] if i < len(volumes) else 0,
            "oi": oi[i] if i < len(oi) else 0,
            "data_source": "dhan_historical_chart",
        })
    return rows


def write_contract_rows(contract: Contract, rows: List[dict]) -> Path:
    folder = RAW_DIR / contract.underlying / contract.expiry / contract.option_type
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{int(contract.strike)}_{contract.security_id}.csv"
    cols = ["timestamp", "underlying", "expiry", "strike", "option_type", "security_id", "exchange_segment", "instrument", "open", "high", "low", "close", "volume", "oi", "data_source"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return out


def download_dhan(from_date: str, to_date: str, interval: str, sleep_s: float) -> Tuple[int, int]:
    token = os.environ.get("DHAN_ACCESS_TOKEN", "")
    client = os.environ.get("DHAN_CLIENT_ID", "")
    if not token or not client:
        write_proof("BLOCKED", "DHAN_CLIENT_ID/DHAN_ACCESS_TOKEN missing; cannot download online historical CE/PE data")
        return 0, 0
    contracts = read_contracts()
    if not contracts:
        write_proof("BLOCKED", f"Contract list missing/empty: {CONTRACTS_CSV}. Need CE/PE security_id list before download.")
        return 0, 0

    base = os.environ.get("DHAN_CHARTS_BASE_URL", "https://api.dhan.co/v2/charts")
    endpoint = os.environ.get("DHAN_HISTORICAL_ENDPOINT", f"{base}/historical")
    headers = dhan_headers()
    ok = 0
    rows_total = 0
    errors: Dict[str, str] = {}
    for idx, c in enumerate(contracts):
        payload = {
            "securityId": c.security_id,
            "exchangeSegment": c.exchange_segment,
            "instrument": c.instrument,
            "fromDate": from_date,
            "toDate": to_date,
            "oi": True,
        }
        if interval:
            payload["interval"] = interval
        try:
            resp = post_json(endpoint, payload, headers)
            text = json.dumps(resp)[:1000].lower()
            if any(x in text for x in FORBIDDEN_WORDS):
                raise RuntimeError("forbidden fake/fallback marker in response")
            rows = normalize_dhan_candles(resp, c)
            if not rows:
                errors[f"{c.underlying}_{c.expiry}_{c.strike}_{c.option_type}"] = "NO_CANDLES_RETURNED"
            else:
                write_contract_rows(c, rows)
                ok += 1
                rows_total += len(rows)
        except error.HTTPError as exc:
            errors[f"{c.underlying}_{c.expiry}_{c.strike}_{c.option_type}"] = f"HTTP_{exc.code}"
        except Exception as exc:
            errors[f"{c.underlying}_{c.expiry}_{c.strike}_{c.option_type}"] = str(exc)[:160]
        if idx < len(contracts) - 1:
            time.sleep(sleep_s)
    status = "PASS" if ok and not errors else ("PARTIAL" if ok else "BLOCKED")
    write_proof(status, "Dhan historical download completed" if ok else "Dhan historical download produced no usable candles", {
        "contracts_requested": len(contracts),
        "contracts_downloaded": ok,
        "rows_downloaded": rows_total,
        "from_date": from_date,
        "to_date": to_date,
        "errors_count": len(errors),
    })
    return ok, rows_total


def import_csv_dir(import_dir: Path) -> Tuple[int, int]:
    if not import_dir.exists():
        write_proof("BLOCKED", f"Import directory not found: {import_dir}")
        return 0, 0
    files = list(import_dir.rglob("*.csv"))
    if not files:
        write_proof("BLOCKED", f"No CSV files found in import directory: {import_dir}")
        return 0, 0
    copied = 0
    rows = 0
    for f in files:
        text_head = f.read_text(encoding="utf-8", errors="replace")[:2000].lower()
        if any(x in text_head for x in FORBIDDEN_WORDS):
            continue
        out = RAW_DIR / "imported" / f.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(f.read_bytes())
        copied += 1
        try:
            with out.open("r", encoding="utf-8", errors="replace") as fh:
                rows += max(sum(1 for _ in fh) - 1, 0)
        except Exception:
            pass
    status = "PASS" if copied else "BLOCKED"
    write_proof(status, "Imported user/licensed CSV option history" if copied else "No valid CSV imported", {"files_imported": copied, "rows_imported_estimate": rows})
    return copied, rows


def parse_float(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else default
    except Exception:
        return default


def read_raw_rows() -> List[dict]:
    rows: List[dict] = []
    for f in RAW_DIR.rglob("*.csv"):
        with f.open("r", newline="", encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh):
                combined = " ".join(str(r.get(k, "")) for k in ("data_source", "source", "quote_source")).lower()
                if any(x in combined for x in FORBIDDEN_WORDS):
                    continue
                rows.append(r)
    return rows


def timestamp_key(v) -> str:
    return str(v)


def build_dataset(forward_steps: int = 3) -> int:
    rows = read_raw_rows()
    if not rows:
        write_proof("BLOCKED", "No raw CE/PE option history rows available for dataset build")
        return 0
    groups: Dict[str, List[dict]] = {}
    for r in rows:
        key = "|".join([str(r.get("underlying", "")), str(r.get("expiry", "")), str(r.get("strike", "")), str(r.get("option_type", "")), str(r.get("security_id", ""))])
        groups.setdefault(key, []).append(r)
    dataset: List[dict] = []
    for key, g in groups.items():
        g.sort(key=lambda x: timestamp_key(x.get("timestamp", "")))
        for i in range(1, max(len(g) - forward_steps, 1)):
            prev = g[i - 1]
            cur = g[i]
            fut = g[i + forward_steps]
            close = parse_float(cur.get("close"))
            prev_close = parse_float(prev.get("close"))
            future_close = parse_float(fut.get("close"))
            if close <= 0 or prev_close <= 0 or future_close <= 0:
                continue
            ret_1 = (close - prev_close) / prev_close
            fwd = (future_close - close) / close
            dataset.append({
                "timestamp": cur.get("timestamp", ""),
                "underlying": cur.get("underlying", ""),
                "expiry": cur.get("expiry", ""),
                "strike": cur.get("strike", ""),
                "option_type": cur.get("option_type", ""),
                "close": close,
                "volume": parse_float(cur.get("volume")),
                "oi": parse_float(cur.get("oi")),
                "return_1": ret_1,
                "range_pct": (parse_float(cur.get("high")) - parse_float(cur.get("low"))) / close if close else 0,
                "target_forward_return": fwd,
                "target_up": 1 if fwd > 0 else 0,
                "data_source": cur.get("data_source", "unknown"),
            })
    if not dataset:
        write_proof("BLOCKED", "Raw rows exist but no valid supervised CE/PE training rows were built")
        return 0
    cols = list(dataset[0].keys())
    with DATASET_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(dataset)
    write_proof("PASS", "CE/PE supervised dataset built", {"dataset_rows": len(dataset), "raw_rows": len(rows), "groups": len(groups)})
    return len(dataset)


def train_model(min_rows: int = 500) -> int:
    if not DATASET_CSV.exists():
        write_proof("BLOCKED", f"Dataset missing: {DATASET_CSV}")
        return 0
    try:
        import pandas as pd
        from joblib import dump
        from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
    except Exception as exc:
        write_proof("BLOCKED", f"Training dependencies missing: {type(exc).__name__}: {exc}")
        return 0

    df = pd.read_csv(DATASET_CSV)
    if len(df) < min_rows:
        write_proof("BLOCKED", f"Not enough CE/PE rows to train: {len(df)} < {min_rows}", {"dataset_rows": int(len(df)), "min_rows": min_rows})
        return 0
    y = df["target_up"].astype(int)
    X = df[["underlying", "option_type", "strike", "close", "volume", "oi", "return_1", "range_pct"]].copy()
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["underlying", "option_type"]),
        ("num", "passthrough", ["strike", "close", "volume", "oi", "return_1", "range_pct"]),
    ])
    models = {
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=5, random_state=42, n_jobs=-1),
    }
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, shuffle=False)
    results = {}
    best_name = None
    best_score = -1.0
    best_pipe = None
    for name, model in models.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, "predict_proba") else pred
        acc = float(accuracy_score(y_test, pred))
        try:
            auc = float(roc_auc_score(y_test, proba))
        except Exception:
            auc = None
        score = auc if auc is not None else acc
        results[name] = {"accuracy": round(acc, 4), "auc": round(auc, 4) if auc is not None else None}
        if score > best_score:
            best_score = score
            best_name = name
            best_pipe = pipe
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if best_pipe is not None:
        dump({"model": best_pipe, "best_model": best_name, "results": results, "trained_at": datetime.utcnow().isoformat()+"Z"}, MODEL_FILE)
    write_proof("PASS", "CE/PE options model trained on historical rows", {
        "dataset_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "best_model": best_name,
        "best_score": round(float(best_score), 4),
        "model_file_exists": MODEL_FILE.exists(),
        "results": results,
        "ready_for_live": False,
    })
    return len(df)


def default_dates(days: int) -> Tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="CE/PE historical options ML pipeline")
    parser.add_argument("--mode", choices=["download", "build", "train", "full"], default="full")
    parser.add_argument("--source", choices=["dhan", "csv", "none"], default="dhan")
    parser.add_argument("--from-date", default=None)
    parser.add_argument("--to-date", default=None)
    parser.add_argument("--lookback-days", type=int, default=45)
    parser.add_argument("--interval", default="")
    parser.add_argument("--sleep-s", type=float, default=3.25)
    parser.add_argument("--import-dir", default="")
    parser.add_argument("--forward-steps", type=int, default=3)
    parser.add_argument("--min-train-rows", type=int, default=500)
    args = parser.parse_args()

    ensure_dirs()
    from_date, to_date = args.from_date, args.to_date
    if not from_date or not to_date:
        from_date, to_date = default_dates(args.lookback_days)

    try:
        if args.mode in ("download", "full"):
            if args.source == "dhan":
                download_dhan(from_date, to_date, args.interval, args.sleep_s)
            elif args.source == "csv":
                if not args.import_dir:
                    write_proof("BLOCKED", "--import-dir required for source=csv")
                    return 0
                import_csv_dir(Path(args.import_dir))
        if args.mode in ("build", "full"):
            build_dataset(forward_steps=args.forward_steps)
        if args.mode in ("train", "full"):
            train_model(min_rows=args.min_train_rows)
        return 0
    except Exception as exc:
        write_proof("BLOCKED", f"Pipeline crashed: {type(exc).__name__}: {str(exc)[:240]}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
