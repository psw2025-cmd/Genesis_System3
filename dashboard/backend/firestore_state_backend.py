"""Firestore persistence for the dashboard runtime state.

The dependency is imported lazily so local development and unit tests continue
working without Google credentials.  One Firestore transaction merges each
write with the current remote document, preserving fields produced by bounded
worker jobs while maintaining a monotonic state version.
"""

from __future__ import annotations

import copy
import hashlib
import base64
import re
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


def _json_clone(value: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(value, default=str))


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)


class FirestoreStateBackend:
    """Transactional shared state document used by Cloud Run services/jobs."""

    def __init__(
        self,
        project: Optional[str] = None,
        collection: Optional[str] = None,
        document: Optional[str] = None,
        *,
        client: Any = None,
        transactional: Optional[Callable] = None,
    ) -> None:
        project = project or os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        collection = collection or os.environ.get("SYSTEM3_FIRESTORE_COLLECTION", "system3_runtime")
        document = document or os.environ.get("SYSTEM3_FIRESTORE_DOCUMENT", "state")
        if "/" in collection or "/" in document:
            raise ValueError("Firestore collection/document names must not contain '/'")

        if client is None:
            from google.cloud import firestore  # Imported only in Firestore mode.

            client = firestore.Client(project=project)
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("transactional wrapper is required with an injected Firestore client")

        self.client = client
        self.document_ref = client.collection(collection).document(document)
        self._transactional = transactional

    def load(self) -> Optional[Dict[str, Any]]:
        snapshot = self.document_ref.get()
        if not getattr(snapshot, "exists", False):
            return None
        data = snapshot.to_dict() or {}
        return _json_clone(data)

    def save(self, state: Dict[str, Any]) -> Dict[str, Any]:
        incoming = _json_clone(state)

        @self._transactional
        def _persist(transaction):
            snapshot = self.document_ref.get(transaction=transaction)
            existing = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            existing = _json_clone(existing or {})
            merged = copy.deepcopy(existing)
            _deep_merge(merged, incoming)

            existing_version = int(existing.get("state_version", 0) or 0)
            incoming_version = int(incoming.get("state_version", 0) or 0)
            merged["state_version"] = (
                incoming_version if incoming_version > existing_version else existing_version + 1
            )
            merged["firestore_updated_at_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            transaction.set(self.document_ref, merged)
            return merged

        return _persist(self.client.transaction())


class FirestoreSchedulerEvidenceBackend:
    """Narrow scheduler evidence/lease documents, separate from runtime state."""

    ALLOWED_KEYS = {"schema_version", "observed_at_utc", "resources", "jobs", "artifacts", "summary"}
    MAX_BYTES = 200_000
    MAX_FUTURE_SKEW_SECONDS = 60

    def __init__(self, project: Optional[str] = None, collection: str = "system3_scheduler_evidence", *, client: Any = None, transactional: Optional[Callable] = None, clock: Optional[Callable[[], datetime]] = None) -> None:
        if "/" in collection:
            raise ValueError("Firestore collection name must not contain '/'")
        project = project or os.environ.get("SYSTEM3_FIRESTORE_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if client is None:
            from google.cloud import firestore
            client = firestore.Client(project=project)
            transactional = transactional or firestore.transactional
        if transactional is None:
            raise ValueError("transactional wrapper is required with an injected Firestore client")
        self.client = client
        self.collection = client.collection(collection)
        self._transactional = transactional
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("scheduler evidence clock must return an aware datetime")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _parse_utc(value: str) -> datetime:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return parsed.astimezone(timezone.utc)

    def load_current(self) -> Optional[Dict[str, Any]]:
        snapshot = self.collection.document("current").get()
        return _json_clone(snapshot.to_dict() or {}) if getattr(snapshot, "exists", False) else None

    _BUSINESS_LANES = frozenset({"rank", "forecast", "signals", "validate"})
    _CLOSURE_REASON_CODES = frozenset({"WEEKEND", "EXCHANGE_HOLIDAY", "MARKET_SESSION_CLOSED"})
    _PENDING_REASON_CODES = frozenset({
        "UNKNOWN_CALENDAR",
        "VALIDATED_FORECAST_MODEL_NOT_CONFIGURED",
        "VALIDATION_NO_PREDICTIONS",
        "VALIDATION_ACTUALS_UNAVAILABLE",
        "VALIDATION_BLOCKED",
    })

    def load_artifact(self, lane: str) -> Optional[Dict[str, Any]]:
        if lane not in self._BUSINESS_LANES:
            raise ValueError("invalid business artifact lane")
        snapshot = self.collection.document(f"artifact_{lane}").get()
        return _json_clone(snapshot.to_dict() or {}) if getattr(snapshot, "exists", False) else None

    def upsert_validation_day(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Persist one Spearman validation day for gate accumulation (durable across deploys)."""
        incoming = _json_clone(report)
        day = str(incoming.get("date") or "").strip()
        try:
            parsed = datetime.strptime(day, "%Y-%m-%d").date()
            if parsed.isoformat() != day:
                raise ValueError("date roundtrip mismatch")
        except Exception as exc:
            raise ValueError("validation day date invalid") from exc
        rho = incoming.get("rank_correlation_spearman", incoming.get("spearman_correlation"))
        try:
            rho_f = float(rho)
        except (TypeError, ValueError) as exc:
            raise ValueError("validation day rho invalid") from exc
        if incoming.get("error") and rho_f == 0.0:
            raise ValueError("validation day error reports are not durable evidence")
        stored = {
            "schema_version": 1,
            "date": day,
            "rank_correlation_spearman": rho_f,
            "spearman_correlation": rho_f,
            "hit_rate": incoming.get("match_rate_top3", incoming.get("hit_rate")),
            "grade": incoming.get("grade"),
            "predicted_top_symbols": incoming.get("predicted_top_symbols") or [],
            "actual_top_symbols": incoming.get("actual_top_symbols") or [],
            "source": incoming.get("source") or "market_result_validator",
            "validated_at": incoming.get("validated_at") or self._now().isoformat().replace("+00:00", "Z"),
            "updated_at_utc": self._now().isoformat().replace("+00:00", "Z"),
        }
        day_ref = self.collection.document(f"validation_day_{day}")
        index_ref = self.collection.document("validation_days_index")

        @self._transactional
        def _persist(transaction):
            day_ref_snap = day_ref.get(transaction=transaction)
            index_snap = index_ref.get(transaction=transaction)
            existing_day = day_ref_snap.to_dict() if getattr(day_ref_snap, "exists", False) else {}
            if existing_day and float(existing_day.get("rank_correlation_spearman", 0)) == rho_f:
                stored_out = _json_clone(existing_day)
            else:
                stored_out = stored
                transaction.set(day_ref, stored_out)
            index = index_snap.to_dict() if getattr(index_snap, "exists", False) else {}
            dates = [str(d) for d in (index.get("dates") or []) if str(d)]
            if day not in dates:
                dates.append(day)
            dates = sorted(set(dates))
            transaction.set(index_ref, {"schema_version": 1, "dates": dates, "updated_at_utc": stored["updated_at_utc"]})
            return stored_out

        return _persist(self.client.transaction())

    def list_validation_days(self) -> list:
        index_snap = self.collection.document("validation_days_index").get()
        if not getattr(index_snap, "exists", False):
            return []
        dates = [str(d) for d in ((index_snap.to_dict() or {}).get("dates") or []) if str(d)]
        rows = []
        for day in dates:
            snap = self.collection.document(f"validation_day_{day}").get()
            if getattr(snap, "exists", False):
                rows.append(_json_clone(snap.to_dict() or {}))
        return rows

    def publish_artifact(self, lane: str, artifact: Dict[str, Any]) -> Dict[str, Any]:
        if lane not in self._BUSINESS_LANES:
            raise ValueError("invalid business artifact lane")
        incoming = _json_clone(artifact)
        allowed = {"schema_version", "lane", "run_id", "produced_at_utc", "business_date", "status", "reason_code", "payload", "source_sha256", "code_sha256", "output_sha256", "output_bytes_b64"}
        if set(incoming) - allowed or incoming.get("schema_version") != 1 or incoming.get("lane") != lane or not incoming.get("run_id"):
            raise ValueError("invalid business artifact schema")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", str(incoming["run_id"])):
            raise ValueError("business artifact run_id invalid")
        try:
            parsed_date = datetime.strptime(str(incoming["business_date"]), "%Y-%m-%d").date()
            if parsed_date.isoformat() != incoming["business_date"]:
                raise ValueError("date roundtrip mismatch")
        except Exception as exc:
            raise ValueError("business artifact date invalid") from exc
        reason_code = incoming.get("reason_code")
        if reason_code not in {None, *self._CLOSURE_REASON_CODES, *self._PENDING_REASON_CODES}:
            raise ValueError("business artifact reason_code invalid")
        status = incoming.get("status")
        closure_codes = self._CLOSURE_REASON_CODES
        pending_codes = self._PENDING_REASON_CODES
        if not ((status == "PASS" and reason_code is None) or (status == "SKIPPED" and reason_code in closure_codes) or (status == "PENDING" and reason_code in pending_codes)):
            raise ValueError("business artifact status/reason_code incoherent")
        produced = self._parse_utc(incoming.get("produced_at_utc", ""))
        if abs((self._now() - produced).total_seconds()) > 3600:
            raise ValueError("business artifact timestamp outside publish window")
        try:
            output_bytes = base64.b64decode(incoming.get("output_bytes_b64", ""), validate=True)
        except Exception as exc:
            raise ValueError("business artifact bytes invalid") from exc
        if len(json.dumps(incoming, separators=(",", ":"), default=str).encode("utf-8")) > 800_000:
            raise ValueError("business artifact exceeds size limit")
        digest = hashlib.sha256(output_bytes).hexdigest()
        if incoming.get("output_sha256") != digest:
            raise ValueError("business artifact output hash mismatch")
        ref = self.collection.document(f"artifact_{lane}")
        @self._transactional
        def _persist(transaction):
            existing_snapshot = ref.get(transaction=transaction)
            existing = existing_snapshot.to_dict() if getattr(existing_snapshot, "exists", False) else {}
            if existing and self._parse_utc(existing["produced_at_utc"]) > produced:
                raise ValueError("business artifact time regressed")
            if existing and existing.get("business_date") == incoming.get("business_date") and existing.get("output_sha256") == digest:
                return _json_clone(existing)
            stored = {**incoming, "artifact_version": int(existing.get("artifact_version", 0) or 0) + 1}
            # Immutable content-addressed history; exact retries address the
            # same document and cannot overwrite a different payload.
            history_ref = self.collection.document(f"artifact_{lane}_{incoming['business_date'].replace('-', '')}_{incoming['run_id']}")
            history = history_ref.get(transaction=transaction)
            if getattr(history, "exists", False):
                if (history.to_dict() or {}) != stored:
                    raise ValueError("immutable business artifact run already exists")
            else:
                create = getattr(transaction, "create", None)
                if create is None:
                    raise RuntimeError("Firestore transaction create is required for immutable history")
                create(history_ref, stored)
            transaction.set(ref, stored)
            return _json_clone(stored)
        return _persist(self.client.transaction())

    def verify_artifact(self, lane: str, *, now: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        artifact = self.load_artifact(lane)
        if not artifact:
            return None
        required = {"schema_version", "lane", "run_id", "produced_at_utc", "business_date", "status", "payload", "source_sha256", "code_sha256", "output_sha256", "output_bytes_b64", "artifact_version"}
        if artifact.get("schema_version") != 1 or artifact.get("lane") != lane or not required.issubset(artifact):
            raise ValueError("business artifact full schema invalid")
        if artifact.get("status") not in {"PASS", "PENDING", "SKIPPED"}:
            raise ValueError("business artifact status invalid")
        for field in ("source_sha256", "code_sha256", "output_sha256"):
            if not isinstance(artifact.get(field), str) or re.fullmatch(r"[0-9a-f]{64}", artifact[field]) is None:
                raise ValueError(f"business artifact {field} invalid")
        raw = base64.b64decode(artifact["output_bytes_b64"], validate=True)
        if hashlib.sha256(raw).hexdigest() != artifact["output_sha256"]:
            raise ValueError("business artifact stored bytes hash mismatch")
        produced = self._parse_utc(artifact["produced_at_utc"])
        trusted_now = (now or self._now()).astimezone(timezone.utc)
        if produced > trusted_now or (trusted_now - produced).total_seconds() > 98 * 3600:
            raise ValueError("business artifact freshness invalid")
        history_name = f"artifact_{lane}_{str(artifact['business_date']).replace('-', '')}_{artifact['run_id']}"
        history = self.collection.document(history_name).get()
        if not getattr(history, "exists", False) or (history.to_dict() or {}) != artifact:
            raise ValueError("business artifact immutable history identity mismatch")
        payload = artifact.get("payload") or {}
        return {key: artifact.get(key) for key in ("lane", "run_id", "business_date", "produced_at_utc", "status", "reason_code", "source_sha256", "code_sha256", "output_sha256", "artifact_version")} | {"verified": True}

    def publish(self, evidence: Dict[str, Any], *, owner: str, fence: int) -> Dict[str, Any]:
        incoming = _json_clone(evidence)
        if incoming.get("schema_version") != 1 or set(incoming) - self.ALLOWED_KEYS:
            raise ValueError("invalid scheduler evidence schema")
        observed = self._parse_utc(incoming.get("observed_at_utc", ""))
        canonical = json.dumps(incoming, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(canonical) > self.MAX_BYTES:
            raise ValueError("scheduler evidence exceeds size limit")
        validation_now = self._now()
        if observed.timestamp() > validation_now.timestamp() + self.MAX_FUTURE_SKEW_SECONDS:
            raise ValueError("scheduler evidence observation is too far in the future")
        incoming["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
        ref = self.collection.document("current")
        lease_ref = self.collection.document("collector_lease")

        @self._transactional
        def _persist(transaction):
            commit_now = self._now()
            lease_snapshot = lease_ref.get(transaction=transaction)
            lease = lease_snapshot.to_dict() if getattr(lease_snapshot, "exists", False) else {}
            if lease.get("owner") != owner or int(lease.get("fence", 0)) != int(fence):
                raise PermissionError("scheduler collector lease owner/fence mismatch")
            if self._parse_utc(lease["expires_at_utc"]) <= commit_now:
                raise PermissionError("scheduler collector lease expired")
            snapshot = ref.get(transaction=transaction)
            existing = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            if existing:
                previous = self._parse_utc(existing["observed_at_utc"])
                if observed < previous:
                    raise ValueError("scheduler evidence observation regressed")
                if observed == previous:
                    if existing.get("evidence_sha256") != incoming["evidence_sha256"]:
                        raise ValueError("conflicting scheduler evidence for identical observation")
                    return _json_clone(existing)
            stored = {**incoming, "evidence_version": int(existing.get("evidence_version", 0) or 0) + 1}
            transaction.set(ref, stored)
            return _json_clone(stored)

        return _persist(self.client.transaction())

    def acquire_lease(self, owner: str, ttl_seconds: int) -> Dict[str, Any]:
        if not owner or not (1 <= int(ttl_seconds) <= 900):
            raise ValueError("invalid scheduler collector lease")
        # owner must be the unique Cloud Run execution name, never a static job name.
        ref = self.collection.document("collector_lease")

        @self._transactional
        def _acquire(transaction):
            commit_now = self._now()
            snapshot = ref.get(transaction=transaction)
            current = snapshot.to_dict() if getattr(snapshot, "exists", False) else {}
            active = bool(current and self._parse_utc(current["expires_at_utc"]) > commit_now)
            if active and current.get("owner") != owner:
                return {"acquired": False, "owner": current.get("owner"), "fence": int(current.get("fence", 0)), "expires_at_utc": current.get("expires_at_utc")}
            fence = int(current.get("fence", 0))
            if not active or current.get("owner") != owner:
                fence += 1
            expires = commit_now.timestamp() + int(ttl_seconds)
            value = {"owner": owner, "fence": fence, "acquired_at_utc": commit_now.isoformat().replace("+00:00", "Z"), "expires_at_utc": datetime.fromtimestamp(expires, timezone.utc).isoformat().replace("+00:00", "Z")}
            transaction.set(ref, value)
            return {"acquired": True, **value}

        return _acquire(self.client.transaction())


def derive_scheduler_health(evidence: Optional[Dict[str, Any]], *, now: Optional[datetime] = None) -> Dict[str, Any]:
    """Derive health only from stored raw facts; producer status is never trusted."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    reasons = []
    if not evidence:
        return {"healthy": False, "status": "UNHEALTHY", "unhealthy_reasons": ["scheduler evidence missing"]}
    try:
        age = (now - FirestoreSchedulerEvidenceBackend._parse_utc(evidence["observed_at_utc"])).total_seconds()
        if age < -60 or age > 180:
            reasons.append(f"scheduler evidence stale or future-dated: age_seconds={age:.0f}")
    except Exception:
        reasons.append("scheduler evidence timestamp invalid")
    expected_contract = {
        "genesis-system3-forecast-daily": ("ENABLED", "genesis-system3-forecast", "0 4 * * MON-FRI", "UTC", 98),
        "genesis-system3-rank-daily": ("ENABLED", "genesis-system3-rank", "45 3 * * MON-FRI", "UTC", 98),
        "genesis-system3-signals-daily": ("ENABLED", "genesis-system3-signals", "15 13 * * MON-FRI", "UTC", 98),
        "genesis-system3-dhan-token-rotate-daily": ("ENABLED", "genesis-system3-dhan-token-rotate", "30 7 * * *", "Asia/Kolkata", 26),
        "genesis-system3-forecast-schedule": ("PAUSED", None, "0 4,5,6,7,8,9 * * 1-5", "UTC", None),
        "genesis-system3-rank-schedule": ("PAUSED", None, "50 3 * * 1-5", "UTC", None),
        "genesis-system3-signals-schedule": ("PAUSED", None, "0 10 * * 1-5", "UTC", None),
        "genesis-system3-scheduler-collector-every-minute": ("ENABLED", "genesis-system3-scheduler-collector", "* * * * *", "UTC", 1),
    }
    resources = evidence.get("resources") if isinstance(evidence.get("resources"), list) else []
    names = [row.get("name") for row in resources if isinstance(row, dict)]
    if len(names) != len(set(names)):
        reasons.append("duplicate scheduler resource names")
    missing = sorted(set(expected_contract) - set(names)); extras = sorted(set(names) - set(expected_contract))
    if missing or extras:
        reasons.append(f"scheduler identity mismatch: missing={missing} extras={extras}")
    enabled = [row for row in resources if row.get("state") == "ENABLED"]
    paused = [row for row in resources if row.get("state") == "PAUSED"]
    workload = [row for row in resources if row.get("name") != "genesis-system3-scheduler-collector-every-minute"]
    control = [row for row in resources if row.get("name") == "genesis-system3-scheduler-collector-every-minute"]
    if len(resources) != 8 or len(workload) != 7 or len(control) != 1 or len(enabled) != 5 or len(paused) != 3:
        reasons.append(f"scheduler coverage mismatch: workload={len(workload)} control={len(control)} total={len(resources)} enabled={len(enabled)} paused={len(paused)} expected=7/1/8/5/3")
    for row in resources:
        expected = expected_contract.get(row.get("name"))
        actual = (row.get("state"), row.get("target_job") if row.get("state") == "ENABLED" else None, row.get("schedule"), row.get("time_zone"))
        if expected and actual != expected[:4]:
            reasons.append(f"scheduler contract mismatch: {row.get('name')}")
        if row.get("state") == "ENABLED":
            if row.get("target_type") != "http":
                reasons.append(f"scheduler target type invalid: {row.get('name')}")
            if row.get("target_uri_valid") is not True:
                reasons.append(f"scheduler target URI invalid: {row.get('name')}")
            if int(row.get("delivery_status_code", 0) or 0) != 0:
                reasons.append(f"scheduler delivery failed: {row.get('name')} code={row.get('delivery_status_code')}")
    job_rows = evidence.get("jobs") if isinstance(evidence.get("jobs"), list) else []
    job_names = [row.get("name") for row in job_rows if isinstance(row, dict)]
    if len(job_names) != len(set(job_names)):
        reasons.append("duplicate Cloud Run job facts")
    jobs = {row.get("name"): row for row in job_rows if isinstance(row, dict)}
    for resource in enabled:
        target = resource.get("target_job")
        fact = jobs.get(target)
        if not fact:
            reasons.append(f"enabled scheduler target missing: {target}")
        elif fact.get("completion_status") != "EXECUTION_SUCCEEDED":
            reasons.append(f"enabled scheduler target failed: {target}={fact.get('completion_status') or 'UNKNOWN'}")
        else:
            try:
                if not resource.get("last_attempt_time") or not fact.get("create_time") or not fact.get("completion_time"):
                    raise ValueError("missing required timestamps")
                attempt = FirestoreSchedulerEvidenceBackend._parse_utc(resource["last_attempt_time"])
                created = FirestoreSchedulerEvidenceBackend._parse_utc(fact["create_time"])
                completed = FirestoreSchedulerEvidenceBackend._parse_utc(fact["completion_time"])
                max_age_hours = expected_contract[resource["name"]][4]
                if attempt > now.replace(microsecond=0) or completed > now.replace(microsecond=0):
                    reasons.append(f"scheduler/execution timestamp materially future: {target}")
                elif resource["name"] == "genesis-system3-scheduler-collector-every-minute":
                    if completed < created or (now - attempt).total_seconds() > 180 or (now - completed).total_seconds() > 300:
                        reasons.append("collector control continuity stale")
                elif created < attempt or completed < created:
                    reasons.append(f"latest execution not linked to scheduler attempt: {target}")
                elif max_age_hours is not None and ((now - attempt).total_seconds() > max_age_hours * 3600 or (now - completed).total_seconds() > max_age_hours * 3600):
                    reasons.append(f"enabled scheduler execution stale beyond cadence grace: {target}")
            except Exception:
                reasons.append(f"scheduler/execution timestamps invalid: {target}")
    readiness_reasons = []
    artifact_rows = evidence.get("artifacts") if isinstance(evidence.get("artifacts"), list) else []
    lane_names = [row.get("lane") for row in artifact_rows if isinstance(row, dict)]
    if len(lane_names) != len(set(lane_names)):
        readiness_reasons.append("duplicate business artifact lanes")
    by_lane = {row.get("lane"): row for row in artifact_rows if isinstance(row, dict)}
    current_ist_date = now.astimezone(__import__("zoneinfo").ZoneInfo("Asia/Kolkata")).date().isoformat()
    for lane in ("rank", "forecast", "signals"):
        artifact = by_lane.get(lane)
        if not artifact:
            readiness_reasons.append(f"business artifact missing: {lane}")
        elif artifact.get("verified") is not True:
            readiness_reasons.append(f"business artifact unverified: {lane}")
        elif artifact.get("business_date") != current_ist_date:
            readiness_reasons.append(f"business artifact wrong date: {lane}")
        elif artifact.get("status") != "PASS":
            readiness_reasons.append(f"business lane not ready: {lane}={artifact.get('status')}")
    closure_codes = {"WEEKEND", "EXCHANGE_HOLIDAY", "MARKET_SESSION_CLOSED"}
    closed = len(by_lane) == 3 and all(row.get("verified") is True and row.get("status") == "SKIPPED" and row.get("reason_code") in closure_codes and row.get("business_date") == current_ist_date for row in by_lane.values())
    unknown_calendar = any(row.get("reason_code") == "UNKNOWN_CALENDAR" for row in by_lane.values())
    return {
        "healthy": not reasons,
        "transport_healthy": not reasons,
        "status": "HEALTHY" if not reasons else "UNHEALTHY",
        "business_readiness": "BLOCKED" if unknown_calendar else ("NOT_APPLICABLE" if closed else ("READY" if not readiness_reasons else ("PARTIAL" if artifact_rows else "PENDING"))),
        "business_readiness_reasons": readiness_reasons,
        "unhealthy_reasons": reasons,
        "observed_at_utc": evidence.get("observed_at_utc"),
        "evidence_version": evidence.get("evidence_version"),
        "evidence_sha256": evidence.get("evidence_sha256"),
        "resources": resources,
        "jobs": list(jobs.values()),
        "artifacts": artifact_rows,
        "coverage": {"workload": len(workload), "control": len(control), "total": len(resources), "enabled": len(enabled), "paused": len(paused), "expected_total": 8},
    }
