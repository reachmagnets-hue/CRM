# CI/CD flow

Local dev → Dockerize & test → push to Git → GitHub Actions builds & pushes image → VPS pulls new image → container restarts.

ASCII diagram:

  Dev → git push main
        │
        ▼
  GitHub Actions (build & push image to GHCR)
        │
        ▼
  SSH to VPS → docker compose pull && up -d
        │
        ▼
  Nginx (80) → Backend (8000)

Key files:
- monorepo/backend/Dockerfile (production image)
- infra/docker-compose.prod.yml (VPS stack from GHCR)
- infra/nginx.conf.template (reverse proxy)
- .github/workflows/deploy.yml (CI/CD automation)
- infra/vps/provision_vps.sh (one-time VPS setup)
