# Non-Docker Deployment (Systemd + Nginx + Uvicorn)

If you prefer running the FastAPI backend directly on the VPS instead of Docker, use this guide. This sets up:

- Python virtual environment at `/opt/rag-backend/venv`
- Code under `/opt/rag-backend/app`
- Systemd service: `rag-backend.service`
- Nginx reverse proxy on port 80 (optional SSL via certbot)

## 1. Prerequisites

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nginx git curl
```

## 2. Create backend directory & virtualenv

```bash
sudo mkdir -p /opt/rag-backend
sudo chown -R "$USER":"$USER" /opt/rag-backend
cd /opt/rag-backend
python3 -m venv venv
source venv/bin/activate
```

## 3. Copy project code (from your repo clone)

From your local machine or a temporary clone on the server:

```bash
# Assuming repo cloned at ~/CRM
rsync -a --delete ~/CRM/monorepo/backend/app /opt/rag-backend/
cp ~/CRM/monorepo/backend/requirements.txt /opt/rag-backend/
cp ~/CRM/monorepo/backend/.env.example /opt/rag-backend/.env  # then edit
```

Install dependencies:

```bash
source /opt/rag-backend/venv/bin/activate
pip install --upgrade pip
pip install -r /opt/rag-backend/requirements.txt
```

Edit `.env` and set real keys (ADMIN_API_KEY, API_PUBLIC_KEYS, TENANT_DOMAINS, etc.).

## 4. Systemd service

Service file (already present in repo at `monorepo/infra/systemd/rag-backend.service`):

```ini
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
```

Install & enable:

```bash
sudo cp monorepo/infra/systemd/rag-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rag-backend.service
sudo systemctl status rag-backend.service
```

## 5. Nginx reverse proxy

Create `/etc/nginx/sites-available/rag-backend`:

```nginx
server {
    server_name api.example.com;  # change
    listen 80;

    location /static/audio/ {
        alias /opt/rag-backend/app/data/audio/; # adjust if data dir different
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
```

Activate:

```bash
sudo ln -s /etc/nginx/sites-available/rag-backend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 6. SSL (Let’s Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
```

Auto-renew is installed via systemd timer by default (`systemctl list-timers | grep certbot`).

## 7. Updating code

```bash
cd ~/CRM
git pull origin main
rsync -a --delete monorepo/backend/app /opt/rag-backend/
cp monorepo/backend/requirements.txt /opt/rag-backend/
source /opt/rag-backend/venv/bin/activate
pip install -r /opt/rag-backend/requirements.txt
sudo systemctl restart rag-backend.service
```

## 8. Logs & troubleshooting

```bash
sudo journalctl -u rag-backend.service -f
sudo nginx -t
sudo systemctl status rag-backend.service
```

## 9. Optional: Gunicorn workers

For higher concurrency you can swap ExecStart:

```ini
ExecStart=/opt/rag-backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000 --timeout 60
```

Then `sudo systemctl restart rag-backend.service`.

## 10. Data directories

If you set `DATA_DIR=/opt/rag-data` and `CHROMA_DIR=/opt/rag-chroma` in `.env`, create them:

```bash
sudo mkdir -p /opt/rag-data /opt/rag-chroma
sudo chown -R www-data:www-data /opt/rag-data /opt/rag-chroma
```

Update service `EnvironmentFile` or `.env` accordingly.

## 11. Quick smoke test

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS https://api.example.com/health
```

If you already use Docker in production, keep that; this alternative is for smaller VPS setups or when you prefer direct system control.

---
Automation script: see `infra/vps/provision_non_docker.sh`.
