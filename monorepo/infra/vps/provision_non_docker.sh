#!/usr/bin/env bash
set -euo pipefail

# Simple provisioning for non-Docker deployment of the FastAPI backend.
# Usage:
#   sudo bash provision_non_docker.sh --domain api.example.com [--data-dir /opt/rag-data] [--chroma-dir /opt/rag-chroma]
# After run: edit /opt/rag-backend/.env then: systemctl restart rag-backend

DOMAIN=""
DATA_DIR="/opt/rag-data"
CHROMA_DIR="/opt/rag-chroma"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --chroma-dir) CHROMA_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$DOMAIN" ]]; then
  echo "--domain required" >&2
  exit 1
fi

echo "[+] Installing packages"
apt update -y
apt install -y python3 python3-venv python3-pip nginx git curl

echo "[+] Creating application directories"
mkdir -p /opt/rag-backend /opt/rag-backend/app "$DATA_DIR" "$CHROMA_DIR"
chown -R $SUDO_USER:$SUDO_USER /opt/rag-backend "$DATA_DIR" "$CHROMA_DIR" || true

cd /opt/rag-backend
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
source venv/bin/activate

echo "[+] Creating placeholder .env"
cat > /opt/rag-backend/.env <<EOF
ADMIN_API_KEY=admin_CHANGE_ME
API_PUBLIC_KEYS=pk_live_CHANGE_ME
DATA_DIR=$DATA_DIR
CHROMA_DIR=$CHROMA_DIR
STORE=chroma
RATE_LIMIT=20/minute
EOF

echo "[+] Writing systemd service"
cat > /etc/systemd/system/rag-backend.service <<EOF
[Unit]
Description=RAG Backend Service (Non-Docker)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/rag-backend
EnvironmentFile=/opt/rag-backend/.env
ExecStart=/opt/rag-backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "[+] Nginx site config"
cat > /etc/nginx/sites-available/rag-backend <<EOF
server {
    server_name $DOMAIN;
    listen 80;

    location /static/audio/ {
        alias $DATA_DIR/audio/;
        add_header Cache-Control "public, max-age=31536000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/rag-backend /etc/nginx/sites-enabled/rag-backend
nginx -t && systemctl reload nginx

echo "[+] Installing Python deps (backend requirements not copied yet)"
pip install --upgrade pip uvicorn fastapi python-dotenv orjson

systemctl daemon-reload
systemctl enable --now rag-backend || true

echo "[+] Done. Next steps:"
echo "  1) rsync or copy your backend app code into /opt/rag-backend/app"
echo "  2) pip install -r /opt/rag-backend/requirements.txt (after copying)"
echo "  3) sudo systemctl restart rag-backend"
echo "  4) (Optional) certbot --nginx -d $DOMAIN"
