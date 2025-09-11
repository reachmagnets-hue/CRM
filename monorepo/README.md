# Multi-tenant RAG Backend + WP Plugin Monorepo

This monorepo provides a FastAPI backend that powers multiple WordPress sites with a shared RAG chatbot, document ingestion, search, and Twilio voice.

## Quick start

1. Install Ollama and pull models:
   - Chat: `llama3` (or `mistral`)
   - Embeddings: `nomic-embed-text`
2. Copy env: `cp backend/.env.example backend/.env` and edit tenant mappings and keys.
3. (Optional) `./scripts/dev_bootstrap.sh`
4. Run dev server:
   - `make -C backend dev`
5. Ingest a doc: `make -C backend ingest FILE=path/to/file.txt TENANT=site_a`
6. Install the WP plugin from `wp-plugins/ollama-chat` on each site and configure Settings.

WordPress integration patterns and code examples: see `docs/WP_INTEGRATION.md`.

## Multi-tenancy

- Map Host header domains to tenant IDs via `TENANT_DOMAINS` in env.
- CORS per-tenant allowed origins via `TENANT_ORIGINS`.
- Vector collections are namespaced per tenant.

## Twilio

- Point your number Voice webhooks to `/api/v1/twilio/voice` and `/api/v1/twilio/handle`.
- Configure TTS if desired (see `scripts/create_piper_voice.sh`).
