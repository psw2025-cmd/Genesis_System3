# High Error Rate / Latency Runbook

## Trigger targets

These are target SLO/alert thresholds, not claims of current performance:

- critical endpoint error rate >1% for 5 minutes;
- 5xx >5% for 1 minute;
- three consecutive critical synthetic failures;
- p95 API latency target >300 ms breach;
- browser error rate materially above established baseline.

## Safety invariants

- Do not change trading mode, enable LIVE, or bypass MutationPolicy.
- Do not encode Cloud Run scaling as an application environment variable.
- Do not roll forward to an unproven candidate.
- Do not perform more than one traffic rollback inside 30 minutes without human approval.

## Automated path

1. Correlate the incident by `trace_id`, exact revision, deploy SHA and endpoint.
2. Distinguish dependency failure, application exception, overload, stale-data condition and client-only failure before remediation.
3. If the error began with a new revision, use the canonical exact traffic map and restore the last proven serving map.
4. If capacity is objectively saturated, create an infrastructure change proposal for Cloud Run min instances/concurrency; do not silently apply an unbounded scale-up.
5. Disable only a pre-approved nonessential read-only feature through an explicit fail-safe capability flag; never disable safety/risk/mutation controls.
6. Run the read-only synthetic and health proof after each remediation.
7. Stop after two unsuccessful automated attempts inside 15 minutes and escalate with evidence.

## Required evidence

- trace ID and request ID;
- exact Cloud Run revision and Git SHA;
- affected endpoints and status distribution;
- p50/p95/p99 latency where available;
- redacted browser network/console artifact for synthetic failures;
- failed-revision forensic artifact when applicable;
- action taken, before/after state, cooldown key and verification result.

## Closure

Close only after the target condition has recovered through at least three consecutive synthetic/uptime checks and the serving exact revision remains LIVE OFF/LOCKED with MutationPolicy ENFORCED.
