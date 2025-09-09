#!/usr/bin/env bash
set -euo pipefail

APP_PATH=${APP_PATH:-/opt/rag}
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER" || true
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Installing docker compose plugin..."
  sudo apt-get install -y docker-compose-plugin || true
fi

sudo mkdir -p /opt/rag-data /opt/rag-chroma "$APP_PATH"
sudo chown -R "$USER":"$USER" /opt/rag-data /opt/rag-chroma "$APP_PATH"
echo "VPS ready at $APP_PATH. Place docker-compose.prod.yml, nginx.conf.template, and .env there."
