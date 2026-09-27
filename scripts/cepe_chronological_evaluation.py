"""Frozen CEPE-NEXT-005 retrospective splits, with all uncapped outcomes.

No parameter tuning or forward prediction. Multi-date gaps need an official
session calendar, so only adjacent calendar dates are evaluated here.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import random
from statistics import mean

from scripts.cepe_range_liquidity_baseline import evaluate


def distribution(values: list[float]) -> dict:
    ordered = sorted(values)
    def quantile(q):
        if not ordered:
            return None
        position = (len(ordered)-1)*q
        low = int(position)
        high = min(low+1, len(ordered)-1)
        return ordered[low] + (ordered[high]-ordered[low])*(position-low)
    return dict(count=len(ordered), mean=mean(ordered) if ordered else None,
        quantiles={str(q):quantile(q) for q in (0,.01,.05,.25,.5,.75,.95,.99,1)},
        thresholds={str(n):sum(x >= n for x in ordered) for n in (3,10,20,30)},
        full_uncapped_distribution_sha256=sha256(json.dumps(ordered,separators=(",", ":")).encode()).hexdigest())


def split_pairs(files: list[Path], start: date, end: date):
    dated = sorted((datetime.strptime(p.name[:8], "%Y%m%d").date(),p) for p in files)
    pairs, gaps = [], []
    for (before,a),(after,b) in zip(dated,dated[1:]):
        if not (start <= before < after <= end):
            continue
        if (after-before).days == 1:
            pairs.append((before,a,after,b))
        else:
            gaps.append(dict(previous_day=before.isoformat(),following_day=after.isoformat(),
                             status="NOT_PROVEN_NO_COMPLETE_SESSION_CALENDAR"))
    return pairs,gaps


def verified(path: Path) -> bytes:
    raw = path.read_bytes()
    receipt = json.loads(path.with_suffix(".receipt.json").read_text())
    day = datetime.strptime(path.name[:8],"%Y%m%d").date()
    source = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{day:%Y%m%d}_F_0000.csv.zip"
    if (receipt["csv_sha256"] != sha256(raw).hexdigest() or receipt["segment"] != "FO"
            or receipt["date"] != day.isoformat() or receipt["source"] != source
            or not receipt.get("first_observed_at") or not receipt.get("zip_sha256")):
        raise ValueError("Unverified source bytes or dated receipt")
    return raw


def source_scope(folder: Path, start: date, end: date, manifest: Path | None = None) -> dict:
    """Bind requested dates to archived receipts before a full-period replay.

    Directory-only runs remain useful subsets but cannot claim full acquisition
    coverage. A 404 is retained as a missing source, never inferred as a holiday.
    """
    files = {datetime.strptime(p.name[:8], "%Y%m%d").date(): p
             for p in folder.glob("????????_fo_bhavcopy.csv")
             if start <= datetime.strptime(p.name[:8], "%Y%m%d").date() <= end}
    scope = dict(source_files=len(files), first_available_date=min(files).isoformat() if files else None,
                 last_available_date=max(files).isoformat() if files else None,
                 status="UNVERIFIED_DIRECTORY_SUBSET", acquisition_manifest_verified=False,
                 market_calendar_complete=False, missing_dates_are_holidays=False)
    if manifest is None:
        return scope
    raw = manifest.read_bytes()
    entries = json.loads(gzip.decompress(raw) if manifest.suffix == ".gz" else raw)
    requested = {start + timedelta(days=i) for i in range((end-start).days+1)}
    rows = {}
    for row in entries:
        day = date.fromisoformat(row["date"])
        if row["segment"] == "FO" and day in requested:
            if day in rows:
                raise ValueError("Duplicate date in source manifest")
            rows[day] = row
    if set(rows) != requested:
        raise ValueError("Source manifest does not account for every requested date")
    expected = {day for day,r in rows.items() if r["status"] in {"downloaded", "already_present"}}
    if any(r["status"] not in {"downloaded", "already_present", "source_404"} for r in rows.values()):
        raise ValueError("Unresolved acquisition error in source manifest")
    if set(files) != expected:
        raise ValueError("Directory differs from acquisition manifest; missing or unexpected source files")
    for day,path in files.items():
        if sha256(verified(path)).hexdigest() != rows[day]["csv_sha256"]:
            raise ValueError("Source bytes differ from acquisition manifest")
    return dict(scope, status="ARCHIVED_ACQUISITION_SCOPE_VERIFIED", acquisition_manifest_verified=True,
                manifest_sha256=sha256(raw).hexdigest(), requested_calendar_dates=len(requested),
                source_404_dates=sum(r["status"] == "source_404" for r in rows.values()))


def run(folder: Path, start: date, end: date, phase: str, *, source_manifest: Path | None = None) -> dict:
    scope = source_scope(folder, start, end, source_manifest)
    pairs,gaps = split_pairs(list(folder.glob("????????_fo_bhavcopy.csv")),start,end)
    daily,errors,population = [],[],[]
    samples = {key:[] for key in ("variant","same_universe_momentum")}
    counts = {key:Counter() for key in samples}
    count_keys = ("selected","scoreable","unscoreable","hits","false_picks","missed_events",
                  "positive_returns","negative_returns","unchanged_returns")
    for index,(before,a,after,b) in enumerate(pairs):
        try:
            result = evaluate(verified(a),verified(b),before,after)
        except (ValueError,KeyError,OSError) as exc:
            errors.append(dict(previous_day=before.isoformat(),following_day=after.isoformat(),
                               error=str(exc),status="EXCLUDED_SOURCE_OR_IDENTITY_ERROR"))
            continue
        population.extend(result["uncapped_eligible_multiples"])
        result["population_distribution"] = distribution(result.pop("uncapped_eligible_multiples"))
        for key in samples:
            samples[key].extend(result[key].pop("reference_multiples"))
            counts[key].update({k:result[key][k] for k in count_keys})
        daily.append(result)
        if (index+1)%20 == 0:
            print(json.dumps(dict(phase=phase,evaluated=index+1,pairs=len(pairs))),flush=True)
    summary = {}
    for key,values in samples.items():
        n = len(values)
        direction = sum(x>1 for x in values)/n*100 if n else None
        precision = sum(x>=3 for x in values)/n*100 if n else None
        summary[key] = dict(counts[key],distribution=distribution(values),
            gross_reference_mean_return_pct=mean((x-1)*100 for x in values) if n else None,
            assumed_cost_stress_mean_return_pct={str(bps):mean((x-1)*100-bps/100 for x in values) if n else None for bps in (0,25,50,100)},
            raw_reference_directional_hit_pct=direction,raw_3x_event_precision_pct=precision,
            reference_gap_to_65pct_directional_gate=None if direction is None else 65-direction,
            reference_gap_to_70pct_3x_precision_gate=None if precision is None else 70-precision)
    differences = [d["variant"]["gross_reference_mean_return_pct"]-d["same_universe_momentum"]["gross_reference_mean_return_pct"]
                   for d in daily if d["variant"]["scoreable"] and d["same_universe_momentum"]["scoreable"]]
    rng = random.Random(20260926)
    boot = sorted(mean(rng.choices(differences,k=len(differences))) for _ in range(10000)) if differences else []
    uncertainty = dict(paired_session_mean_excess_pct=mean(differences) if differences else None,
        paired_day_bootstrap_95pct_interval=[boot[249],boot[9749]] if boot else None,
        positive_excess_days=sum(x>0 for x in differences),negative_excess_days=sum(x<0 for x in differences),
        bootstrap_seed=20260926,resamples=10000,
        limitations="Day bootstrap does not correct serial dependence or selection across earlier experiments. Contract observations are not independent.")
    return dict(task_id="CEPE-NEXT-005",phase=phase,start=start.isoformat(),end=end.isoformat(),
        generated_at=datetime.now(timezone.utc).isoformat(),
        registration_commit="1cf0f9d731e3d3bebaa2f496484c0cb56646732f",
        strategy_implementation_commit="85e1c444c6c247aa468f009e83a61dc97929b287",
        evaluated_session_pairs=len(daily),source_scope=scope,skipped_calendar_gaps=gaps,excluded_errors=errors,
        summary=summary,uncertainty=uncertainty,population_distribution=distribution(population),daily=daily,
        multiple_precision="Six decimal reference multiples from frozen comparator; no capping",
        negative_forecasts_issued=0,forward_predictions=0,forward_outcomes=0,
        calibrated_expected_range=None,source_availability_at_historical_issue="NOT_PROVEN",
        executable_cost_net_performance="NOT_PROVEN",project_qualified_oos_trades=0,project_qualified_oos_days=0,
        gap_to_100_qualified_oos_trades=100,gap_to_60_qualified_oos_days=60,
        project_sharpe="NOT_PROVEN",project_max_drawdown="NOT_PROVEN",project_deflated_sharpe="NOT_PROVEN",
        numeric_reference_metrics_are_project_gate_pass=False,catalyst_ablation="NO_CATALYST_BASELINE_ONLY",
        orders_allowed=False,status="RETROSPECTIVE_REFERENCE_ONLY")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("folder",type=Path)
    p.add_argument("phase",choices=["development","validation","frozen_retrospective_test"])
    p.add_argument("output",type=Path)
    p.add_argument("--source-manifest",type=Path,
                   help="Require a complete acquisition manifest and every archived FO source in the phase")
    args = p.parse_args()
    registry = json.loads(Path("research/experiments/cepe_range_liquidity_v1.json").read_text())
    start,end = map(date.fromisoformat,registry["data_plan"][args.phase])
    result = run(args.folder,start,end,args.phase,source_manifest=args.source_manifest)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"daily","skipped_calendar_gaps"}},indent=2))


if __name__ == "__main__":
    main()
