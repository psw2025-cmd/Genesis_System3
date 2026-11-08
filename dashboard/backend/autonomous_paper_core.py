"""PAPER-only autonomous event ledger, gap detector, recovery, reconciliation and learning.

No broker imports, no order placement, no live-model promotion. Every price/fill
created here remains SIMULATED until independent outcome evidence exists.
SQLite must reside on a durable, single-writer filesystem for cross-revision
recovery; an ephemeral filesystem only proves process-restart recovery.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


GENESIS = "0" * 64
FILL_MODE = "SIMULATED_PAPER_FILL_NOT_BROKER"
CAPITAL_LIMIT_INR = 50_000.0


def estimate_costed_paper_pnl(entry: float, exit_price: float, qty: int) -> float:
    """Conservative estimated broker-style charges, NOT verified actual costs."""
    buy = _positive(entry, "ENTRY_PRICE")
    sell = _positive(exit_price, "EXIT_PRICE")
    size = _positive(qty, "QTY")
    if int(size) != size:
        raise PaperEvidenceError("NONINTEGER_PAPER_QUANTITY")
    gross = (sell - buy) * size
    entry_value, exit_value = buy * size, sell * size
    brokerage = 40.0
    stt = exit_value * 0.000625
    exchange = (entry_value + exit_value) * 0.0005
    gst = (brokerage + exchange) * 0.18
    slippage = (entry_value + exit_value) * 0.001
    return round(gross - (brokerage + stt + exchange + gst + slippage), 2)



class PaperEvidenceError(ValueError):
    """A corrupt or inconsistent PAPER history must block new paper actions."""


def _stamp(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise PaperEvidenceError("INVALID_EVENT_TIME") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise PaperEvidenceError("EVENT_TIME_REQUIRES_TIMEZONE")
    return result


def _positive(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PaperEvidenceError("INVALID_" + field)
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise PaperEvidenceError("INVALID_" + field)
    return value


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise PaperEvidenceError("INVALID_EVENT_PAYLOAD") from exc


def detect_opening_gap(*, session: str, previous_close: float, opening_price: float,
                       opened_at: str, source: str, threshold_pct: float = 0.5) -> dict:
    """Compare the actual session OPEN to the prior session CLOSE, never LTP."""
    if not session or not source or source.upper().startswith(("SYNTHETIC", "REPLAY")):
        raise PaperEvidenceError("MISSING_REAL_GAP_PROVENANCE")
    if _stamp(opened_at).date().isoformat() != session:
        # A UTC timestamp can be a day earlier than an IST session; callers
        # must provide an exchange-local ISO timestamp for this comparison.
        raise PaperEvidenceError("GAP_SESSION_MISMATCH")
    previous = _positive(previous_close, "PREVIOUS_CLOSE")
    opening = _positive(opening_price, "OPENING_PRICE")
    threshold = _positive(threshold_pct, "GAP_THRESHOLD")
    percent = round((opening / previous - 1.0) * 100, 4)
    classification = "GAP_UP" if percent >= threshold else ("GAP_DOWN" if percent <= -threshold else "FLAT")
    return {"session": session, "previous_close": previous,
            "opening_price": opening, "gap_pct": percent, "direction": classification,
            "opened_at": opened_at, "source": source,
            "verification_status": "SOURCE_REPORTED_NOT_INDEPENDENTLY_VERIFIED"}


class MasterPaperLedger:
    """Single-writer, hash-chained event log. Projection files are not authority."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                trade_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                payload TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL UNIQUE)""")

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=20)
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    @staticmethod
    def _digest(event_id: str, trade_id: str, kind: str, timestamp: str,
                payload: str, previous: str) -> str:
        return hashlib.sha256(_canonical([event_id, trade_id, kind, timestamp,
                                           payload, previous]).encode("utf-8")).hexdigest()

    def _verified_events(self, db: sqlite3.Connection) -> list[dict]:
        previous = GENESIS
        results = []
        for seq, eid, trade, kind, timestamp, payload, prior, digest in db.execute(
            "SELECT seq,event_id,trade_id,event_type,timestamp_utc,payload,"
            "previous_hash,event_hash FROM events ORDER BY seq"
        ):
            try:
                doc = json.loads(payload)
                _stamp(timestamp)
            except (ValueError, TypeError) as exc:
                raise PaperEvidenceError("CORRUPT_PAPER_LEDGER") from exc
            if prior != previous or digest != self._digest(
                eid, trade, kind, timestamp, payload, prior
            ):
                raise PaperEvidenceError("PAPER_LEDGER_HASH_MISMATCH")
            results.append({"seq": seq, "event_id": eid, "trade_id": trade,
                            "type": kind, "at": timestamp, "data": doc})
            previous = digest
        return results

    @staticmethod
    def _project(events: list[dict]) -> dict:
        trades: dict[str, dict] = {}
        gaps: dict[str, dict] = {}
        outcomes: dict[str, dict] = {}
        legacy_unverified = False
        for event in events:
            trade, kind, data = event["trade_id"], event["type"], event["data"]
            if kind == "LEGACY_SNAPSHOT":
                if trades:
                    raise PaperEvidenceError("LEGACY_SNAPSHOT_ORDER_INVALID")
                for row in data["open"] + data["closed"]:
                    key = str(row["position_id"])
                    if key in trades:
                        raise PaperEvidenceError("DUPLICATE_LEGACY_POSITION")
                    trades[key] = dict(row, legacy_unverified=True)
                legacy_unverified = True
            elif kind == "GAP_OBSERVED":
                gaps[trade] = data
            elif kind == "PAPER_POSITION_OPENED":
                if trade in trades:
                    raise PaperEvidenceError("DUPLICATE_PAPER_OPEN")
                trades[trade] = dict(data["position"])
            elif kind == "PAPER_POSITION_MARKED":
                if trade not in trades or trades[trade].get("status") == "CLOSED":
                    raise PaperEvidenceError("MARK_WITHOUT_OPEN")
                trades[trade].update(data["mark"])
            elif kind == "PAPER_POSITION_CLOSED":
                if trade not in trades or trades[trade].get("status") == "CLOSED":
                    raise PaperEvidenceError("CLOSE_WITHOUT_OPEN")
                trades[trade] = dict(data["position"])
            elif kind == "OUTCOME_RECORDED":
                if trade not in trades or trades[trade].get("status") != "CLOSED":
                    raise PaperEvidenceError("OUTCOME_WITHOUT_CLOSE")
                outcomes[trade] = data
            elif kind in ("PAPER_ORDER_CREATED", "PAPER_ENTRY_FILL",
                          "PAPER_EXIT_FILL", "LEARNING_PROPOSED"):
                continue
            else:
                raise PaperEvidenceError("UNKNOWN_PAPER_EVENT_TYPE")
        opened = [x for x in trades.values() if x.get("status") != "CLOSED"]
        closed = [x for x in trades.values() if x.get("status") == "CLOSED"]
        return {"open_positions": opened, "closed_positions": closed,
                "gaps": gaps, "outcomes": outcomes, "legacy_unverified": legacy_unverified,
                "event_count": len(events), "verified_hash_chain": True}

    def snapshot(self) -> dict:
        with self._db() as db:
            return self._project(self._verified_events(db))

    def append_batch(self, records: list[tuple[str, str, str, str, Mapping[str, Any]]]) -> bool:
        """Commit a complete order/fill/position transition atomically."""
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            events = self._verified_events(db)
            self._project(events)  # State-machine check BEFORE any writes.
            seen = {e["event_id"]: e for e in events}
            pending = []
            for eid, trade, kind, timestamp, data in records:
                _stamp(timestamp)
                if not eid or not trade or not kind:
                    raise PaperEvidenceError("MISSING_EVENT_IDENTITY")
                encoded = _canonical(dict(data))
                if eid in seen:
                    previous = seen[eid]
                    if (previous["trade_id"], previous["type"], previous["at"],
                        _canonical(previous["data"])) != (trade, kind, timestamp, encoded):
                        raise PaperEvidenceError("CONFLICTING_DUPLICATE_PAPER_EVENT")
                    continue
                if eid in (x[0] for x in pending):
                    raise PaperEvidenceError("DUPLICATE_EVENT_WITHIN_BATCH")
                pending.append((eid, trade, kind, timestamp, encoded))
            if len(pending) not in (0, len(records)):
                raise PaperEvidenceError("PARTIAL_PAPER_TRANSITION")
            previous_hash = db.execute(
                "SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            tip = previous_hash[0] if previous_hash else GENESIS
            for eid, trade, kind, timestamp, encoded in pending:
                digest = self._digest(eid, trade, kind, timestamp, encoded, tip)
                db.execute("INSERT INTO events(event_id,trade_id,event_type,timestamp_utc,"
                           "payload,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?)",
                           (eid, trade, kind, timestamp, encoded, tip, digest))
                tip = digest
            self._project(self._verified_events(db))  # Reject invalid transitions.
            return bool(pending)

    def import_legacy_once(self, opened: list[dict], closed: list[dict], timestamp: str) -> None:
        """Retain old evidence but NEVER upgrade it to verified fills."""
        if not (opened or closed):
            return
        if self.snapshot()["event_count"]:
            return
        for row in opened + closed:
            if not isinstance(row, dict) or not row.get("position_id"):
                raise PaperEvidenceError("INVALID_LEGACY_POSITION")
        self.append_batch([("legacy-import-v1", "_migration", "LEGACY_SNAPSHOT", timestamp,
                            {"open": opened, "closed": closed,
                             "verification_status": "LEGACY_UNVERIFIED"})])

    def record_gap(self, symbol: str, gap: dict) -> bool:
        return self.append_batch([("gap:" + gap["session"] + ":" + symbol, symbol,
                                   "GAP_OBSERVED", gap["opened_at"], gap)])

    def record_open(self, position: dict, at: str) -> bool:
        trade = str(position["position_id"])
        price = _positive(position["entry_price"], "ENTRY_PRICE")
        qty = _positive(position["qty"], "QTY")
        if int(qty) != qty:
            raise PaperEvidenceError("NONINTEGER_PAPER_QUANTITY")
        state = self.snapshot()
        if any(p.get("legacy_unverified") for p in state["open_positions"]):
            raise PaperEvidenceError("LEGACY_RECONCILIATION_REQUIRED")
        if sum(float(p["entry_price"]) * float(p["qty"])
               for p in state["open_positions"]) + price * qty > CAPITAL_LIMIT_INR:
            raise PaperEvidenceError("PAPER_CUMULATIVE_CAPITAL_LIMIT")
        entry = dict(position, status="OPEN", entry_price=price,
                     paper_fill_mode=FILL_MODE, evidence_status="SIMULATED_NOT_MARKET_VERIFIED")
        return self.append_batch([
            (trade + ":order", trade, "PAPER_ORDER_CREATED", at,
             {"qty": int(qty), "entry_price": price, "broker_order": False}),
            (trade + ":entry", trade, "PAPER_ENTRY_FILL", at,
             {"qty": int(qty), "fill_price": price, "mode": FILL_MODE}),
            (trade + ":open", trade, "PAPER_POSITION_OPENED", at, {"position": entry}),
        ])

    def record_mark(self, position: dict, at: str) -> bool:
        trade = str(position["position_id"])
        _positive(position["current_price"], "MARK_PRICE")
        # Repeated ticks must be idempotent; caller timestamps every market tick.
        return self.append_batch([(
            trade + ":mark:" + at, trade, "PAPER_POSITION_MARKED", at,
            {"mark": {"current_price": float(position["current_price"]),
                      "unrealized_pnl": position.get("unrealized_pnl"),
                      "ltp": position.get("ltp")}}
        )])

    def record_close(self, position: dict, at: str) -> bool:
        trade = str(position["position_id"])
        _positive(position["exit_price"], "EXIT_PRICE")
        closed = dict(position, status="CLOSED", paper_fill_mode=FILL_MODE,
                      pnl_verification_status="COSTED_SIMULATION_NOT_BROKER_VERIFIED")
        expected = estimate_costed_paper_pnl(
            float(closed["entry_price"]), float(closed["exit_price"]), int(closed["qty"]))
        reported = closed.get("realized_pnl")
        if reported is None or not isinstance(reported, (int, float)) or (
            not math.isfinite(float(reported)) or abs(float(reported) - expected) > 0.011
        ):
            raise PaperEvidenceError("PAPER_NET_PNL_RECONCILIATION_FAILED")
        return self.append_batch([
            (trade + ":exit", trade, "PAPER_EXIT_FILL", at,
             {"fill_price": closed["exit_price"], "qty": closed["qty"], "mode": FILL_MODE}),
            (trade + ":close", trade, "PAPER_POSITION_CLOSED", at, {"position": closed}),
        ])

    def reconcile(self, current_open: list[dict]) -> dict:
        snapshot = self.snapshot()
        ledger_by_id = {p["position_id"]: p for p in snapshot["open_positions"]}
        current_by_id = {p["position_id"]: p for p in current_open}
        matches = set(ledger_by_id) == set(current_by_id)
        if matches:
            matches = all(
                float(ledger_by_id[k].get("entry_price") or 0) ==
                float(current_by_id[k].get("entry_price") or 0)
                and float(ledger_by_id[k].get("qty") or 0) ==
                float(current_by_id[k].get("qty") or 0)
                for k in ledger_by_id
            )
        pending_legacy = any(p.get("legacy_unverified") for p in snapshot["open_positions"])
        return {"status": "PASS" if matches and not pending_legacy else "BLOCKED",
                "projection_matches": matches,
                "master_open_count": len(ledger_by_id),
                "projection_open_count": len(current_by_id),
                "legacy_unverified": snapshot["legacy_unverified"],
                "verified_hash_chain": snapshot["verified_hash_chain"]}

    def record_outcome(self, trade: str, *, reference_price: float, at: str,
                       source: str, reference_id: str | None = None) -> dict:
        """Assess a CLOSED simulated trade against a later, independent market print."""
        price = _positive(reference_price, "OUTCOME_PRICE")
        state = self.snapshot()
        row = next((x for x in state["closed_positions"] if x["position_id"] == trade), None)
        if row is None:
            raise PaperEvidenceError("OUTCOME_REQUIRES_CLOSED_POSITION")
        end = str(row.get("timestamp") or row.get("time_ist") or "")
        if end and "T" in end and _stamp(at) < _stamp(end):
            raise PaperEvidenceError("OUTCOME_PRECEDES_ENTRY")
        verified = source == "INDEPENDENT_EXCHANGE_SNAPSHOT" and bool(reference_id)
        result = {"reference_price": price, "reference_at": at, "reference_source": source,
                  "reference_id": reference_id,
                  "validation_status": "SOURCE_ATTESTED" if verified else "NOT_VERIFIED",
                  "paper_exit_price": row.get("exit_price"),
                  "difference_from_paper_exit": round(price - float(row["exit_price"]), 4)}
        self.append_batch([(
            trade + ":outcome:" + at, trade, "OUTCOME_RECORDED", at, result
        )])
        return result

    def learning_proposal(self, at: str, min_samples: int = 10) -> dict:
        """Compute shadow-only diagnostics, never train/promote on self-labelled fills."""
        if min_samples < 2:
            raise PaperEvidenceError("UNSAFE_LEARNING_MIN_SAMPLES")
        snap = self.snapshot()
        accepted = [p for p in snap["closed_positions"]
                    if snap["outcomes"].get(str(p["position_id"]), {}).get("validation_status")
                    == "SOURCE_ATTESTED" and not p.get("legacy_unverified")]
        accepted.sort(key=lambda p: str(p.get("timestamp") or ""))
        if len(accepted) < min_samples:
            return {"status": "NOT_VERIFIED", "eligible_trades": len(accepted),
                    "reason": "INSUFFICIENT_INDEPENDENT_OUTCOMES",
                    "model_promoted": False}
        split = max(1, int(len(accepted) * .8))
        holdout = accepted[split:]
        if not holdout:
            raise PaperEvidenceError("LEARNING_HOLDOUT_MISSING")
        train = accepted[:split]
        def winrate(rows: list[dict]) -> float:
            return round(sum(float(x.get("realized_pnl") or 0) > 0 for x in rows) /
                         len(rows), 4)
        proposal = {"status": "SHADOW_ONLY", "eligible_trades": len(accepted),
                    "train_count": len(train), "holdout_count": len(holdout),
                    "train_win_rate": winrate(train),
                    "holdout_win_rate": winrate(holdout),
                    "model_promoted": False,
                    "reason": "NO_AUTOMATIC_PRODUCTION_MODEL_PROMOTION"}
        self.append_batch([("learning:" + at, "_learning", "LEARNING_PROPOSED", at, proposal)])
        return proposal
