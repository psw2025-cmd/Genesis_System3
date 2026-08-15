"""Durable Firestore authority for Genesis System3 PAPER trading.

Cloud Run container files are explicitly NOT an authority: service instances and
jobs are disposable.  This backend keeps the current paper state in Firestore
and writes immutable, content-addressed lifecycle events for audit/recovery.

Safety invariants are enforced on every read/write:
- mode is PAPER
- LIVE trading is false
- broker order endpoints are never called
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Iterable, Optional


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("paper timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _safe_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", raw) is None:
        raise ValueError("paper execution/event id invalid")
    return raw


def paper_event_id(event: Dict[str, Any]) -> str:
    """Stable non-sequential event id; retries address the same Firestore doc."""
    raw = "|".join(
        str(event.get(key) or "")
        for key in ("position_id", "action", "timestamp", "time_ist", "exit_reason")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def summarize_paper_state(state: Dict[str, Any]) -> Dict[str, Any]:
    open_positions = state.get("open_positions") if isinstance(state.get("open_positions"), list) else []
    closed_positions = state.get("closed_positions") if isinstance(state.get("closed_positions"), list) else []
    realized = sum(float(row.get("realized_pnl") or 0) for row in closed_positions if isinstance(row, dict))
    unrealized = sum(float(row.get("unrealized_pnl") or row.get("unrealizedProfit") or 0) for row in open_positions if isinstance(row, dict))
    wins = sum(1 for row in closed_positions if isinstance(row, dict) and float(row.get("realized_pnl") or 0) > 0)
    losses = sum(1 for row in closed_positions if isinstance(row, dict) and float(row.get("realized_pnl") or 0) <= 0)
    total = wins + losses
    return {
        "open_count": len(open_positions),
        "closed_count": len(closed_positions),
        "total_trades": total,
        "winning_trades": wins,
        "losing_trades": losses,
        "win_rate": round(wins / total * 100.0, 2) if total else 0.0,
        "total_realized_pnl": round(realized, 2),
        "total_unrealized_pnl": round(unrealized, 2),
        "total_pnl": round(realized + unrealized, 2),
        "open_positions": len(open_positions),
        "mode": "PAPER",
        "live_trading_enabled": False,
    }


class FirestorePaperLedgerBackend:
    """Transactional single-writer paper ledger with immutable event history."""

    SCHEMA_VERSION = 1
    MAX_CURRENT_BYTES = 850_000
    MAX_RECENT_EVENTS = 500
    MAX_CLOSED_IN_CURRENT = 500
    MAX_FUTURE_SKEW_SECONDS = 60

    def __init__(
        self,
        project: Optional[str] = None,
        collection: Optional[str] = None,
        *,
        client: Any = None,
        transactional: Optional[Callable] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        project = project or os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        collection = collection or os.environ.get("SYSTEM3_PAPER_COLLECTION", "system3_paper_ledger")
        if "/" in collection:
            raise ValueError("Firestore paper collection name must not contain '/'")
        if client is None:
            from google.cloud import firestore

            client = firestore.Client(project=project)
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("transactional wrapper is required with an injected Firestore client")
        self.client = client
        self.collection = client.collection(collection)
        self.collection_name = collection
        self._transactional = transactional
        self._clock = clock or _utc_now

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("paper ledger clock must return aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _enforce_safety(state: Dict[str, Any]) -> Dict[str, Any]:
        out = _clone(state or {})
        out["mode"] = "PAPER"
        out["live_trading_enabled"] = False
        out["broker_order_endpoints_called"] = False
        return out

    def load_current(self) -> Optional[Dict[str, Any]]:
        snap = self.collection.document("current").get()
        if not getattr(snap, "exists", False):
            return None
        data = self._enforce_safety(snap.to_dict() or {})
        if int(data.get("schema_version", 0) or 0) != self.SCHEMA_VERSION:
            raise ValueError("paper ledger schema invalid")
        return data

    def acquire_lease(self, owner: str, ttl_seconds: int = 55) -> Dict[str, Any]:
        owner = _safe_id(owner)
        ttl_seconds = max(10, min(int(ttl_seconds), 55))
        ref = self.collection.document("writer_lease")

        @self._transactional
        def _acquire(transaction):
            now = self._now()
            snap = ref.get(transaction=transaction)
            existing = snap.to_dict() if getattr(snap, "exists", False) else {}
            existing_owner = str((existing or {}).get("owner") or "")
            expires_raw = str((existing or {}).get("expires_at_utc") or "")
            try:
                expires = _parse_utc(expires_raw) if expires_raw else datetime.min.replace(tzinfo=timezone.utc)
            except Exception:
                expires = datetime.min.replace(tzinfo=timezone.utc)
            if existing_owner and existing_owner != owner and expires > now:
                return {
                    "acquired": False,
                    "owner": existing_owner,
                    "fence": int((existing or {}).get("fence", 0) or 0),
                    "expires_at_utc": _iso_utc(expires),
                }
            fence = int((existing or {}).get("fence", 0) or 0)
            if existing_owner != owner or expires <= now:
                fence += 1
            value = {
                "owner": owner,
                "fence": fence,
                "acquired_at_utc": _iso_utc(now),
                "expires_at_utc": _iso_utc(now + timedelta(seconds=ttl_seconds)),
                "live_trading_enabled": False,
            }
            transaction.set(ref, value)
            return {"acquired": True, **value}

        return _acquire(self.client.transaction())

    def _validate_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        value = self._enforce_safety(snapshot)
        value["schema_version"] = self.SCHEMA_VERSION
        value.setdefault("open_positions", [])
        value.setdefault("closed_positions", [])
        value.setdefault("recent_events", [])
        if not isinstance(value["open_positions"], list) or not isinstance(value["closed_positions"], list):
            raise ValueError("paper positions must be lists")
        if not isinstance(value["recent_events"], list):
            raise ValueError("paper recent_events must be list")
        value["closed_positions"] = value["closed_positions"][-self.MAX_CLOSED_IN_CURRENT :]
        value["recent_events"] = value["recent_events"][-self.MAX_RECENT_EVENTS :]
        updated = str(value.get("updated_at_utc") or _iso_utc(self._now()))
        parsed = _parse_utc(updated)
        if (parsed - self._now()).total_seconds() > self.MAX_FUTURE_SKEW_SECONDS:
            raise ValueError("paper snapshot timestamp materially future")
        value["updated_at_utc"] = _iso_utc(parsed)
        value["summary"] = summarize_paper_state(value)
        value["data_source"] = str(value.get("data_source") or "DHAN_LIVE_MARK_TO_MARKET")
        raw = json.dumps(value, separators=(",", ":"), sort_keys=True, default=str).encode("utf-8")
        if len(raw) > self.MAX_CURRENT_BYTES:
            raise ValueError("paper current snapshot exceeds Firestore safe size")
        return value

    def publish(
        self,
        snapshot: Dict[str, Any],
        *,
        owner: str,
        fence: int,
        events: Iterable[Dict[str, Any]] = (),
    ) -> Dict[str, Any]:
        owner = _safe_id(owner)
        incoming = self._validate_snapshot(snapshot)
        event_rows = []
        for raw in events:
            if not isinstance(raw, dict):
                continue
            event = self._enforce_safety(raw)
            event["event_id"] = str(event.get("event_id") or paper_event_id(event))
            _safe_id(event["event_id"])
            event["schema_version"] = self.SCHEMA_VERSION
            event_rows.append(event)

        current_ref = self.collection.document("current")
        lease_ref = self.collection.document("writer_lease")
        event_refs = [(self.collection.document(f"event_{row['event_id']}"), row) for row in event_rows]

        @self._transactional
        def _persist(transaction):
            now = self._now()
            # Firestore requires reads before writes. Read every document first.
            lease_snap = lease_ref.get(transaction=transaction)
            current_snap = current_ref.get(transaction=transaction)
            event_snaps = [(ref, row, ref.get(transaction=transaction)) for ref, row in event_refs]

            lease = lease_snap.to_dict() if getattr(lease_snap, "exists", False) else {}
            if str((lease or {}).get("owner") or "") != owner or int((lease or {}).get("fence", 0) or 0) != int(fence):
                raise PermissionError("paper writer lease owner/fence mismatch")
            if _parse_utc(str((lease or {}).get("expires_at_utc") or "1970-01-01T00:00:00Z")) <= now:
                raise PermissionError("paper writer lease expired")

            existing = current_snap.to_dict() if getattr(current_snap, "exists", False) else {}
            existing_version = int((existing or {}).get("ledger_version", 0) or 0)
            incoming_updated = _parse_utc(incoming["updated_at_utc"])
            if existing and str(existing.get("updated_at_utc") or ""):
                previous_updated = _parse_utc(existing["updated_at_utc"])
                if incoming_updated < previous_updated:
                    raise ValueError("paper ledger time regressed")
            stored = copy.deepcopy(incoming)
            stored["ledger_version"] = existing_version + 1
            stored["ledger_source"] = "FIRESTORE_PAPER_LEDGER"
            stored["firestore_updated_at_utc"] = _iso_utc(now)
            stored["writer_execution"] = owner
            stored["writer_fence"] = int(fence)

            for ref, row, snap in event_snaps:
                if getattr(snap, "exists", False):
                    existing_event = self._enforce_safety(snap.to_dict() or {})
                    if existing_event != row:
                        raise ValueError("immutable paper event conflict")
                else:
                    create = getattr(transaction, "create", None)
                    if create is None:
                        raise RuntimeError("Firestore transaction create required for paper history")
                    create(ref, row)
            transaction.set(current_ref, stored)
            return _clone(stored)

        return _persist(self.client.transaction())

    def public_snapshot(self) -> Dict[str, Any]:
        current = self.load_current()
        if not current:
            return {
                "status": "EMPTY",
                "mode": "PAPER",
                "engine": "cloud_paper_firestore_v1",
                "positions_source": "FIRESTORE_PAPER_LEDGER",
                "data_source": "PENDING_FIRST_DURABLE_PAPER_TICK",
                "positions": {"positions": [], "open_positions": [], "open_count": 0},
                "pnl": {"summary": summarize_paper_state({}), "closed_positions": []},
                "trades": {"entries": [], "exits": [], "count": 0},
                "paper_truth": {
                    "ledger_source": "FIRESTORE_PAPER_LEDGER",
                    "durable": True,
                    "ledger_version": 0,
                    "displayed_rows": 0,
                    "broker_order_endpoints_called": False,
                    "order_endpoints_label": "INTENTIONALLY_NOT_CALLED_PAPER_SAFE",
                    "message": "Durable paper ledger is ready; no paper lifecycle event has been persisted yet.",
                },
                "broker_order_endpoints_called": False,
                "live_trading_enabled": False,
            }

        opens = current.get("open_positions") or []
        closed = current.get("closed_positions") or []
        recent = current.get("recent_events") or []
        session_date = str(current.get("session_date") or "")
        entries = [row for row in recent if isinstance(row, dict) and str(row.get("action") or "").upper() == "OPEN" and (not session_date or session_date in str(row.get("timestamp") or row.get("time_ist") or ""))]
        exits = [row for row in recent if isinstance(row, dict) and str(row.get("action") or "").upper() == "CLOSE" and (not session_date or session_date in str(row.get("timestamp") or row.get("time_ist") or ""))]
        summary = current.get("summary") if isinstance(current.get("summary"), dict) else summarize_paper_state(current)
        return {
            "status": "ok",
            "mode": "PAPER",
            "engine": "cloud_paper_firestore_v1",
            "positions_source": "FIRESTORE_PAPER_LEDGER",
            "data_source": current.get("data_source") or "DHAN_LIVE_MARK_TO_MARKET",
            "positions": {"positions": opens, "open_positions": opens, "open_count": len(opens)},
            "pnl": {"summary": summary, "closed_positions": closed},
            "trades": {"entries": entries, "exits": exits, "count": len(entries) + len(exits)},
            "paper_truth": {
                "ledger_source": "FIRESTORE_PAPER_LEDGER",
                "durable": True,
                "ledger_version": int(current.get("ledger_version", 0) or 0),
                "session_date": session_date or None,
                "updated_at_utc": current.get("updated_at_utc"),
                "firestore_updated_at_utc": current.get("firestore_updated_at_utc"),
                "writer_execution": current.get("writer_execution"),
                "displayed_rows": len(opens),
                "history_events_cached": len(recent),
                "broker_order_endpoints_called": False,
                "order_endpoints_label": "INTENTIONALLY_NOT_CALLED_PAPER_SAFE",
                "mark_to_market": "DHAN_OPTION_CHAIN_LTP",
            },
            "broker_order_endpoints_called": False,
            "live_trading_enabled": False,
        }
