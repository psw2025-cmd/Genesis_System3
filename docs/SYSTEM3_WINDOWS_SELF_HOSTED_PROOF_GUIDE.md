# System3 Windows Self-Hosted Full Proof Guide

This project now has a Windows self-hosted proof workflow:

```text
.github/workflows/system3-windows-self-hosted-full-proof.yml
```

It runs on:

```yaml
runs-on: [self-hosted, Windows, X64]
```

## Purpose

Render pipeline minutes are exhausted, so the project needs visible proof that does not depend on Render build minutes. This workflow runs on the local Windows GitHub runner and produces:

```text
reports/latest/windows_self_hosted_full_system_proof/summary.json
reports/latest/windows_self_hosted_full_system_proof/summary.md
reports/latest/windows_self_hosted_full_system_proof/index.html
```

## What it proves

- Windows runner identity
- Python/Node availability
- System3 gate evaluator
- auto coordinator
- GitHub + Render failure tracker
- dashboard visible issue tracker
- autopilot proof board
- backend HTTP endpoints
- broker/Dhan read-only endpoints
- simulation endpoint
- paper/system reports

## What it does NOT do

- It does not enable live trading.
- It does not place broker orders.
- It does not hide red blockers.
- It does not treat simulation as real production proof.

## Safety defaults

```text
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
ANALYZE_MODE=1
```

## Runner setup required on Windows

On the Windows machine where the GitHub runner is installed, verify:

```powershell
python --version
node --version
git --version
```

The runner must appear online in GitHub:

```text
Repo → Settings → Actions → Runners → self-hosted Windows X64 runner = Online
```

## How to run manually

Go to GitHub:

```text
Actions → System3 Windows Self-Hosted Full Proof → Run workflow
```

## How to read result

Open:

```text
reports/latest/windows_self_hosted_full_system_proof/index.html
```

Final status meanings:

```text
PASS    = all checked proof gates passed
BLOCKED = at least one real blocker remains
```

A BLOCKED result is not failure of the proof system. It means proof correctly found a blocker.
