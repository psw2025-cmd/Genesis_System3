# P1 Security Remediation (2026-02-28)

Based on governance scan and pip-audit results.

## Upgraded (4 packages → 4 vulns eliminated)

| Package | Before | After | CVE / Fix |
|---------|--------|-------|-----------|
| duckdb | 0.9.2 | 1.4.4 | CVE-2024-22682, CVE-2024-41672 |
| pyarrow | 14.0.2 | 23.0.1 | CVE-2024-52338 (deserialization RCE) |
| pillow | 10.4.0 | 12.1.1 | CVE-2026-25990 (PSD out-of-bounds write) |
| streamlit | 1.37.0 | 1.54.0 | Required for pillow 12.x compatibility |

## Blocked (4 packages, 9 vulns)

| Package | Version | Fix | Blocker |
|---------|---------|-----|---------|
| flask | 3.0.3 | 3.1.3 | dash 2.x requires Flask<3.1 |
| werkzeug | 3.0.6 | 3.1.6 | dash 2.x requires Werkzeug<3.1 |
| keras | 2.15.0 | 3.11+ | tensorflow 2.15 pins keras 2.15 |
| protobuf | 4.25.8 | 5.29.6+ | tensorflow pins protobuf 4.25.x |

## Mitigations for Blocked Packages

- **flask/werkzeug**: Upgrade when dash 3.x is released with Flask 3.1+ support. Until then, avoid session caching behind proxies; set `Cache-Control: private` where appropriate.
- **keras**: Do not load untrusted `.keras` model files. Use `safe_mode=True` when loading models from external sources (mitigation is partial).
- **protobuf**: Avoid parsing untrusted protobuf with `json_format.ParseDict`; limit recursion depth where possible.

## Verification

```powershell
pip check
pip-audit
```

**Result:** 9 vulns in 4 packages (down from 13 in 7). All remaining blocked by tensorflow 2.15 / dash 2.x.
