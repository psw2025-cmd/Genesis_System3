"""
Final Best Strategy Selector
Compares all optimization results and selects the absolute best
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def load_all_results() -> List[Dict]:
    """Load all optimization results."""
    results = []

    # Load 10K optimization results
    path_10k = ROOT_DIR / "outputs" / "strategy_optimization_results.json"
    if path_10k.exists():
        try:
            with open(path_10k, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    results.extend([{"source": "10k_optimization", **r} for r in data])
        except:
            pass

    # Load iterative improvement results
    path_iter = ROOT_DIR / "outputs" / "iterative_improvement_results.json"
    if path_iter.exists():
        try:
            with open(path_iter, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    results.extend([{"source": "iterative", **r} for r in data])
        except:
            pass

    # Load world-class optimization results
    path_wc = ROOT_DIR / "outputs" / "world_class_optimization_results.json"
    if path_wc.exists():
        try:
            with open(path_wc, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    results.extend([{"source": "world_class", **r} for r in data])
        except:
            pass

    return results


def calculate_final_score(result: Dict) -> float:
    """Calculate final composite score."""
    # Extract result data
    if "result" in result:
        res = result["result"]
    elif "strategy" in result:
        res = result
    else:
        res = result

    # Normalize metrics
    pnl = res.get("total_pnl", 0)
    roi = res.get("roi_pct", 0)
    win_rate = res.get("win_rate", 0)
    sharpe = res.get("sharpe_ratio", 0)
    profit_factor = res.get("profit_factor", 0)
    max_dd = abs(res.get("max_drawdown", 0))

    # Weighted scoring
    pnl_score = min(pnl / 100000, 2.0) * 0.25  # Cap at 2x
    roi_score = min(roi / 100, 2.0) * 0.20
    win_rate_score = win_rate * 0.20
    sharpe_score = min(sharpe / 50, 2.0) * 0.15
    profit_factor_score = min(profit_factor / 100, 2.0) * 0.10
    drawdown_penalty = min(max_dd / 50000, 1.0) * 0.10  # Penalty for drawdown

    final_score = (pnl_score + roi_score + win_rate_score + sharpe_score + profit_factor_score - drawdown_penalty) * 100

    return final_score


def select_best_strategy() -> Dict:
    """Select the absolute best strategy from all results."""
    print("=" * 80)
    print("  FINAL BEST STRATEGY SELECTOR")
    print("=" * 80)

    all_results = load_all_results()

    if not all_results:
        print("No optimization results found. Run optimizations first.")
        return None

    print(f"\nLoaded {len(all_results)} strategy results from all optimizations")

    # Calculate scores
    scored_results = []
    for result in all_results:
        score = calculate_final_score(result)
        scored_results.append({"result": result, "score": score})

    # Sort by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # Display top 10
    print("\n" + "=" * 80)
    print("  TOP 10 STRATEGIES (ALL OPTIMIZATIONS)")
    print("=" * 80)

    for i, item in enumerate(scored_results[:10], 1):
        result = item["result"]
        res = result.get("result", result.get("strategy", result))

        source = result.get("source", "unknown")
        config = result.get("config", result.get("strategy", {}))

        print(f"\n[{i}] Score: {item['score']:.2f} | Source: {source}")
        print(f"    PnL: Rs {res.get('total_pnl', 0):,.2f}")
        print(f"    ROI: {res.get('roi_pct', 0):.1f}%")
        print(f"    Win Rate: {res.get('win_rate', 0)*100:.1f}%")
        print(f"    Sharpe: {res.get('sharpe_ratio', 0):.2f}")
        print(f"    Profit Factor: {res.get('profit_factor', 0):.2f}")
        if config:
            print(
                f"    Config: {config.get('position_sizing', 'N/A')} | {config.get('stop_loss', 'N/A')} | {config.get('take_profit', 'N/A')}"
            )

    # Best strategy
    best = scored_results[0]
    best_result = best["result"]
    best_res = best_result.get("result", best_result.get("strategy", best_result))

    print("\n" + "=" * 80)
    print("  ABSOLUTE BEST STRATEGY")
    print("=" * 80)
    print(f"\nSource: {best_result.get('source', 'unknown')}")
    print(f"Final Score: {best['score']:.2f}")
    print(f"\nConfiguration:")
    best_config = best_result.get("config", best_result.get("strategy", {}))
    print(json.dumps(best_config, indent=2))
    print(f"\nPerformance:")
    print(f"  Total PnL: Rs {best_res.get('total_pnl', 0):,.2f}")
    print(f"  ROI: {best_res.get('roi_pct', 0):.1f}%")
    print(f"  Win Rate: {best_res.get('win_rate', 0)*100:.1f}%")
    print(f"  Sharpe Ratio: {best_res.get('sharpe_ratio', 0):.2f}")
    print(f"  Profit Factor: {best_res.get('profit_factor', 0):.2f}")
    print(f"  Max Drawdown: Rs {abs(best_res.get('max_drawdown', 0)):,.2f}")

    # Save
    output_path = ROOT_DIR / "outputs" / "final_best_strategy.json"
    with open(output_path, "w") as f:
        json.dump(
            {"best_strategy": best_result, "score": best["score"], "top_10": scored_results[:10]},
            f,
            indent=2,
            default=str,
        )

    print(f"\n\nBest strategy saved to: {output_path}")

    return best_result


if __name__ == "__main__":
    select_best_strategy()
