# Genesis System3 Oracle VM + GitHub Self-Hosted Runner Setup Guide

Date: 2026-06-07

## Goal

Prepare a controllable deployment path where GitHub Actions can deploy Genesis System3 backend to an Oracle Cloud VM through a GitHub self-hosted runner.

## Current prepared repo files

- `docker-compose.oracle.yml`
- `.github/workflows/oracle-selfhosted-deploy.yml`
- `scripts/oracle_bootstrap.sh`
- `scripts/oracle_healthcheck.sh`
- `scripts/oracle_restart.sh`

## Safety status

This setup keeps live trading disabled by default:

- `SYSTEM3_MODE=analyzer`
- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`

No broker API live trading is enabled by these deployment files.

## Manual action required from user

### 1. Create Oracle Cloud account

Create or login to Oracle Cloud.

### 2. Create Always Free Ubuntu VM

Recommended VM:

- Image: Ubuntu 22.04 or 24.04
- Shape: Ampere A1 if available, otherwise a free eligible shape
- Public IPv4: enabled
- SSH key: download/private key saved safely

### 3. Open ingress ports in Oracle Cloud network/security rules

Minimum:

- TCP 22 for SSH
- TCP 8000 for backend test access

Later, for production/domain:

- TCP 80
- TCP 443

### 4. SSH into VM

Use Oracle's SSH instructions for the created VM.

### 5. Run bootstrap script

After cloning or downloading this repo on the VM, run:

```bash
bash scripts/oracle_bootstrap.sh
```

Then reboot or log out/in so Docker group permission activates.

### 6. Add GitHub self-hosted runner

In GitHub repo:

`Settings -> Actions -> Runners -> New self-hosted runner -> Linux`

Use labels:

```text
self-hosted
oracle
system3
```

Run GitHub's displayed runner commands on the Oracle VM.

When the runner screen says connected/listening, reply to ChatGPT:

```text
oracle runner connected
```

## What ChatGPT can do after runner is connected

- Trigger `Oracle VM - Self Hosted Deploy`
- Pull latest backend image from GHCR
- Restart backend container
- Run healthcheck
- Read GitHub Actions logs
- Fix deployment files if any error appears

## What remains manual forever

- Oracle account creation
- VM creation/deletion
- Broker account/API key creation
- Broker TOTP/MPIN/private credentials
- Adding private secrets
- Final approval before any real-money live trading

## First workflow to run after setup

GitHub Actions:

`Oracle VM - Self Hosted Deploy`

Inputs:

- `deploy_backend=true`
- `run_healthcheck=true`

Expected proof:

- `Oracle self-hosted runner preflight PASS`
- backend container `genesis-backend` running
- `HEALTHCHECK_PASS`
