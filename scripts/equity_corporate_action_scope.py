"""Flag official corporate-action exposure; never invent adjusted returns."""
from datetime import date, datetime
from hashlib import sha256
import json
from urllib.parse import urlparse, parse_qs


def capture(raw: bytes, receipt: dict) -> dict:
    source = urlparse(receipt["source_url"])
    params = parse_qs(source.query)
    if (source.scheme != "https" or source.netloc != "www.nseindia.com"
            or source.path != "/api/corporates-corporateActions"
            or params.get("index") != ["equities"]
            or receipt["raw_sha256"] != sha256(raw).hexdigest()):
        raise ValueError("Unbound official corporate-action source")
    observed = datetime.fromisoformat(receipt["first_observed_at"].replace("Z", "+00:00"))
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError("Observation timestamp requires timezone")
    start = datetime.strptime(params["from_date"][0], "%d-%m-%Y").date()
    end = datetime.strptime(params["to_date"][0], "%d-%m-%Y").date()
    rows = json.loads(raw)
    if not isinstance(rows,list) or not rows or end < start:
        raise ValueError("Empty or invalid action interval")
    by_symbol,by_isin,seen = {},{},set()
    for row in rows:
        day = datetime.strptime(row["exDate"],"%d-%b-%Y").date()
        symbol,isin = row["symbol"].strip(),row["isin"].strip()
        if not start <= day <= end or not symbol or not isin:
            raise ValueError("Action date or identity outside source scope")
        digest = sha256(json.dumps(row,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        item = dict(row,record_sha256=digest,ex_date=day.isoformat())
        by_symbol.setdefault(symbol,[]).append(item)
        by_isin.setdefault(isin,[]).append(item)
    return dict(start=start,end=end,source_sha256=receipt["raw_sha256"],by_symbol=by_symbol,
                by_isin=by_isin,unique_records=len(seen),raw_records=len(rows),
                historical_feature_availability="NOT_PROVEN",complete_action_coverage=False)


def review(scope: dict, symbol: str, isin: str, decision: date, outcome: date) -> dict:
    if outcome <= decision:
        raise ValueError("Outcome must follow decision")
    candidates = scope["by_symbol"].get(symbol,[]) + scope["by_isin"].get(isin,[])
    found = {r["record_sha256"]:r for r in candidates
             if decision < date.fromisoformat(r["ex_date"]) <= outcome}
    identity_review = any(r["isin"] != isin for r in found.values())
    covered = scope["start"] <= decision and outcome <= scope["end"]
    return dict(action_count=len(found),events=list(found.values()),
                identity_link_review_required=identity_review,requested_interval_covered=covered,
                status="ACTION_OR_IDENTITY_REVIEW_REQUIRED" if found else "NO_MATCH_IN_CAPTURE_COVERAGE_NOT_PROVEN",
                source_sha256=scope["source_sha256"],adjusted_return_proven=False,
                use_as_historical_prediction_feature_allowed=False)
