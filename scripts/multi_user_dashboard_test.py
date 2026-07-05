"""
Multi-User Dashboard Testing Framework
Simulates multiple traders/users accessing dashboard simultaneously
Tests for race conditions, data consistency, and performance
"""

import asyncio
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import aiohttp
import pytz

ROOT_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"


@dataclass
class UserSession:
    """Represents a user session"""

    user_id: str
    start_time: str
    requests_made: int
    errors: List[str]
    response_times: List[float]
    data_consistency_errors: List[str]


class MultiUserDashboardTester:
    """Tests dashboard with multiple concurrent users"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.sessions: List[UserSession] = []
        self.test_results: Dict[str, Any] = {}

    async def user_session(self, user_id: str, duration_seconds: int = 60):
        """Simulate a single user session"""
        session = UserSession(
            user_id=user_id,
            start_time=datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            requests_made=0,
            errors=[],
            response_times=[],
            data_consistency_errors=[],
        )

        async with aiohttp.ClientSession() as http_session:
            start_time = time.time()
            last_health_data = None

            while time.time() - start_time < duration_seconds:
                try:
                    # Randomly select an endpoint to test
                    endpoints = [
                        ("/api/health", "health"),
                        ("/api/qc", "qc"),
                        ("/api/signal/top", "signal"),
                        ("/api/positions", "positions"),
                        ("/api/pnl", "pnl"),
                        ("/api/perf", "perf"),
                        ("/api/chain/NIFTY", "chain_nifty"),
                        ("/api/chain/BANKNIFTY", "chain_banknifty"),
                    ]

                    endpoint, name = random.choice(endpoints)

                    request_start = time.time()
                    async with http_session.get(
                        f"{self.base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        request_time = time.time() - request_start
                        session.response_times.append(request_time)
                        session.requests_made += 1

                        if response.status == 200:
                            data = await response.json()

                            # Check data consistency for health endpoint
                            if name == "health":
                                if last_health_data:
                                    # Check if critical fields changed unexpectedly
                                    if "cycle_count" in data and "cycle_count" in last_health_data:
                                        if data["cycle_count"] < last_health_data["cycle_count"]:
                                            session.data_consistency_errors.append(
                                                f"Cycle count decreased: {last_health_data['cycle_count']} -> {data['cycle_count']}"
                                            )

                                last_health_data = data.copy()
                        else:
                            session.errors.append(f"{endpoint}: Status {response.status}")

                    # Random delay between requests (0.5-2 seconds)
                    await asyncio.sleep(random.uniform(0.5, 2.0))

                except asyncio.TimeoutError:
                    session.errors.append(f"{endpoint}: Timeout")
                except Exception as e:
                    session.errors.append(f"{endpoint}: {str(e)}")

        self.sessions.append(session)
        return session

    async def run_concurrent_users(self, num_users: int = 5, duration_seconds: int = 60):
        """Run multiple concurrent user sessions"""
        print(f"Starting {num_users} concurrent user sessions for {duration_seconds} seconds...")
        print("=" * 60)

        tasks = []
        for i in range(num_users):
            user_id = f"user_{i+1}"
            task = self.user_session(user_id, duration_seconds)
            tasks.append(task)

        # Run all sessions concurrently
        await asyncio.gather(*tasks)

        # Analyze results
        self._analyze_results()

    def _analyze_results(self):
        """Analyze test results"""
        total_requests = sum(s.requests_made for s in self.sessions)
        total_errors = sum(len(s.errors) for s in self.sessions)
        total_consistency_errors = sum(len(s.data_consistency_errors) for s in self.sessions)

        avg_response_time = 0
        all_response_times = []
        for s in self.sessions:
            all_response_times.extend(s.response_times)

        if all_response_times:
            avg_response_time = sum(all_response_times) / len(all_response_times)
            min_response_time = min(all_response_times)
            max_response_time = max(all_response_times)
        else:
            min_response_time = 0
            max_response_time = 0

        self.test_results = {
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "num_users": len(self.sessions),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "total_consistency_errors": total_consistency_errors,
            "avg_response_time_ms": avg_response_time * 1000,
            "min_response_time_ms": min_response_time * 1000,
            "max_response_time_ms": max_response_time * 1000,
            "sessions": [asdict(s) for s in self.sessions],
        }

        print("\n" + "=" * 60)
        print("MULTI-USER TEST RESULTS")
        print("=" * 60)
        print(f"Users: {len(self.sessions)}")
        print(f"Total Requests: {total_requests}")
        print(f"Total Errors: {total_errors}")
        print(f"Error Rate: {self.test_results['error_rate']:.2f}%")
        print(f"Consistency Errors: {total_consistency_errors}")
        print(f"Avg Response Time: {avg_response_time*1000:.2f}ms")
        print(f"Min Response Time: {min_response_time*1000:.2f}ms")
        print(f"Max Response Time: {max_response_time*1000:.2f}ms")

        if total_errors > 0:
            print("\nErrors by endpoint:")
            error_counts = {}
            for s in self.sessions:
                for error in s.errors:
                    endpoint = error.split(":")[0]
                    error_counts[endpoint] = error_counts.get(endpoint, 0) + 1

            for endpoint, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {endpoint}: {count}")

        if total_consistency_errors > 0:
            print("\nData Consistency Errors:")
            for s in self.sessions:
                for error in s.data_consistency_errors:
                    print(f"  {s.user_id}: {error}")

    def save_results(self, filename: str = None):
        """Save test results"""
        if filename is None:
            filename = f"multi_user_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results_path = OUTPUTS_DIR / "validation" / filename
        results_path.parent.mkdir(parents=True, exist_ok=True)

        with open(results_path, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        print(f"\nResults saved: {results_path}")
        return results_path


async def main():
    """Main test function"""
    tester = MultiUserDashboardTester()

    # Test with 5 concurrent users for 60 seconds
    await tester.run_concurrent_users(num_users=5, duration_seconds=60)

    # Save results
    tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())
