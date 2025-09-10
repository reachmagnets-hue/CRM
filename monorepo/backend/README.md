# Backend quickstart

- Health: GET /health
- API base: /api/v1

## WordPress via WP Webhooks

Receive (WordPress -> Backend):
- URL: https://<your-server>/api/v1/webhooks/wp
- Method: POST
- Headers:
  - X-Site-Id: <tenant/site id>
  - X-Api-Key: <site api key> (map in SITE_API_KEYS)
- Body (example):
  {
    "event": "form_submission",
    "data": { "name": "John", "phone": "+1..." },
    "sent_at": 1710000000
  }

Send (Backend -> WordPress):
- Configure env in `.env`:
  - WP_WEBHOOK_URL: WP Webhooks Receive Data URL
  - WP_WEBHOOK_KEY: optional shared secret (produces X-Webhook-Secret HMAC-SHA256)

## Required env

See `.env.example`. Important:
- SITE_API_KEYS=site_a:key1;site_b:key2
- TENANT_DOMAINS / TENANT_ORIGINS for CORS/tenant routing
- DATA_DIR and CHROMA_DIR for storage

## Dev

cp .env.example .env
uvicorn app.main:app --reload
