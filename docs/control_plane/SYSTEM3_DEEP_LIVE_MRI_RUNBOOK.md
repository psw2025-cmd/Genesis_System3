# System3 Deep Live MRI — Read-Only Forensic Runbook

Authority: GitHub `main` for code and GCP production for runtime. This collector is read-only and is not runtime authority by itself.

## Purpose

Collect repeated production API samples, HTTP response headers, latency, cross-sample content hashes, robust latency anomalies, DNS/TCP/TLS evidence, rendered browser DOM/screenshot when Chrome/Edge is available, and public GitHub main/Issue #188/status snapshots. The result is a single ZIP suitable for cross-verification against governed GitHub/GCP workflow evidence.

## Safety contract

The script performs only GET/read operations. It does not deploy, rotate Dhan credentials, mutate Secret Manager, change IAM, invoke orders, or enable LIVE trading. PAPER/read-only safeguards remain unchanged.

## Canonical script

`scripts/system3_deep_live_mri.ps1`

## Recommended user invocation

Run from Windows PowerShell or VS Code PowerShell terminal:

```powershell
$u='https://raw.githubusercontent.com/psw2025-cmd/Genesis_System3/docs/deep-live-mri-forensic-kit-20260830/scripts/system3_deep_live_mri.ps1';$p='C:\Temp\System3_Deep_Live_MRI.ps1';Invoke-WebRequest -Uri $u -OutFile $p -UseBasicParsing;& $p
```

The script creates `C:\Temp\System3_DEEP_MRI_<timestamp>.zip`. Upload that ZIP for analysis.

## Evidence produced

- 5 samples by default, 20 seconds apart.
- Production endpoints including health/state/deploy info/broker/auto-gates/P&L/accuracy/instruments and four required option chains.
- Additional discovery probes for market, scanner, alerts, paper, model, and storage endpoint contracts. Missing endpoints are preserved as errors rather than treated as success.
- HTTP status, response time, response headers, response bytes.
- Cross-sample SHA-256 change detector.
- Robust median/MAD-style latency anomaly detector.
- DNS, TCP 443, traceroute, and TLS certificate evidence.
- Static `/ui` shell and, where possible, a headless browser screenshot plus rendered DOM.
- Public GitHub main, Issue #188, and commit-status snapshots.
- Endpoint consensus CSV and complete SHA-256 manifest.

## Analysis priorities

Cross-verify repeated evidence and focus on defects reproduced across independent surfaces. Highest priority clusters are: exact GitHub↔GCP revision binding; broker REST↔UI parity; WebSocket/stream state; model/version/training lineage; prediction→actual metric lineage; PAPER ledger vs synthetic/demo data; instrument-universe reconciliation; storage durability/readback; option-chain freshness; request amplification/latency; and terminal 22-tab semantics.

## Acceptance rule

Do not convert this laptop-side capture into runtime authority. It is supplementary evidence only. Final PASS still requires exact-current-main governed GCP evidence and truthful live production UI proof, with market-session proof where freshness depends on an open India market session.
