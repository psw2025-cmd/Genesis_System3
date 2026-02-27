"""
Generate Synthetic Live Market Data for Dashboard Testing
Creates realistic option chain data to simulate live market conditions
"""

import json
import random
import csv
import time
from datetime import datetime
from pathlib import Path
import pytz

# Base spot prices (realistic values)
BASE_SPOTS = {"NIFTY": 19500, "BANKNIFTY": 45000, "FINNIFTY": 21000, "MIDCPNIFTY": 12000, "SENSEX": 72000}

# Strike steps
STRIKE_STEPS = {"NIFTY": 50, "BANKNIFTY": 100, "FINNIFTY": 50, "MIDCPNIFTY": 25, "SENSEX": 100}


def generate_synthetic_chain(underlying: str, num_strikes: int = 20):
    """Generate synthetic option chain data for an underlying"""
    base_spot = BASE_SPOTS.get(underlying, 20000)
    strike_step = STRIKE_STEPS.get(underlying, 50)

    # Add some random movement to spot (±0.5%) - vary each time
    # Use time-based seed for variation
    random.seed(int(time.time() * 1000) % 1000000)
    spot_movement = random.uniform(-0.005, 0.005)
    current_spot = base_spot * (1 + spot_movement)

    contracts = []
    atm_strike = round(current_spot / strike_step) * strike_step

    # Generate strikes around ATM
    strikes = []
    for i in range(-num_strikes // 2, num_strikes // 2 + 1):
        strikes.append(atm_strike + (i * strike_step))

    for strike in strikes:
        # Calculate moneyness
        moneyness = (current_spot - strike) / current_spot

        # Generate CE (Call) contract
        ce_ltp = max(1.0, abs(moneyness) * current_spot * 0.01 + random.uniform(5, 50))
        ce_oi = random.randint(10000, 500000)
        ce_volume = random.randint(100, 10000)
        ce_iv = random.uniform(0.15, 0.35)
        ce_delta = random.uniform(0.1, 0.9)
        ce_gamma = random.uniform(0.01, 0.05)
        ce_vega = random.uniform(0.5, 2.0)
        ce_theta = random.uniform(-0.5, -0.1)

        contracts.append(
            {
                "underlying": underlying,
                "strike": float(strike),
                "option_type": "CE",
                "spot_price": float(current_spot),
                "ltp": float(ce_ltp),
                "bidPrice": float(ce_ltp * 0.99),
                "offerPrice": float(ce_ltp * 1.01),
                "mid_price": float(ce_ltp),
                "oi": int(ce_oi),
                "volume": int(ce_volume),
                "iv": float(ce_iv),
                "delta": float(ce_delta),
                "gamma": float(ce_gamma),
                "vega": float(ce_vega),
                "theta": float(ce_theta),
                "symbol": f"{underlying}{int(strike)}CE",
                "token": f"{underlying}{int(strike)}CE{random.randint(100000, 999999)}",
                "expiry": "08FEB2026",
                "fetch_timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            }
        )

        # Generate PE (Put) contract
        pe_ltp = max(1.0, abs(moneyness) * current_spot * 0.01 + random.uniform(5, 50))
        pe_oi = random.randint(10000, 500000)
        pe_volume = random.randint(100, 10000)
        pe_iv = random.uniform(0.15, 0.35)
        pe_delta = random.uniform(-0.9, -0.1)
        pe_gamma = random.uniform(0.01, 0.05)
        pe_vega = random.uniform(0.5, 2.0)
        pe_theta = random.uniform(-0.5, -0.1)

        contracts.append(
            {
                "underlying": underlying,
                "strike": float(strike),
                "option_type": "PE",
                "spot_price": float(current_spot),
                "ltp": float(pe_ltp),
                "bidPrice": float(pe_ltp * 0.99),
                "offerPrice": float(pe_ltp * 1.01),
                "mid_price": float(pe_ltp),
                "oi": int(pe_oi),
                "volume": int(pe_volume),
                "iv": float(pe_iv),
                "delta": float(pe_delta),
                "gamma": float(pe_gamma),
                "vega": float(pe_vega),
                "theta": float(pe_theta),
                "symbol": f"{underlying}{int(strike)}PE",
                "token": f"{underlying}{int(strike)}PE{random.randint(100000, 999999)}",
                "expiry": "08FEB2026",
                "fetch_timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            }
        )

    return contracts


def generate_synthetic_signal():
    """Generate a synthetic trading signal"""
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY"]
    strategies = ["BUY_CE", "BUY_PE", "IRON_CONDOR", "BULL_CALL_SPREAD"]

    # 70% chance of TRADE signal
    if random.random() < 0.7:
        underlying = random.choice(underlyings)
        strategy = random.choice(strategies)
        confidence = random.uniform(0.65, 0.90)

        return {
            "action": "TRADE",
            "mode": "LIVE",
            "underlying": underlying,
            "strategy": strategy,
            "confidence": confidence,
            "reason": "STRONG_SIGNAL",
            "reasons": ["High liquidity", "Good risk-reward", "Trend alignment"],
            "symbol": f"{underlying}19700CE",
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "entry_mid": random.uniform(50, 200),
            "stop_loss": random.uniform(30, 100),
            "target": random.uniform(150, 400),
        }
    else:
        return {
            "action": "NO_TRADE",
            "mode": "LIVE",
            "reason": "LOW_CONFIDENCE",
            "reasons": ["Low confidence", "Poor risk-reward"],
            "confidence": random.uniform(0.3, 0.55),
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


def main():
    """Generate all synthetic data files"""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    print("Generating synthetic live market data...")

    # 1. Generate chain data for all underlyings
    all_contracts = []
    for underlying in BASE_SPOTS.keys():
        contracts = generate_synthetic_chain(underlying, num_strikes=20)
        all_contracts.extend(contracts)
        print(f"  [OK] Generated {len(contracts)} contracts for {underlying}")

    # Save to chain_raw_live.csv
    chain_file = outputs_dir / "chain_raw_live.csv"
    if all_contracts:
        with open(chain_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_contracts[0].keys())
            writer.writeheader()
            writer.writerows(all_contracts)
        print(f"  [OK] Saved {len(all_contracts)} total contracts to chain_raw_live.csv")
    else:
        print("  ❌ No contracts generated")
        return

    # 2. Generate trading signal
    signal = generate_synthetic_signal()
    signal_file = outputs_dir / "top_trade_signal.json"
    with open(signal_file, "w") as f:
        json.dump(signal, f, indent=2, default=str)
    print(f"  [OK] Generated signal: {signal['action']} - {signal.get('underlying', 'N/A')}")

    # 3. Update health.json to show LIVE mode
    health_file = outputs_dir / "health.json"
    health = {}
    if health_file.exists():
        with open(health_file, "r") as f:
            health = json.load(f)
    health["mode"] = "LIVE"
    health["is_running"] = True
    health["is_connected"] = True
    health["last_data_fetch"] = datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
    health["total_cycles"] = health.get("total_cycles", 0) + 1
    with open(health_file, "w") as f:
        json.dump(health, f, indent=2, default=str)
    print("  [OK] Updated health.json to LIVE mode")

    # 4. Generate QC report (PASS)
    qc_report = {
        "status": "PASS",
        "qc_passed": True,
        "mode": "LIVE",
        "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        "underlying_count": len(BASE_SPOTS),
        "total_contracts": len(all_contracts),
        "cycle": health.get("total_cycles", 1),
    }
    qc_file = outputs_dir / "qc_report_live.json"
    with open(qc_file, "w") as f:
        json.dump(qc_report, f, indent=2, default=str)
    print("  [OK] Generated QC report (PASS)")

    print("\n[SUCCESS] Synthetic live market data generated successfully!")
    print(f"   Total contracts: {len(all_contracts)}")
    print(f"   Signal: {signal['action']}")
    print(f"   Mode: LIVE")


if __name__ == "__main__":
    main()
