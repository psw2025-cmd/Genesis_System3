import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dashboard.backend.app import _synthesize_operational_alerts, get_recent_alerts


async def test():
    alerts = await _synthesize_operational_alerts()
    print("Synthesized alerts count:", len(alerts))
    for a in alerts:
        print(f"  [{a['severity']}] {a['id']}: {a['title']}")

    recent = await get_recent_alerts()
    print("Recent alerts count:", recent.get("count"))
    print("All good!")


if __name__ == "__main__":
    asyncio.run(test())
