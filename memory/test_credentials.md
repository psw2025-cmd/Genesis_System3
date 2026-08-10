# Test credentials — GENESIS SYSTEM 3

NOTE: App runs on Google Cloud Run, NOT in this pod. No local login flow.

- Live web URL: https://genesis-system3-web-doq2wplepa-el.a.run.app
- Dhan Client ID: 1106583741
- Dhan PIN: 197819 (stored in GCP secret `dhan-pin` v10 — USER MUST ROTATE THIS PIN, it was exposed in chat)
- GCP project: system3-openalgo-safe / asia-south1
- Secrets in GCP Secret Manager: dhan-pin, dhan-totp-secret, dhan-access-token, system3-dhan-client-id
- Broker status check: GET {live_url}/api/broker/status
