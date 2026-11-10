import pyotp
import requests
from google.cloud import secretmanager

PROJECT = "system3-openalgo-safe"
client = secretmanager.SecretManagerServiceClient()


def get_secret(n):
    p = f"projects/{PROJECT}/secrets/{n}/versions/latest"
    return client.access_secret_version(request={"name": p}).payload.data.decode().strip()


def rotate(request=None):
    cid = get_secret("dhan-client-id")
    pin = get_secret("dhan-pin")
    sec = get_secret("dhan-totp-secret")
    totp = pyotp.TOTP(sec).now()
    url = f"https://auth.dhan.co/app/generateAccessToken?dhanClientId={cid}&pin={pin}&totp={totp}"
    r = requests.post(url, timeout=15)
    if r.status_code == 200 and "accessToken" in r.text:
        tok = r.json()["accessToken"]
        parent = f"projects/{PROJECT}/secrets/dhan-access-token"
        client.add_secret_version(request={"parent": parent, "payload": {"data": tok.encode()}})
        return ("SUCCESS", 200) if request is not None else True
    return ("FAILED", 500) if request is not None else False


if __name__ == "__main__":
    print(rotate())
