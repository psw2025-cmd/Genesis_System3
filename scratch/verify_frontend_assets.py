import requests
import re

url = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/"
r = requests.get(url, timeout=10)
print(f"UI HTML Status: {r.status_code}")
assets = re.findall(r'(?:src|href)="(/ui/assets/[^"]+)"', r.text)
print(f"Assets found: {assets}")

all_ok = True
for a in assets:
    a_url = f"https://genesis-system3-web-doq2wplepa-el.a.run.app{a}"
    ar = requests.get(a_url, timeout=10)
    size = len(ar.content)
    print(f"Asset {a} -> HTTP {ar.status_code} ({size} bytes)")
    if ar.status_code != 200:
        all_ok = False

# Also check deploy provenance
prov_url = "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/assets/deploy-provenance.json"
pr = requests.get(prov_url, timeout=10)
print(f"Deploy Provenance: HTTP {pr.status_code} -> {pr.text[:200]}")

if all_ok and pr.status_code == 200:
    print("\nALL FRONTEND ASSETS AND PROVENANCE VERIFIED WITH HTTP 200 SUCCESS!")
else:
    print("\nSOME ASSETS FAILED")
