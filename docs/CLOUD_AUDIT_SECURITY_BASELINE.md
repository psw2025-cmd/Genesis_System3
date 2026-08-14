# Cloud Audit Security Baseline

Authority: GitHub `main` source, Google Cloud runtime. This baseline is ANALYZER/PAPER only and grants no broker order authority.

## Deterministic gates

- CodeQL advanced scanning: Python and JavaScript/TypeScript, `security-extended`.
- Dependabot: npm, root/backend pip, Docker, GitHub Actions.
- Security Audit Evidence: `npm audit`, `pip-audit`, Bandit; machine JSON plus Markdown; high/critical or known pip vulnerabilities fail closed.
- SonarQube/SonarQube Cloud: scanner is configuration-aware. Missing `SONAR_TOKEN` or `SONAR_PROJECT_KEY` is recorded as `BLOCKED_MISSING_CONFIGURATION`, never PASS.

## Required external configuration for Sonar execution

- GitHub secret: `SONAR_TOKEN`.
- GitHub variable: `SONAR_PROJECT_KEY`.
- SonarQube Cloud: set `SONAR_ORGANIZATION`; `SONAR_HOST_URL` is optional.
- SonarQube Server: set `SONAR_HOST_URL`; leave `SONAR_ORGANIZATION` empty.

No secret value is written to repository evidence.

## Closure rule

This baseline is not a production-readiness declaration. Deterministic security failures, missing external-provider proof, runtime safety failures, or broker/rotator failures keep the overall cloud audit open.
