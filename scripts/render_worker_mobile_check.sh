#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

echo "========================================"
echo "RETIRED — Render.com worker mobile check"
echo "========================================"
echo "Render.com hosting is retired."
echo "Production is GCP Cloud Run: genesis-system3-web"
echo "UI=https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/"

if [ -f "$ROOT/render.yaml" ]; then
  echo "RESULT=FAIL"
  echo "REASON=render.yaml is present; delete it. Cloud Run is the only host."
  exit 2
fi

echo "RESULT=PASS"
echo "REASON=render.yaml absent; Cloud Run is the only production host."
exit 0
