#!/usr/bin/env bash
set -euo pipefail

echo "Restarting Genesis System3 backend on Oracle VM"

test -f docker-compose.oracle.yml

docker compose -f docker-compose.oracle.yml pull genesis-backend
docker compose -f docker-compose.oracle.yml up -d genesis-backend
docker compose -f docker-compose.oracle.yml ps

bash scripts/oracle_healthcheck.sh
