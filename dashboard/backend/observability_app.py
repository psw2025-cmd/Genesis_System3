"""Cloud Run ASGI entrypoint with secret-safe request/trace correlation.

Security authority remains in ``dashboard.backend.secure_app``. This module only
wraps the already-validated FastAPI app with metadata-only observability.
"""

from dashboard.backend.secure_app import app as secure_app
from dashboard.backend.structured_logging import RequestIDMiddleware

app = RequestIDMiddleware(secure_app)
