# Hostinger deployment (Docker + GitHub Actions)

This app deploys as two containers: backend (FastAPI) and nginx. For Hostinger VPS or any Ubuntu server with Docker, use the provided compose and the prebuilt image from GHCR.

## Prereqs

- Hostinger VPS (Ubuntu) with SSH access
- Docker Engine + docker compose plugin (the `provision_vps.sh` can help)
- Domain DNS pointing to the server (optional but recommended)

## One-time server setup

1) SSH into the server and create app/data dirs

   mkdir -p /opt/rag-data /opt/rag-chroma /opt/rag

2) Install Docker & compose (if missing)

   curl -fsSL https://get.docker.com | sh
   sudo apt-get install -y docker-compose-plugin || true

3) Put files under APP path (default /opt/rag)

   - docker-compose.prod.yml
   - nginx.conf.template
   - .env (see `.env.example` for keys)

4) Test locally

   cd /opt/rag
   IMAGE=ghcr.io/reachmagnets-hue/crm-backend:latest docker compose -f docker-compose.prod.yml up -d
   curl -fsS http://localhost/health

## GitHub Actions deployment

Already included: `.github/workflows/deploy.yml` builds/pushes the image and deploys to your VPS.

Set these in GitHub repo settings > Secrets and variables > Actions:

- VPS_HOST: your.server.com or IP
- VPS_USER: ssh user
- VPS_SSH_KEY: private key contents (starts with `-----BEGIN OPENSSH PRIVATE KEY-----`)
- VPS_APP_PATH: e.g. /opt/rag
- Optional: PROD_ENV: Base64 of your `.env` file (run `base64 -w0 .env` locally and paste)
- Optional: GHCR_USERNAME and GHCR_PAT if your package is private

Push to `main` to trigger build and deploy. The workflow will:

- Build Docker image from `monorepo/backend/Dockerfile`
- Push to GHCR at `ghcr.io/reachmagnets-hue/crm-backend`
- Copy compose and nginx files to VPS
- Write `.env` (if `PROD_ENV` is provided)
- `docker compose up -d` and smoke test `/health`

## Hostinger Docker Compose UI (optional)

The workflow copies files into `$APP_PATH/auto_body` for their UI. You can also upload `.env` there if you prefer managing via the panel.

## Ports & reverse proxy

- Nginx container listens on 80 and proxies:
  - `/api/` -> backend:8000
  - `/health` passthrough
  - `/static/audio/` served from host `/opt/rag-data/audio`

If you need HTTPS, terminate TLS at an external proxy or use Hostinger’s options. Alternatively, deploy Traefik/Caddy as a separate service.

## Troubleshooting

- Check logs: `docker compose -f docker-compose.prod.yml logs -f backend nginx`
- Verify volumes exist and are writable: `/opt/rag-data`, `/opt/rag-chroma`
- Ensure `.env` contains real keys for `ADMIN_API_KEY`, `API_PUBLIC_KEYS`, and tenant mappings.
