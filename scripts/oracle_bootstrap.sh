#!/usr/bin/env bash
set -euo pipefail

# Genesis System3 Oracle VM bootstrap.
# Run once on a fresh Ubuntu Oracle VM before installing the GitHub self-hosted runner.
# This script installs Docker Engine and Docker Compose plugin.

if [ "${EUID}" -eq 0 ]; then
  echo "Do not run as root. Run as the normal Ubuntu user with sudo access."
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required."
  exit 1
fi

echo "[1/7] Updating apt packages"
sudo apt-get update -y

echo "[2/7] Installing prerequisites"
sudo apt-get install -y ca-certificates curl gnupg lsb-release ufw

echo "[3/7] Installing Docker official repository"
sudo install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
fi
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

echo "[4/7] Installing Docker Engine and Compose plugin"
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "[5/7] Enabling Docker service"
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker "$USER"

echo "[6/7] Configuring local firewall defaults"
sudo ufw allow OpenSSH || true
sudo ufw allow 8000/tcp || true
sudo ufw status || true

echo "[7/7] Proof"
docker --version || sudo docker --version
docker compose version || sudo docker compose version

echo "BOOTSTRAP_PASS"
echo "IMPORTANT: Log out and log back in, or reboot, so Docker group membership becomes active for user: $USER"
