# SEC-1 frontend npm audit remediation (2026-08-16)

## Goal
Clear the repository Security Audit Evidence hard failure `npm_audit` without `--force`, `--legacy-peer-deps`, advisory ignores, or weakened policy.

## Verified published fixes
| Package | Vulnerable range (audit) | Chosen fixed version |
|---------|--------------------------|----------------------|
| vite | <=6.4.2 | **6.4.3** |
| postcss | <=8.5.22 | **8.5.26** |
| @vitejs/plugin-react | peer needed Vite 6 support | **4.7.0** (peer: `^4 \|\| ^5 \|\| ^6 \|\| ^7`) |
| esbuild (transitive) | <=0.24.2 | **0.25.12** via vite 6.4.3 |
| nanoid (transitive) | <=3.3.17 | **3.3.18** via postcss 8.5.26 |

Vite 8 was rejected for this wave: Dependabot PR #204 / audit `fixAvailable` points at 8.x, but current plugin peer policy and PR #217 keep remediation on the Vite 6.4.3+ compatible major.

## Local proof (this PR)
- `npm ci` → 0 vulnerabilities
- `npm audit` → 0 vulnerabilities
- `npm run build` → vite 6.4.3 production build PASS

## Out of scope
- UI functional edits (UI-OBS-1 PR #251 frozen)
- BR-1 broker files (PR #250)
- LIVE / orders / token / GCP mutations
