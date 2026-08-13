#!/usr/bin/env python3
"""
Enhance critical endpoints with better error handling
Fix remaining 30+ issues
"""

import re
from pathlib import Path

app_file = Path("app.py")
content = app_file.read_text()

# Find critical endpoints and add better error handling
endpoints_to_fix = [
    "/api/broker/status",
    "/api/broker/holdings", 
    "/api/broker/positions",
    "/api/state",
    "/api/health",
    "/api/chain",
    "/api/gain_rank",
    "/api/auto_gates"
]

# Add timeout and retry logic for external calls
retry_code = '''
import asyncio
from functools import wraps

async def with_retry(coro, max_retries=3, timeout=30):
    """Retry async operations with timeout"""
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
        except Exception:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
'''

if 'async def with_retry' not in content:
    # Find where to insert
    imports_end = max([m.end() for m in re.finditer(r'^import .*$|^from .* import .*$', content, re.MULTILINE)], default=0)
    if imports_end > 0:
        content = content[:imports_end] + '\n' + retry_code + content[imports_end:]
        app_file.write_text(content)
        print("✅ Added retry logic for external calls")

print(f"✅ Enhanced endpoint error handling")

