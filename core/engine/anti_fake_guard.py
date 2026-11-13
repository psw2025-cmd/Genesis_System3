# Genesis System3 - Anti-Fake Guard Engine.
from __future__ import annotations
import os, time, hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Tuple

class AntiFakeGuard:
    def __init__(self):
        self.ist_tz = timezone(timedelta(hours=5, minutes=30))

    def is_market_hours(self, dt: Optional[datetime] = None) -> Tuple[bool, str]:
        now_ist = (dt or datetime.now(timezone.utc)).astimezone(self.ist_tz)
        weekday = now_ist.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        if weekday in (5, 6):
            return False, f"EXCHANGE_CLOSED_WEEKEND ({now_ist.strftime('%A')})"
        time_minutes = now_ist.hour * 60 + now_ist.minute
        open_minutes = 9 * 60 + 15    # 09:15 IST
        close_minutes = 15 * 60 + 30  # 15:30 IST
        if time_minutes < open_minutes:
            return False, f"PRE_MARKET_HOURS (Current: {now_ist.strftime('%H:%M')} IST, Opens: 09:15 IST)"
        elif time_minutes > close_minutes:
            return False, f"POST_MARKET_HOURS (Current: {now_ist.strftime('%H:%M')} IST, Closed: 15:30 IST)"
        return True, "EXCHANGE_OPEN_MARKET_HOURS"

    def audit_and_wrap_payload(
        self,
        symbol: str,
        data: Dict[str, Any],
        raw_source: str = "DhanHQ Live Feed",
        is_live_connected: bool = True
    ) -> Dict[str, Any]:
        sym = symbol.upper().strip()
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        is_open, market_reason = self.is_market_hours(now_utc)

        # Anti-Fake Rule 1: If market closed or feed disconnected, NEVER emit fake/stale numbers as live
        is_verified_live = is_open and is_live_connected
        verification_status = "REAL_VERIFIED" if is_verified_live else "NO VERIFIED LIVE DATA"

        # Extract timestamps
        exch_ts = data.get("exchange_timestamp") or data.get("timestamp") or now_iso
        try:
            exch_dt = datetime.fromisoformat(exch_ts.replace("Z", "+00:00"))
            age_s = round((now_utc - exch_dt).total_seconds(), 2)
        except Exception:
            age_s = 0.0

        # Classification assignment
        if is_verified_live:
            classification = "REAL_VERIFIED"
        elif "simulated" in str(data.get("execution_mode", "")).lower():
            classification = "SIMULATED"
        elif "synthetic" in str(data.get("risk_type", "")).lower():
            classification = "SYNTHETIC"
        else:
            classification = "CACHED"

        wrapped = {
            "symbol": sym,
            "verification_status": verification_status,
            "verified": is_verified_live,
            "market_session": {
                "is_open": is_open,
                "reason": market_reason,
                "window": "Mon-Fri 09:15 - 15:30 IST"
            },
            "provenance": {
                "source": raw_source,
                "classification": classification,
                "timestamp": now_iso,
                "exchange_timestamp": exch_ts,
                "age_seconds": max(0.0, age_s)
            },
            "data": data
        }
        return wrapped

anti_fake_guard = AntiFakeGuard()
