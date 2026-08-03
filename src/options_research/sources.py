"""Official Dhan/NSE historical data sources with resumable manifest writes."""
from __future__ import annotations

import csv
import io
import os
import time
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

import pandas as pd
import requests

from .contracts import RollingRequest, Underlying, flatten_rolling_response, sha256_file, write_frame
from .manifest import Manifest

DHAN_ROLLING_URL = "https://api.dhan.co/v2/charts/rollingoption"
DHAN_DETAILED_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
NSE_NEW_URL = "https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
NSE_OLD_URL = (
    "https://archives.nseindia.com/content/historical/DERIVATIVES/"
    "{year}/{mon}/fo{day}{mon}{year}bhav.csv.zip"
)


def download_security_master(destination: Path, timeout: float = 60.0) -> Path:
    if destination.exists() and destination.stat().st_size > 100:
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(DHAN_DETAILED_MASTER_URL, timeout=timeout)
    response.raise_for_status()
    if len(response.content) < 100 or b"," not in response.content[:500]:
        raise ValueError("DHAN_SECURITY_MASTER_RESPONSE_INVALID")
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(response.content)
    os.replace(temporary, destination)
    return destination


def load_universe(path: Path, exchanges: Sequence[str] = ("NSE", "BSE")) -> list[Underlying]:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"security master missing or empty: {path}")
    allowed = {value.upper() for value in exchanges}
    found: dict[tuple[str, str, str], Underlying] = {}
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        for row in csv.DictReader(handle):
            exchange = (row.get("EXCH_ID") or row.get("SEM_EXM_EXCH_ID") or "").upper().strip()
            segment = (row.get("SEGMENT") or row.get("SEM_SEGMENT") or "").upper().strip()
            instrument = (row.get("INSTRUMENT") or row.get("SEM_INSTRUMENT_NAME") or "").upper().strip()
            if exchange not in allowed or segment not in {"D", "DERIVATIVES"} or instrument not in {"OPTIDX", "OPTSTK"}:
                continue
            symbol = (row.get("UNDERLYING_SYMBOL") or row.get("SYMBOL_NAME") or row.get("SM_SYMBOL_NAME") or "").upper().strip()
            security_id = str(row.get("UNDERLYING_SECURITY_ID") or row.get("SEM_UNDERLYING_SECURITY_ID") or "").strip()
            if not security_id and exchange == "NSE":
                security_id = {"NIFTY": "13", "BANKNIFTY": "25", "FINNIFTY": "27", "MIDCPNIFTY": "442"}.get(symbol, "")
            if symbol and security_id:
                exchange_segment = f"{exchange}_FNO"
                found[(exchange_segment, symbol, instrument)] = Underlying(
                    symbol, security_id, instrument, exchange_segment,
                )
    return sorted(found.values(), key=lambda item: (item.exchange_segment, item.instrument, item.symbol))


def _dhan_error_code(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("errorCode") or payload.get("error_code") or payload.get("code") or "")


def download_dhan(
    plan: Sequence[RollingRequest], data_root: Path, manifest: Manifest, limit: int | None = None,
    delay_seconds: float = 0.25, retries: int = 4,
) -> dict:
    token = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    if not token:
        return {"status": "BLOCKED", "reason": "DHAN_ACCESS_TOKEN_MISSING", "planned_requests": len(plan)}
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json", "Content-Type": "application/json", "access-token": token,
        **({"client-id": client_id} if client_id else {}),
    })
    downloaded = failed = no_data = rows_total = skipped = processed = 0
    for request in plan:
        if manifest.status(request.key) in {"DOWNLOADED", "EXISTS_VALID", "NO_DATA"}:
            skipped += 1
            continue
        if limit is not None and processed >= limit:
            break
        processed += 1
        response = None
        try:
            payload: dict = {}
            for attempt in range(retries):
                response = session.post(DHAN_ROLLING_URL, json=request.payload(), timeout=60)
                try:
                    payload = response.json()
                except ValueError:
                    payload = {}
                code = _dhan_error_code(payload)
                retryable = response.status_code in {429, 500, 502, 503, 504} or code in {"805", "DH-904"}
                if retryable and attempt < retries - 1:
                    time.sleep(max(delay_seconds, 0.25) * (2 ** attempt))
                    continue
                response.raise_for_status()
                if code:
                    raise ValueError(f"DHAN_ERROR_{code}: {payload}")
                break
            frame = flatten_rolling_response(request, payload)
            common = {
                "object_key": request.key, "source": "DHAN_ROLLING", "symbol": request.underlying.symbol,
                "start_date": request.from_date.isoformat(), "end_date": request.to_date.isoformat(),
                "http_status": response.status_code if response else None,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            }
            if frame.empty:
                manifest.upsert(**common, status="NO_DATA", rows=0, bytes=0, sha256="", path="", error="EMPTY_SERIES")
                no_data += 1
                continue
            relative = (
                Path("dhan_rolling") / request.underlying.exchange_segment / request.underlying.instrument
                / request.underlying.symbol / str(request.from_date.year)
            )
            output = write_frame(frame, data_root / relative / f"{request.key}.parquet")
            manifest.upsert(
                **common, status="DOWNLOADED", rows=len(frame), bytes=output.stat().st_size,
                sha256=sha256_file(output), path=str(output), error="",
            )
            downloaded += 1
            rows_total += len(frame)
        except Exception as error:
            manifest.upsert(
                object_key=request.key, source="DHAN_ROLLING", symbol=request.underlying.symbol,
                start_date=request.from_date.isoformat(), end_date=request.to_date.isoformat(), status="FAILED",
                rows=0, bytes=0, sha256="", path="", http_status=response.status_code if response else None,
                error=f"{type(error).__name__}: {str(error)[:500]}", updated_utc=datetime.now(timezone.utc).isoformat(),
            )
            failed += 1
        time.sleep(max(0.0, delay_seconds))
    return {
        "status": "PASS" if failed == 0 else "PARTIAL", "planned_batch": processed,
        "downloaded_requests": downloaded, "skipped": skipped, "no_data": no_data,
        "failed": failed, "rows": rows_total,
    }


def nse_urls(day: date) -> list[str]:
    values = {
        "ymd": day.strftime("%Y%m%d"), "year": day.strftime("%Y"),
        "mon": day.strftime("%b").upper(), "day": day.strftime("%d"),
    }
    return [NSE_NEW_URL.format(**values), NSE_OLD_URL.format(**values)]


def download_nse_eod(start: date, end: date, data_root: Path, manifest: Manifest, limit: int | None = None) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"})
    days = [start + timedelta(days=index) for index in range((end - start).days + 1) if (start + timedelta(days=index)).weekday() < 5]
    downloaded = unavailable = failed = rows_total = skipped = processed = 0
    for day in days:
        key = f"NSE_FO_{day:%Y%m%d}"
        if manifest.status(key) in {"DOWNLOADED", "EXISTS_VALID", "UNAVAILABLE"}:
            skipped += 1
            continue
        if limit is not None and processed >= limit:
            break
        processed += 1
        last_error, http_status = "", None
        for url in nse_urls(day):
            try:
                response = session.get(url, timeout=40)
                http_status = response.status_code
                if http_status == 404:
                    continue
                response.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                    names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                    if not names:
                        raise ValueError("ZIP_CONTAINS_NO_CSV")
                    raw = archive.read(max(names, key=lambda name: archive.getinfo(name).file_size))
                frame = pd.read_csv(io.BytesIO(raw), low_memory=False, on_bad_lines="skip")
                output = write_frame(frame, data_root / "nse_fo_eod" / str(day.year) / f"{day:%Y%m%d}_fo.parquet")
                manifest.upsert(
                    object_key=key, source="NSE_FO_EOD", symbol="ALL", start_date=day.isoformat(), end_date=day.isoformat(),
                    status="DOWNLOADED", rows=len(frame), bytes=output.stat().st_size, sha256=sha256_file(output),
                    path=str(output), http_status=http_status, error="", updated_utc=datetime.now(timezone.utc).isoformat(),
                )
                downloaded += 1
                rows_total += len(frame)
                break
            except Exception as error:
                last_error = f"{type(error).__name__}: {str(error)[:500]}"
        else:
            final_status = "UNAVAILABLE" if http_status == 404 else "FAILED"
            unavailable += int(final_status == "UNAVAILABLE")
            failed += int(final_status == "FAILED")
            manifest.upsert(
                object_key=key, source="NSE_FO_EOD", symbol="ALL", start_date=day.isoformat(), end_date=day.isoformat(),
                status=final_status, rows=0, bytes=0, sha256="", path="", http_status=http_status,
                error=last_error, updated_utc=datetime.now(timezone.utc).isoformat(),
            )
        time.sleep(0.25)
    return {
        "status": "PASS" if failed == 0 else "PARTIAL", "planned_batch": processed,
        "downloaded_days": downloaded, "skipped": skipped, "unavailable_days": unavailable,
        "failed": failed, "rows": rows_total,
    }
