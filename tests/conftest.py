import os
import sys

# Ensure repository root and audit directory are in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIT_DIR = os.path.join(REPO_ROOT, "audit")

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if AUDIT_DIR not in sys.path:
    sys.path.insert(0, AUDIT_DIR)
