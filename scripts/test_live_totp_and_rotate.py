from __future__ import annotations

from scripts.gcp_dhan_token_rotation_job import main as run_canonical_rotation_job


def run_totp_test() -> bool:
    """Delegate Dhan TOTP rotation to the single canonical authority."""
    rc = run_canonical_rotation_job()
    return rc == 0


if __name__ == "__main__":
    raise SystemExit(0 if run_totp_test() else 1)
