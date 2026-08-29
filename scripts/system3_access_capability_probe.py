#!/usr/bin/env python3
"""System3 / Cursor / Claude CLI access capability probe.

Writes a redacted report of what credentials and tools are available so humans
can grant missing access. Never prints secret values.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PRIMARY = Path(r"C:\Users\ADMIN\Genesis_System3\Genesis_System3")
OUT_DIR = PRIMARY / "reports" / "latest" / "access_capability"
LIVE_BASE = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
REPO = "psw2025-cmd/Genesis_System3"
GCP_PROJECT = "system3-openalgo-safe"

GMAIL_CRED = Path(
    r"C:\Pritam_CV_Tier1_EPC\Piping-E3D-Job-Intelligence\private-config\gmail_credentials.json"
)
GMAIL_TOKEN = Path(
    r"C:\Pritam_CV_Tier1_EPC\Piping-E3D-Job-Intelligence\private-config\gmail_token.json"
)
GMAIL_PY = Path(r"C:\Pritam_CV_Tier1_EPC\.venv-pr53\Scripts\python.exe")

BANNED_PATHS = [
    Path(r"C:\System3\Genesis_System3"),
    Path(r"C:\Users\ADMIN\Genesis_System3"),  # parent only
]
OVERLAY = Path(r"C:\Genesis_System3")


def _run(cmd: list[str], timeout: int = 45) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout_head": out[:800],
            "stderr_head": err[:400],
        }
    except FileNotFoundError:
        return {"ok": False, "code": 127, "stdout_head": "", "stderr_head": "not_found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": 124, "stdout_head": "", "stderr_head": "timeout"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "code": 1, "stdout_head": "", "stderr_head": type(exc).__name__}


def _http(url: str, timeout: int = 30) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "system3-access-probe/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return {"ok": True, "status": resp.status, "body_head": body[:500]}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "body_head": str(exc)[:300]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": None, "body_head": f"{type(exc).__name__}: {exc}"[:300]}


def _which(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    # Windows Cloud SDK often only on interactive PATH
    if name in {"gcloud", "gsutil", "bq"}:
        candidates = [
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / f"{name}.cmd",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / f"{name}.cmd",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / f"{name}.cmd",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return None


def _gcloud_cmd() -> list[str]:
    g = _which("gcloud")
    return [g] if g else ["gcloud"]


def check_tools() -> dict[str, Any]:
    names = ["git", "gh", "gcloud", "curl", "python", "py", "claude", "cursor", "node", "npm"]
    return {n: {"path": _which(n), "present": bool(_which(n))} for n in names}


def check_paths() -> dict[str, Any]:
    items = {
        "primary_clone": PRIMARY,
        "primary_git_head": PRIMARY / ".git" / "HEAD",
        "overlay_not_clone": OVERLAY,
        "banned_old_system3": BANNED_PATHS[0],
        "banned_parent_admin": BANNED_PATHS[1],
        "gmail_credentials": GMAIL_CRED,
        "gmail_token": GMAIL_TOKEN,
        "gmail_python": GMAIL_PY,
    }
    out = {}
    for k, p in items.items():
        out[k] = {
            "path": str(p),
            "exists": p.exists(),
            "is_file": p.is_file() if p.exists() else False,
            "is_dir": p.is_dir() if p.exists() else False,
        }
    # primary git usable?
    git_ok = _run(["git", "-C", str(PRIMARY), "rev-parse", "--is-inside-work-tree"])
    out["primary_git_usable"] = git_ok
    old_ok = _run(["git", "-C", str(BANNED_PATHS[0]), "rev-parse", "--is-inside-work-tree"])
    out["old_system3_git_usable"] = old_ok
    return out


def check_disk() -> dict[str, Any]:
    drives = {}
    for letter in "CDEF":
        root = Path(f"{letter}:/")
        if not root.exists():
            continue
        try:
            usage = shutil.disk_usage(root)
            drives[letter] = {
                "free_gb": round(usage.free / (1024**3), 2),
                "total_gb": round(usage.total / (1024**3), 2),
                "ok_for_worktrees": usage.free > 10 * 1024**3,
            }
        except OSError as exc:
            drives[letter] = {"error": type(exc).__name__}
    return drives


def check_github() -> dict[str, Any]:
    status = _run(["gh", "auth", "status"])
    api = _run(["gh", "api", "user", "--jq", ".login"])
    repo = _run(["gh", "api", f"repos/{REPO}", "--jq", ".full_name"])
    main = _run(["gh", "api", f"repos/{REPO}/commits/main", "--jq", ".sha"])
    return {
        "auth_status": status,
        "user": api,
        "repo_visible": repo,
        "main_sha": main,
        "ok": bool(api.get("ok") and repo.get("ok")),
    }


def check_gcloud() -> dict[str, Any]:
    gcmd = _gcloud_cmd()
    acct = _run([*gcmd, "auth", "list", "--format=value(account,status)"])
    project = _run([*gcmd, "config", "get-value", "project"])
    adc = _run([*gcmd, "auth", "application-default", "print-access-token"])
    # redact token
    if adc.get("ok") and adc.get("stdout_head"):
        adc = {**adc, "stdout_head": "[REDACTED_TOKEN_PRESENT]", "token_present": True}
    else:
        adc = {**adc, "token_present": False}
    run = _run(
        [
            *gcmd,
            "run",
            "services",
            "describe",
            "genesis-system3-web",
            f"--project={GCP_PROJECT}",
            "--region=asia-south1",
            "--format=value(status.url)",
        ],
        timeout=60,
    )
    return {
        "gcloud_resolved": gcmd,
        "auth_list": acct,
        "project": project,
        "adc": adc,
        "run_describe": run,
        "ok": bool(run.get("ok") or (acct.get("ok") and "ACTIVE" in (acct.get("stdout_head") or ""))),
    }


def check_gmail() -> dict[str, Any]:
    base = {
        "credentials_present": GMAIL_CRED.exists(),
        "token_present": GMAIL_TOKEN.exists(),
        "python_present": GMAIL_PY.exists(),
        "ok": False,
        "detail": "",
    }
    if not (base["credentials_present"] and base["token_present"] and base["python_present"]):
        base["detail"] = "missing_credential_files_or_python"
        return base
    # live API ping (readonly)
    code = r"""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
tok=Path(r'%s')
creds=Credentials.from_authorized_user_file(str(tok), [
 'https://www.googleapis.com/auth/gmail.readonly',
 'https://www.googleapis.com/auth/gmail.send',
 'https://www.googleapis.com/auth/gmail.compose'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
svc=build('gmail','v1',credentials=creds,cache_discovery=False)
prof=svc.users().getProfile(userId='me').execute()
print(json.dumps({'emailAddress':prof.get('emailAddress'),'messagesTotal':prof.get('messagesTotal')}))
""" % str(GMAIL_TOKEN).replace("\\", "\\\\")
    r = _run([str(GMAIL_PY), "-c", code], timeout=90)
    base["api"] = r
    base["ok"] = bool(r.get("ok"))
    base["detail"] = "gmail_profile_ok" if r.get("ok") else (r.get("stderr_head") or r.get("stdout_head") or "fail")
    return base


def check_live_cloud() -> dict[str, Any]:
    endpoints = {
        "deploy_info": f"{LIVE_BASE}/api/deploy_info",
        "broker_status": f"{LIVE_BASE}/api/broker/status",
        "system_health": f"{LIVE_BASE}/api/system_health",
        "ui": f"{LIVE_BASE}/ui/",
    }
    out = {}
    for k, url in endpoints.items():
        out[k] = {"url": url, **_http(url)}
    return out


def check_network() -> dict[str, Any]:
    hosts = ["github.com", "api.github.com", "gmail.googleapis.com", "run.app", "oauth2.googleapis.com"]
    out = {}
    for h in hosts:
        try:
            socket.getaddrinfo(h, 443)
            out[h] = {"dns_ok": True}
        except OSError as exc:
            out[h] = {"dns_ok": False, "error": type(exc).__name__}
    return out


def check_claude_cli() -> dict[str, Any]:
    path = _which("claude")
    version = _run(["claude", "--version"]) if path else {"ok": False, "stderr_head": "not_on_path"}
    # common config locations (existence only)
    homes = [
        Path.home() / ".claude",
        Path.home() / ".config" / "claude",
        Path(r"C:\Users\ADMIN\.claude"),
    ]
    return {
        "on_path": bool(path),
        "path": path,
        "version": version,
        "config_dirs": {str(p): p.exists() for p in homes},
    }


def classify(report: dict[str, Any]) -> dict[str, list[str]]:
    have: list[str] = []
    missing: list[str] = []

    def add(ok: bool, name: str) -> None:
        (have if ok else missing).append(name)

    tools = report["tools"]
    add(tools.get("git", {}).get("present"), "tool:git")
    add(tools.get("gh", {}).get("present"), "tool:gh")
    add(tools.get("gcloud", {}).get("present"), "tool:gcloud")
    add(tools.get("claude", {}).get("present"), "tool:claude_cli")
    add(report["github"]["ok"], "github_api_auth")
    add(report["gcloud"].get("run_describe", {}).get("ok") or report["gcloud"].get("adc", {}).get("token_present"), "gcloud_cloud_run_or_adc")
    add(report["gmail"]["ok"], "gmail_api")
    add(report["paths"]["primary_git_usable"].get("ok"), "primary_clone_git")
    add(not report["paths"]["old_system3_git_usable"].get("ok"), "old_path_correctly_unusable")
    live = report["live_cloud"]
    add(live.get("deploy_info", {}).get("ok"), "live_deploy_info")
    add(live.get("broker_status", {}).get("ok"), "live_broker_status")
    add(live.get("ui", {}).get("ok"), "live_ui")
    return {"HAVE": have, "MISSING_OR_FAIL": missing}


def grant_commands(missing: list[str]) -> list[str]:
    cmds: list[str] = []
    if "tool:gh" in missing or "github_api_auth" in missing:
        cmds.append("gh auth login -h github.com -p https -w")
        cmds.append("gh auth refresh -h github.com -s repo,workflow,read:org,gist")
    if "tool:gcloud" in missing or "gcloud_cloud_run_or_adc" in missing:
        cmds.append("gcloud auth login")
        cmds.append("gcloud auth application-default login")
        cmds.append(f"gcloud config set project {GCP_PROJECT}")
    if "gmail_api" in missing:
        cmds.append(
            "# Re-auth Gmail (readonly+send+compose) using existing private-config paths; "
            "run from Pritam_CV_Tier1_EPC venv after fixing invalid_grant"
        )
        cmds.append(
            f"{GMAIL_PY} -c \"print('Use Gmail OAuth reauth flow for', r'{GMAIL_TOKEN}')\""
        )
    if "tool:claude_cli" in missing:
        cmds.append("npm install -g @anthropic-ai/claude-code")
        cmds.append("claude  # then complete login /api key setup interactively")
    if "primary_clone_git" in missing:
        cmds.append(
            f"git clone https://github.com/{REPO}.git \"{PRIMARY}\""
        )
    if "live_deploy_info" in missing or "live_ui" in missing:
        cmds.append("# Network/DNS to Cloud Run failed — check VPN/firewall/DNS")
    cmds.append(
        f'# After grants, re-run: {sys.executable} "{PRIMARY / "scripts" / "system3_access_capability_probe.py"}"'
    )
    return cmds


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# System3 Access Capability Probe",
        "",
        f"Generated: {report['generated_ist']}",
        f"Host: {report['host']}",
        f"Primary: `{PRIMARY}`",
        "",
        "## Summary",
        "",
        "### HAVE",
    ]
    for x in report["classification"]["HAVE"]:
        lines.append(f"- {x}")
    lines.append("")
    lines.append("### MISSING_OR_FAIL")
    miss = report["classification"]["MISSING_OR_FAIL"]
    if not miss:
        lines.append("- (none)")
    else:
        for x in miss:
            lines.append(f"- {x}")
    lines.append("")
    lines.append("## Grant commands (run locally)")
    lines.append("")
    lines.append("```powershell")
    for c in report["grant_commands"]:
        lines.append(c)
    lines.append("```")
    lines.append("")
    lines.append("## Details (redacted JSON also saved)")
    lines.append("")
    lines.append(
        f"- JSON: `{OUT_DIR / 'ACCESS_PROBE_RESULT.json'}`\n"
        f"- Grant revise: `{OUT_DIR / 'ACCESS_GRANT_REVISE.ps1'}`\n"
        f"- Claude CLI helper: `{PRIMARY / 'scripts' / 'claude_cli_access_bootstrap.md'}`"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema": "system3_access_capability_probe_v1",
        "generated_ist": dt.datetime.now().astimezone().isoformat(),
        "host": socket.gethostname(),
        "python": sys.executable,
        "tools": check_tools(),
        "paths": check_paths(),
        "disk": check_disk(),
        "network_dns": check_network(),
        "github": check_github(),
        "gcloud": check_gcloud(),
        "gmail": check_gmail(),
        "live_cloud": check_live_cloud(),
        "claude_cli": check_claude_cli(),
    }
    report["classification"] = classify(report)
    report["grant_commands"] = grant_commands(report["classification"]["MISSING_OR_FAIL"])

    json_path = OUT_DIR / "ACCESS_PROBE_RESULT.json"
    md_path = OUT_DIR / "ACCESS_PROBE_RESULT.md"
    grant_path = OUT_DIR / "ACCESS_GRANT_REVISE.ps1"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")

    ps = [
        "# Auto-generated from ACCESS_PROBE_RESULT — run in elevated PowerShell if needed",
        "$ErrorActionPreference = 'Continue'",
        f"Write-Host 'Granting missing System3 access based on probe at {report['generated_ist']}'",
    ]
    for c in report["grant_commands"]:
        if c.startswith("#"):
            ps.append(c)
        else:
            ps.append(c)
    ps.append(f'& "{sys.executable}" "{PRIMARY / "scripts" / "system3_access_capability_probe.py"}"')
    grant_path.write_text("\n".join(ps) + "\n", encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {grant_path}")
    print("HAVE:", ", ".join(report["classification"]["HAVE"]) or "(none)")
    print("MISSING:", ", ".join(report["classification"]["MISSING_OR_FAIL"]) or "(none)")
    return 0 if not report["classification"]["MISSING_OR_FAIL"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
