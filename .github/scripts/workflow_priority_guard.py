#!/usr/bin/env python3
"""Fail closed unless only the approved System3 priority workflows are active."""
from __future__ import annotations

import re
from pathlib import Path

WORKFLOW_DIR = Path(".github/workflows")
POLICY_PATH = Path("docs/SYSTEM3_WORKFLOW_PRIORITY_POLICY.md")

AUTOMATIC = {
    "ci.yml",
    "workflow-priority-guard.yml",
    "cloud-run-auto-deploy.yml",
    "gcp-authority-repair.yml",
    "gcp-live-ui-semantic-proof.yml",
    "gcp-stage2-ci.yml",
    "gcp-dhan-token-fix-ci.yml",
    "frontend-runtime-smoke.yml",
    "codeql-security.yml",
    "security-audit.yml",
    "sonarqube-audit.yml",
    "full-cloud-audit.yml",
    "system3-preflight-control-plane.yml",
    "repo-clean-forensic-toolkit.yml",
}
MANUAL_ONLY = {"gcp-dhan-token-rotation.yml"}
ALLOWED = AUTOMATIC | MANUAL_ONLY

FORENSIC_WORKFLOW = "workflow-priority-guard.yml"
IAM_REPAIR_WORKFLOW = "gcp-authority-repair.yml"
LIVE_UI_PROOF_WORKFLOW = "gcp-live-ui-semantic-proof.yml"
EVENT_TRIGGER_WORKFLOWS = {FORENSIC_WORKFLOW, IAM_REPAIR_WORKFLOW, LIVE_UI_PROOF_WORKFLOW}
FORENSIC_MONITORED_WORKFLOWS = {
    "Genesis System3 Global Safety CI",
    "Cloud Run Auto Deploy",
    "Frontend Browser Runtime Smoke",
    "GCP Dhan Token Fix CI",
    "GCP Dhan Token Rotation Manual Recovery",
    "GCP Stage 2 Safety Checks",
    "CodeQL Security Audit",
    "Security Audit Evidence",
    "SonarQube Audit",
    "Full Cloud Audit and Forensic Consensus",
}


def _top_level_on_block(text: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^on\s*:\s*$", line):
            start = index + 1
            continue
        if start is not None and line.strip() and not line.lstrip().startswith("#"):
            current_indent = len(line) - len(line.lstrip())
            if current_indent == 0:
                return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""


def main() -> int:
    files = sorted(
        p.name
        for pattern in ("*.yml", "*.yaml")
        for p in WORKFLOW_DIR.glob(pattern)
        if p.is_file()
    )
    actual = set(files)
    unexpected = sorted(actual - ALLOWED)
    missing = sorted(ALLOWED - actual)
    if unexpected or missing:
        raise SystemExit(
            f"WORKFLOW_ALLOWLIST_FAIL unexpected={unexpected} missing={missing} actual={files}"
        )

    if not POLICY_PATH.is_file():
        raise SystemExit(f"WORKFLOW_POLICY_MISSING {POLICY_PATH}")

    forbidden_trigger = re.compile(
        r"^\s*(schedule|repository_dispatch|issue_comment|issues)\s*:",
        re.IGNORECASE | re.MULTILINE,
    )
    self_hosted = re.compile(
        r"runs-on:\s*(?:\[[^\]]*)?self-hosted",
        re.IGNORECASE,
    )
    retired_runtime = re.compile(r"render\.com|api\.render\.com", re.IGNORECASE)
    live_enable = re.compile(
        r"LIVE_TRADING_ENABLED\s*[:=]\s*[\"']?(?:1|true|yes)|"
        r"SYSTEM3_LIVE_TRADING_ALLOWED\s*[:=]\s*[\"']?(?:1|true|yes)|"
        r"AUTO_EXECUTE_TRADES\s*[:=]\s*[\"']?(?:1|true|yes)",
        re.IGNORECASE,
    )
    event_trigger = re.compile(
        r"^\s*(workflow_run|deployment_status)\s*:",
        re.IGNORECASE | re.MULTILINE,
    )

    trigger_blocks: dict[str, str] = {}
    workflow_text: dict[str, str] = {}
    for name in files:
        text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
        workflow_text[name] = text
        on_block = _top_level_on_block(text)
        trigger_blocks[name] = on_block
        if not on_block:
            raise SystemExit(f"WORKFLOW_TRIGGER_BLOCK_MISSING file={name}")
        match = forbidden_trigger.search(on_block)
        if match:
            raise SystemExit(f"WORKFLOW_FORBIDDEN_TRIGGER file={name} match={match.group(1)!r}")
        event_match = event_trigger.search(on_block)
        if event_match and name not in EVENT_TRIGGER_WORKFLOWS:
            raise SystemExit(
                f"WORKFLOW_EVENT_TRIGGER_RESERVED file={name} match={event_match.group(1)!r}"
            )
        if self_hosted.search(text):
            raise SystemExit(f"WORKFLOW_SELF_HOSTED_FORBIDDEN file={name}")
        if retired_runtime.search(text):
            raise SystemExit(f"WORKFLOW_RETIRED_RUNTIME_REFERENCE file={name}")
        if live_enable.search(text):
            raise SystemExit(f"WORKFLOW_LIVE_TRADING_FORBIDDEN file={name}")

    manual_on = trigger_blocks["gcp-dhan-token-rotation.yml"]
    if "workflow_dispatch:" not in manual_on:
        raise SystemExit("MANUAL_ROTATION_WORKFLOW_DISPATCH_MISSING")
    if re.search(r"^\s*(push|pull_request)\s*:", manual_on, re.MULTILINE):
        raise SystemExit(f"MANUAL_ROTATION_HAS_AUTOMATIC_TRIGGER block={manual_on!r}")

    ci_on = trigger_blocks["ci.yml"]
    if "pull_request:" not in ci_on or "push:" not in ci_on:
        raise SystemExit("GLOBAL_SAFETY_PRIORITY_TRIGGERS_MISSING")

    guard_on = trigger_blocks[FORENSIC_WORKFLOW]
    for required in ("pull_request:", "push:", "workflow_dispatch:", "workflow_run:", "deployment_status:"):
        if required not in guard_on:
            raise SystemExit(f"WORKFLOW_PRIORITY_GUARD_TRIGGER_MISSING trigger={required}")
    for monitored in sorted(FORENSIC_MONITORED_WORKFLOWS):
        if monitored not in guard_on:
            raise SystemExit(f"FORENSIC_MONITORED_WORKFLOW_MISSING workflow={monitored!r}")

    guard_text = workflow_text[FORENSIC_WORKFLOW]
    if re.search(
        r"^\s*(contents|actions|deployments|issues|pull-requests|checks|statuses):\s*write\s*$",
        guard_text,
        re.IGNORECASE | re.MULTILINE,
    ):
        raise SystemExit("FORENSIC_RESPONDER_WRITE_PERMISSION_FORBIDDEN")
    if "deployments: read" not in guard_text:
        raise SystemExit("FORENSIC_RESPONDER_DEPLOYMENTS_READ_MISSING")
    if "persist-credentials: false" not in guard_text:
        raise SystemExit("FORENSIC_RESPONDER_CHECKOUT_CREDENTIAL_PERSISTENCE_NOT_DISABLED")
    if re.search(
        r"ref:\s*\$\{\{\s*github\.event\.workflow_run\.(head_sha|head_branch)\s*\}\}",
        guard_text,
        re.IGNORECASE,
    ):
        raise SystemExit("FORENSIC_RESPONDER_UNTRUSTED_REF_CHECKOUT_FORBIDDEN")
    if not re.search(r"ref:\s*main\s*$", guard_text, re.MULTILINE):
        raise SystemExit("FORENSIC_RESPONDER_DEFAULT_BRANCH_CHECKOUT_MISSING")

    repair_on = trigger_blocks[IAM_REPAIR_WORKFLOW]
    repair_text = workflow_text[IAM_REPAIR_WORKFLOW]
    if "workflow_run:" not in repair_on or "workflow_dispatch:" not in repair_on:
        raise SystemExit("IAM_REPAIR_REQUIRED_TRIGGERS_MISSING")
    if "deployment_status:" in repair_on:
        raise SystemExit("IAM_REPAIR_DEPLOYMENT_STATUS_TRIGGER_FORBIDDEN")
    if re.search(r"^\s*(push|pull_request)\s*:", repair_on, re.MULTILINE):
        raise SystemExit("IAM_REPAIR_DIRECT_CODE_EVENT_TRIGGER_FORBIDDEN")
    if 'workflows: ["Cloud Run Auto Deploy"]' not in repair_on:
        raise SystemExit("IAM_REPAIR_WORKFLOW_RUN_SOURCE_NOT_EXACT")
    if "head_branch == 'main'" not in repair_text:
        raise SystemExit("IAM_REPAIR_MAIN_BRANCH_GUARD_MISSING")
    if "actions: write" in repair_text or "contents: write" in repair_text:
        raise SystemExit("IAM_REPAIR_GITHUB_WRITE_PERMISSION_FORBIDDEN")
    if "gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com" not in repair_text:
        raise SystemExit("IAM_REPAIR_PRIMARY_IDENTITY_MISSING")
    if "gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com" not in repair_text:
        raise SystemExit("IAM_REPAIR_FALLBACK_IDENTITY_MISSING")
    if repair_text.count("uses: ./.github/workflows/cloud-run-auto-deploy.yml") != 1:
        raise SystemExit("IAM_REPAIR_BOUNDED_DEPLOY_REUSE_INVALID")
    if "gcloud run jobs execute" in repair_text:
        raise SystemExit("IAM_REPAIR_DHAN_OR_JOB_EXECUTION_FORBIDDEN")

    semantic_on = trigger_blocks[LIVE_UI_PROOF_WORKFLOW]
    semantic_text = workflow_text[LIVE_UI_PROOF_WORKFLOW]
    if "workflow_run:" not in semantic_on or "workflow_dispatch:" not in semantic_on:
        raise SystemExit("LIVE_UI_PROOF_REQUIRED_TRIGGERS_MISSING")
    if 'workflows: ["Cloud Run Auto Deploy"]' not in semantic_on:
        raise SystemExit("LIVE_UI_PROOF_WORKFLOW_RUN_SOURCE_NOT_EXACT")
    if "head_branch == 'main'" not in semantic_text:
        raise SystemExit("LIVE_UI_PROOF_MAIN_BRANCH_GUARD_MISSING")
    if re.search(r"^\s*(push|pull_request|deployment_status)\s*:", semantic_on, re.MULTILINE):
        raise SystemExit("LIVE_UI_PROOF_DIRECT_CODE_OR_DEPLOYMENT_TRIGGER_FORBIDDEN")
    if "contents: read" not in semantic_text or "statuses: write" not in semantic_text:
        raise SystemExit("LIVE_UI_PROOF_MINIMAL_GITHUB_PERMISSIONS_MISSING")
    for forbidden_permission in ("actions: write", "contents: write", "deployments: write", "issues: write", "pull-requests: write"):
        if forbidden_permission in semantic_text:
            raise SystemExit(f"LIVE_UI_PROOF_WRITE_PERMISSION_FORBIDDEN permission={forbidden_permission}")
    if "persist-credentials: false" not in semantic_text:
        raise SystemExit("LIVE_UI_PROOF_CHECKOUT_CREDENTIAL_PERSISTENCE_NOT_DISABLED")
    if "gcloud " in semantic_text or "gcloud\t" in semantic_text:
        raise SystemExit("LIVE_UI_PROOF_GCP_MUTATION_SURFACE_FORBIDDEN")
    if "python scripts/gcp_live_ui_semantic_proof.py" not in semantic_text:
        raise SystemExit("LIVE_UI_PROOF_CANONICAL_SCRIPT_MISSING")

    deploy_on = trigger_blocks["cloud-run-auto-deploy.yml"]
    if "push:" not in deploy_on or not re.search(r"branches:\s*\[\s*main\s*\]", deploy_on):
        raise SystemExit("CLOUD_RUN_MAIN_TRIGGER_MISSING")
    if "workflow_call:" not in deploy_on:
        raise SystemExit("CLOUD_RUN_REUSABLE_TRIGGER_MISSING")

    full_audit_on = trigger_blocks["full-cloud-audit.yml"]
    if "push:" not in full_audit_on or not re.search(r"branches:\s*\[\s*main\s*\]", full_audit_on):
        raise SystemExit("FULL_CLOUD_AUDIT_MAIN_TRIGGER_MISSING")
    if "workflow_dispatch:" not in full_audit_on:
        raise SystemExit("FULL_CLOUD_AUDIT_MANUAL_TRIGGER_MISSING")

    preflight_on = trigger_blocks["system3-preflight-control-plane.yml"]
    if "push:" not in preflight_on or not re.search(r"branches:\s*\[\s*main\s*\]", preflight_on):
        raise SystemExit("PREFLIGHT_CONTROL_PLANE_MAIN_TRIGGER_MISSING")
    if "workflow_dispatch:" not in preflight_on:
        raise SystemExit("PREFLIGHT_CONTROL_PLANE_MANUAL_TRIGGER_MISSING")

    for name in (
        "gcp-stage2-ci.yml",
        "gcp-dhan-token-fix-ci.yml",
        "frontend-runtime-smoke.yml",
        "codeql-security.yml",
        "security-audit.yml",
        "sonarqube-audit.yml",
        "repo-clean-forensic-toolkit.yml",
    ):
        if "pull_request:" not in trigger_blocks[name]:
            raise SystemExit(f"FOCUSED_PRIORITY_PR_TRIGGER_MISSING file={name}")

    print(
        "WORKFLOW_PRIORITY_POLICY=PASS",
        {
            "active_workflow_count": len(files),
            "automatic": sorted(AUTOMATIC),
            "manual_only": sorted(MANUAL_ONLY),
            "unexpected": [],
            "self_hosted": False,
            "retired_runtime_workflows": False,
            "scheduled_github_workflows": False,
            "event_forensic_responder": FORENSIC_WORKFLOW,
            "event_iam_repair": IAM_REPAIR_WORKFLOW,
            "event_live_ui_semantic_proof": LIVE_UI_PROOF_WORKFLOW,
            "event_monitored_workflow_count": len(FORENSIC_MONITORED_WORKFLOWS),
            "event_responder_write_permissions": False,
            "iam_repair_github_write_permissions": False,
            "live_ui_proof_runtime_mutation_permissions": False,
            "live_trading": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
