"""Genesis System3 — Complete WebSocket & Data Stream Diagnostic for All Indices & Equities."""

import asyncio
import datetime
import json
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure local laptop environment
os.environ["INDEX_CHAIN_MICRO_STREAM"] = "0"
os.environ["MARKET_TOP_MICRO_STREAM"] = "0"

from fastapi.testclient import TestClient
from dashboard.backend.app import app
from core.data.datasource_manager import DataSourceManager

client = TestClient(app)
dsm = DataSourceManager()

def test_websocket_stream():
    print("\n" + "=" * 90)
    print("   GENESIS SYSTEM3 — SECTION 1: WEBSOCKET STREAM (/ws/stream) AUDIT")
    print("=" * 90)

    ws_frames = []
    start_time = time.time()
    try:
        with client.websocket_connect("/ws/stream") as websocket:
            connect_latency = round((time.time() - start_time) * 1000, 2)
            print(f"   [OK] Connected to /ws/stream in {connect_latency}ms")

            # Collect frames sent immediately on connect (market_status, health_update, paper_update, etc.)
            for i in range(3):
                try:
                    data = websocket.receive_json()
                    frame_type = data.get("type", "unknown")
                    ts = data.get("timestamp", "")
                    ws_frames.append(data)
                    print(f"   [FRAME {i+1}] Type: {frame_type:<22} | Timestamp: {ts} | Size: {len(json.dumps(data))} bytes")
                except Exception as ex:
                    break

        ws_result = {
            "status": "PASS",
            "connect_latency_ms": connect_latency,
            "frames_received": len(ws_frames),
            "frame_types": [f.get("type") for f in ws_frames],
        }
    except Exception as e:
        print(f"   [FAIL] WebSocket connection error: {e}")
        ws_result = {"status": "FAIL", "error": str(e)}

    return ws_result

def test_all_indices_stream():
    print("\n" + "=" * 90)
    print("   GENESIS SYSTEM3 — SECTION 2: ALL INDICES REAL-TIME DATA STREAM TEST")
    print("=" * 90)

    indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]
    index_results = {}

    for idx in indices:
        start_t = time.time()
        # Test endpoint
        res = client.get(f"/api/chain/{idx}")
        latency = round((time.time() - start_t) * 1000, 2)
        status_code = res.status_code

        if status_code == 200:
            try:
                data = res.json()
                spot = data.get("spot") or data.get("underlying_spot") or 0.0
                total_contracts = data.get("total_contracts") or len(data.get("strikes", [])) or 0
                pcr = data.get("pcr") or 0.0
                status = data.get("status") or "OK"
                index_results[idx] = {
                    "status": "PASS",
                    "status_code": 200,
                    "latency_ms": latency,
                    "spot_price": spot,
                    "total_contracts": total_contracts,
                    "pcr": pcr,
                    "market_status": status,
                }
                print(f"   [PASS] Index: {idx:<12} | Spot: {spot:>10.2f} | Contracts: {total_contracts:>4} | PCR: {pcr:>5.3f} | Latency: {latency:>6.2f}ms")
            except Exception as e:
                index_results[idx] = {"status": "FAIL", "error": str(e)}
                print(f"   [FAIL] Index: {idx:<12} | Parsing error: {e}")
        else:
            index_results[idx] = {"status": "FAIL", "status_code": status_code, "latency_ms": latency}
            print(f"   [FAIL] Index: {idx:<12} | HTTP {status_code} | Latency: {latency:>6.2f}ms")

    return index_results

def test_all_equities_stream():
    print("\n" + "=" * 90)
    print("   GENESIS SYSTEM3 — SECTION 3: ALL EQUITIES & MARKET TOP SCANNER STREAM")
    print("=" * 90)

    equity_results = {}

    # 1. Equity Options Scanner
    start_t = time.time()
    res_eq = client.get("/api/scanner/equity_options")
    eq_latency = round((time.time() - start_t) * 1000, 2)
    if res_eq.status_code == 200:
        eq_data = res_eq.json()
        contracts_scored = eq_data.get("contracts_scored_total", 0)
        table = eq_data.get("market_top_table", [])
        top_symbols = [row.get("symbol", "") for row in table[:10]]
        equity_results["equity_options_scanner"] = {
            "status": "PASS",
            "latency_ms": eq_latency,
            "contracts_scored": contracts_scored,
            "top_ranked_symbols": top_symbols,
            "table_rows": len(table),
        }
        print(f"   [PASS] Equity Options Scanner  | Scored: {contracts_scored:>5} | Top Rows: {len(table):>3} | Latency: {eq_latency:>6.2f}ms")
        if top_symbols:
            print(f"          Top Equities: {', '.join(top_symbols[:8])}")
    else:
        equity_results["equity_options_scanner"] = {"status": "FAIL", "status_code": res_eq.status_code}
        print(f"   [FAIL] Equity Options Scanner  | HTTP {res_eq.status_code}")

    # 2. Live Market Board
    start_t = time.time()
    res_mb = client.get("/api/market/live_board")
    mb_latency = round((time.time() - start_t) * 1000, 2)
    if res_mb.status_code == 200:
        mb_data = res_mb.json()
        gainers = mb_data.get("top_gainers", [])
        losers = mb_data.get("top_losers", [])
        equity_results["market_live_board"] = {
            "status": "PASS",
            "latency_ms": mb_latency,
            "gainers_count": len(gainers),
            "losers_count": len(losers),
        }
        print(f"   [PASS] Live Market Board       | Gainers: {len(gainers):>3} | Losers: {len(losers):>3} | Latency: {mb_latency:>6.2f}ms")
    else:
        equity_results["market_live_board"] = {"status": "FAIL", "status_code": res_mb.status_code}
        print(f"   [FAIL] Live Market Board       | HTTP {res_mb.status_code}")

    # 3. Batch Market Data
    start_t = time.time()
    res_batch = client.get("/api/batch/market-data")
    batch_latency = round((time.time() - start_t) * 1000, 2)
    if res_batch.status_code == 200:
        batch_data = res_batch.json()
        equity_results["batch_market_data"] = {
            "status": "PASS",
            "latency_ms": batch_latency,
            "keys": list(batch_data.keys()),
        }
        print(f"   [PASS] Batch Market Data Feed  | Status: OK | Latency: {batch_latency:>6.2f}ms")
    else:
        equity_results["batch_market_data"] = {"status": "FAIL", "status_code": res_batch.status_code}
        print(f"   [FAIL] Batch Market Data Feed  | HTTP {res_batch.status_code}")

    return equity_results

def main():
    now_ist = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    now_utc = datetime.datetime.utcnow().isoformat() + "Z"

    ws_res = test_websocket_stream()
    idx_res = test_all_indices_stream()
    eq_res = test_all_equities_stream()

    full_audit = {
        "timestamp_ist": now_ist,
        "timestamp_utc": now_utc,
        "authority": "LOCAL_LAPTOP",
        "websocket_audit": ws_res,
        "indices_data_stream": idx_res,
        "equities_data_stream": eq_res,
    }

    out1 = Path(r"C:\Genesis_System3_Runtime\state\websocket_and_data_stream_audit.json")
    out1.parent.mkdir(parents=True, exist_ok=True)
    out1.write_text(json.dumps(full_audit, indent=2), encoding="utf-8")

    out2 = Path(r"C:\Temp\websocket_and_data_stream_audit.json")
    out2.write_text(json.dumps(full_audit, indent=2), encoding="utf-8")

    print("\n" + "=" * 90)
    print("   [OK] WebSocket and Data Stream Diagnostic Complete!")
    print(f"        Saved -> {out1}")
    print(f"        Saved -> {out2}")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    main()
