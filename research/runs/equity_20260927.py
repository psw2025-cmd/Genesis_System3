"""Reproduce the two-year raw EQ-series evidence, without issuing forecasts.

Run from the repository root:
  PYTHONPATH=. python research/runs/equity_20260927.py DATA_DIR SOURCE_DIR OUTPUT
SOURCE_DIR contains corporate_actions_2years.json and its .receipt.json.
"""
from collections import Counter
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
import sys

from scripts.equity_horizon_replay import parse, replay
from scripts.equity_corporate_action_scope import capture


def run(folder, sources):
    snapshots = []
    for path in sorted(folder.glob("????????_cm_bhavcopy.csv")):
        day = datetime.strptime(path.name[:8], "%Y%m%d").date()
        if not date(2024, 9, 26) <= day <= date(2026, 9, 25):
            continue
        raw = path.read_bytes()
        receipt = json.loads(path.with_suffix(".receipt.json").read_text())
        expected = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{day:%Y%m%d}_F_0000.csv.zip"
        if (receipt["csv_sha256"] != sha256(raw).hexdigest()
                or receipt["date"] != day.isoformat() or receipt["segment"] != "CM"
                or receipt["source"] != expected or not receipt.get("zip_sha256")
                or not receipt.get("first_observed_at")):
            raise ValueError(f"Unbound source receipt: {path.name}")
        snapshots.append((day, raw))
    receipt = json.loads((sources / "corporate_actions_2years.json.receipt.json").read_text())
    raw_actions = (sources / "corporate_actions_2years.json").read_bytes()
    action_scope = capture(raw_actions, receipt)
    result = replay(snapshots, corporate_action_scope=action_scope)
    parsed = {day.isoformat(): parse(raw, day) for day, raw in snapshots}
    summaries = {str(h): Counter() for h in (7, 14, 365)}
    values = {str(h): [] for h in (7, 14, 365)}
    for decision in result["decisions"]:
        before = parsed[decision["decision_date"]]
        # Verify the baseline's immutable selection digest before reconstructing
        # its descriptive distribution. This is not a second selection rule.
        keys = sorted((k for k, v in before.items() if v["volume"] >= 10000 and v["price"] >= 10),
                      key=lambda k: (-before[k]["volume"], k))[:20]
        if sha256(json.dumps(keys, separators=(",", ":")).encode()).hexdigest() != decision["selected_keys_sha256"]:
            raise ValueError("Baseline selection changed")
        for horizon, outcome in decision["horizons"].items():
            summary = summaries[horizon]
            if outcome["status"] != "UNADJUSTED_RESEARCH_ONLY":
                summary["missing_target_session_decisions"] += 1
                continue
            after = parsed[outcome["observed_date"]]
            multiples = [after[k]["price"] / before[k]["price"] for k in keys if k in after]
            if len(multiples) != outcome["matched"] or sum(m >= 2 for m in multiples) != outcome["at_least_2x"]:
                raise ValueError("Replay outcome disagrees with raw observations")
            values[horizon].extend(multiples)
            review = outcome["corporate_action_review"]
            summary.update(dict(scored_decision_dates=1, selected=outcome["selected"],
                matched=outcome["matched"], unmatched=outcome["delisted_or_missing"],
                raw_at_least_2x=outcome["at_least_2x"],
                positive_references=sum(m > 1 for m in multiples),
                negative_references=sum(m < 1 for m in multiples),
                unchanged_references=sum(m == 1 for m in multiples),
                matched_with_corporate_action_events=review["matched_with_events"],
                unmatched_with_events=review["unmatched_with_events"],
                identity_reviews=review["identity_links_requiring_review"]))
    summary_out = {}
    for horizon, counter in summaries.items():
        ordered = sorted(values[horizon])
        def quantile(q):
            if not ordered:
                return None
            i = (len(ordered) - 1) * q
            low = int(i)
            return ordered[low] + (ordered[min(low + 1, len(ordered)-1)] - ordered[low]) * (i-low)
        summary_out[horizon] = dict(counter,
            raw_mean_return_pct=mean((m-1)*100 for m in ordered) if ordered else None,
            raw_multiple_quantiles={str(q): quantile(q) for q in (0, .05, .25, .5, .75, .95, 1)},
            raw_multiples_sha256=sha256(json.dumps(ordered, separators=(",", ":")).encode()).hexdigest())
    return dict(task_id="EQ-HISTORY-006", evidence_at=datetime.now(timezone.utc).isoformat(),
        implementation_commit="bd74880c2cb0f1dde7d6c24c41a621fdc1de5d1c",
        source_dates=[snapshots[0][0].isoformat(), snapshots[-1][0].isoformat()],
        source_files=len(snapshots), action_receipt=receipt, action_records=action_scope["raw_records"],
        summary=summary_out, replay=result, qualified_candidates=0, forward_predictions=0,
        forward_outcomes=0, adjusted_multibagger_results="NOT_PROVEN",
        source_scope="Mixed EQ-series raw research, not company-only equity validation",
        classification_and_actions_complete=False, source_available_at_historical_issue="NOT_PROVEN",
        executable_cost_net_performance="NOT_PROVEN", qualified_oos_trades=0,
        qualified_oos_days=0, orders_allowed=False)


if __name__ == "__main__":
    folder, sources, output = map(Path, sys.argv[1:])
    report = run(folder, sources)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "replay"}, indent=2))
