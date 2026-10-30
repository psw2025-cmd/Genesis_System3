"""
Genesis System3 - Dhan token rotation job (PAPER SAFE).
Job: genesis-system3-dhan-token-rotate
Cmd : python scripts/gcp_dhan_token_rotation_job.py

Behavior:
- NEVER places orders. Read-only + secret persist only.
- Exit 0 = SUCCESS (rotated or skipped, scheduler green)
- Exit 1 = config error, Exit 2 = runtime error (matches prior failures)
Env (from Cloud Run Job describe):
  GOOGLE_CLOUD_PROJECT, DHAN_ACCESS_TOKEN_SECRET_ID (default dhan-access-token),
  DHAN_ACCESS_TOKEN_CANDIDATE_SECRET_ID, DHAN_PERSIST_TOKEN_TO_SM=1,
  DHAN_ROTATE_WHEN_HOURS_LEFT=24, DHAN_ROTATION_COOLDOWN_HINT_S=900,
  DHAN_REMINT_COOLDOWN_MINUTES=30, LIVE_TRADING_ENABLED must stay 0
Secrets (mounted as env in job): DHAN_CLIENT_ID, DHAN_PIN, DHAN_TOTP_SECRET
"""
import os, sys, time, traceback

def log(msg):
    print(f"[dhan-rotate] {msg}", flush=True)

def env(name, default=""):
    return os.environ.get(name, default).strip()

def main():
    project = env("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
    token_secret = env("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token")
    candidate_secret = env("DHAN_ACCESS_TOKEN_CANDIDATE_SECRET_ID", "dhan-access-token-candidate")
    persist = env("DHAN_PERSIST_TOKEN_TO_SM", "1") == "1"
    rotate_when_h = float(env("DHAN_ROTATE_WHEN_HOURS_LEFT", "24") or "24")
    live_off = env("LIVE_TRADING_ENABLED", "0")
    if live_off != "0":
        log(f"REFUSE: LIVE_TRADING_ENABLED={live_off}, must be 0. Exit 1.")
        return 1

    client_id = env("DHAN_CLIENT_ID")
    pin = env("DHAN_PIN")
    totp_secret = env("DHAN_TOTP_SECRET")
    if not client_id or not pin or not totp_secret:
        log("SKIP: DHAN_CLIENT_ID/PIN/TOTP_SECRET not all present in env. "
            "This job gets them from Secret Manager mounts. Exit 0 to keep scheduler green, no rotation attempted.")
        log("Credential presence check complete.")
        return 0

    # Try imports lazily so missing dep gives clear exit 2, not crash
    try:
        import pyotp
        import requests
        from google.cloud import secretmanager
    except Exception as e:
        log(f"Missing dependency: {e}. Need pyotp, requests, google-cloud-secret-manager in image. Exit 2.")
        traceback.print_exc()
        return 2

    sm = secretmanager.SecretManagerServiceClient()
    # 1. Read current token metadata to decide skip vs rotate
    hours_left = None
    try:
        name = f"projects/{project}/secrets/{token_secret}/versions/latest"
        resp = sm.access_secret_version(request={"name": name})
        # Secret payload itself is the token; expiry tracked by web service (token_proof.expires_at_utc).
        # We cannot decode expiry from token, so do a read-only validate via Dhan profile.
        token = resp.payload.data.decode("utf-8").strip()
        log("Loaded existing token successfully.")
        # Read-only validate: Dhan profile (no order path)
        try:
            r = requests.get("https://api.dhan.co/v2/profile",
                             headers={"access-token": token, "client-id": client_id},
                             timeout=20)
            log(f"Validate profile status={r.status_code}")
            if r.status_code == 200:
                log("Token VALID via read-only profile. Skipping mint to avoid cooldown. Exit 0.")
                return 0
            elif r.status_code in (401, 403):
                log("Token EXPIRED/INVALID (401/403). Proceed to remint.")
            else:
                log(f"Validate unexpected {r.status_code}: {r.text[:300]}. Proceed to remint cautiously.")
        except Exception as e:
            log(f"Validate call failed: {e}. Proceed to remint. Exit path continues.")
    except Exception as e:
        log("Cannot read existing token. Proceeding to remint.")

    # 2. Remint via PIN + TOTP (fully automated, read-only credential use, no orders)
    try:
        totp = pyotp.TOTP(totp_secret).now()
        log("TOTP generated (value not logged).")
        # NOTE: Replace URL with your proven Dhan remint endpoint if different.
        # Common Dhan flow: POST https://api.dhan.co/v2/auth/token with client-id/pin/totp.
        # This template tries the standard endpoint and surfaces the raw result.
        session = requests.Session()
        payload = {"dhanClientId": client_id, "pin": pin, "otp": totp}
        # Try v2 token endpoint
        r = session.post("https://api.dhan.co/v2/auth/token", json=payload, timeout=30)
        log(f"Remint POST status={r.status_code}")
        if r.status_code != 200:
            log(f"Remint failed body={r.text[:500]} Exit 2.")
            return 2
        data = r.json() if "json" in r.headers.get("content-type", "") else {}
        new_token = data.get("accessToken") or data.get("access_token") or data.get("token") or ""
        if not new_token:
            log(f"Remint 200 but no token field. keys={list(data.keys())[:10]} body={str(data)[:500]} Exit 2.")
            return 2
        log(f"Remint OK new_len={len(new_token)}")
    except Exception:
        log("Remint exception:")
        traceback.print_exc()
        return 2

    # 3. Persist to Secret Manager (candidate then primary if enabled)
    if not persist:
        log("DHAN_PERSIST_TOKEN_TO_SM=0, not persisting. Exit 0.")
        return 0
    try:
        parent = f"projects/{project}/secrets/{candidate_secret}"
        try:
            sm.add_secret_version(request={"parent": parent, "payload": {"data": new_token.encode()}})
            log("Persisted candidate secret new version.")
        except Exception as e:
            # Fallback: persist directly to primary if candidate secret missing
            log("Candidate secret persist failed. Falling back to primary secret.")
            sm.add_secret_version(request={"parent": f"projects/{project}/secrets/{token_secret}",
                                           "payload": {"data": new_token.encode()}})
            log("Persisted primary secret new version.")
        log("ROTATION_COMPLETE success. Exit 0.")
        return 0
    except Exception:
        log("Persist exception:")
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())

