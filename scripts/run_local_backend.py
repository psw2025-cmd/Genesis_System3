import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import uvicorn

if __name__ == "__main__":
    from dashboard.backend.app import app
    uvicorn.run(app, host="127.0.0.1", port=8000, loop="asyncio", log_level="info")



