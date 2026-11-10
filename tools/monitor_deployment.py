"""Monitor Cloud Run Deployment Workflow."""

import json
import subprocess
import time

RUN_ID = "33250991033"
print(f"Monitoring Cloud Run Deployment Run {RUN_ID}...")

for i in range(40):
    p = subprocess.run(
        ["gh", "run", "view", RUN_ID, "--json", "status,conclusion,jobs"],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\ADMIN\Genesis_System3\Genesis_System3",
    )
    try:
        data = json.loads(p.stdout)
        status = data.get("status")
        conclusion = data.get("conclusion")
        jobs = data.get("jobs", [])
        job_states = [
            f"{j.get('name')}: {j.get('status')}/{j.get('conclusion')}"
            for j in jobs
        ]
        print(
            f"Poll {i+1} (elapsed {(i+1)*15}s): Status={status}, Conclusion={conclusion} | Jobs={job_states}"
        )
        if status == "completed":
            print(f"Deployment workflow finished with conclusion: {conclusion}")
            break
    except Exception as e:
        print(f"Poll {i+1}: error {e}")
    time.sleep(15)
