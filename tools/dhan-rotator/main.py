"""Compatibility wrapper delegating to canonical rotation job."""
from __future__ import annotations

import sys
from scripts.gcp_dhan_token_rotation_job import main as canonical_main


def rotate(request=None):
    rc = canonical_main()
    success = rc == 0
    if request is not None:
        return ("SUCCESS", 200) if success else ("FAILED", 500)
    return success


if __name__ == "__main__":
    sys.exit(canonical_main())

