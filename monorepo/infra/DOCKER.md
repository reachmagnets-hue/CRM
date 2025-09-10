# Docker usage

## Dev

1) Copy env file and edit:

```
cp ../backend/.env.example ../backend/.env
```

2) Start dev compose (backend + nginx):

```
docker compose -f docker-compose.dev.yml up --build
```

- Backend: http://localhost:8000
- Nginx proxy: http://localhost:8080

## Prod-ish

1) Ensure `../backend/.env` has real secrets and domains.
2) Start compose:

```
docker compose up -d --build
```

- Nginx exposes :80 and proxies `/api/` to backend, serves `/static/audio/`.

## Important env keys

- API_PUBLIC_KEYS, ADMIN_API_KEY
- TENANT_DOMAINS, TENANT_ORIGINS, BOOKING_PAGES
- TWILIO_VOICE_WEBHOOK_BASE, TWILIO_NUMBER_MAP
- DATA_DIR, CHROMA_DIR
- Optional WordPress: WP_WEBHOOK_URL, WP_WEBHOOK_KEY

## Volumes

- `../backend/data` (audio/uploads)
- `../backend/chroma` (vector store)
