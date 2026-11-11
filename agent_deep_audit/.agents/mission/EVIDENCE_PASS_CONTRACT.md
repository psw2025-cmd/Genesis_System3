# Independent evidence standard
This is a verification contract, not a generated certificate.

For each check ID, retain: current UTC time; actual workspace, Git SHA and deployed revision (when relevant); executed command/test path and exit code; expected versus observed behavior; raw source packets or sanitized logs with timestamps; exact artifact URI, hash and reproduction instructions; reviewer and decision distinct from generator.

PASS requires all relevant items and a repeated independent check. FAIL denotes actual failed assertions; BLOCKED denotes tools/auth/market closed/entitlement/access limits; UNVERIFIED denotes missing independent proof.
Do not transform self-authored narrative into evidence, do not treat a SHA256 checksum as proof that prices or fills are real, and do not count a GET endpoint as proof of a real broker session. Preserve safety and privacy.

The prior scripts/run_1872_acceptance_pipeline.py produces textual PASS claims and owner signoff. Its existing CSV and JSON output must be preserved as historical claims; do not run it as an acceptance certificate unless it is repaired and independently tested. Use .agents/state/INDEPENDENT_VERIFICATION.csv for genuine check-by-check certification.
