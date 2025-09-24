# Docker usage

## Dev

1) Copy env file and edit:

```
cp ../backend/.env.example ../backend/.env
```

2) Start dev compose (backend + Caddy):

```
docker compose -f docker-compose.dev.yml up --build
```

- Backend: http://localhost:8000
- Caddy proxy: http://localhost:8080

## Prod-ish

1) Ensure `../backend/.env` has real secrets and domains (or use the CI to inject a .env on the VPS).
2) Start compose:

```
docker compose up -d --build
```

- Caddy exposes :80 (and optionally :443) and reverse-proxies to backend, serves `/static/audio/`.

For VPS/Hostinger deployment with prebuilt images and GitHub Actions, see `.github/workflows/deploy.yml` and `infra/DOCKER.md` in this folder.

## Important env keys

- ADMIN_API_KEY, SITE_API_KEYS
- TENANT_DOMAINS, TENANT_ORIGINS
- DATA_DIR, CHROMA_DIR
- OLLAMA_BASE, OLLAMA_MODEL, EMBED_MODEL
- Optional WordPress: WP_WEBHOOK_URL, WP_WEBHOOK_KEY

## Volumes

- `../backend/data` (audio/uploads)
- `../backend/chroma` (vector store)
