=== Ollama Chat (Multi-tenant) ===
Contributors: you
Tags: chat, ai, rag
Requires at least: 5.6
Tested up to: 6.x
Stable tag: 0.1.0
License: GPLv2 or later

Floating chat widget that connects to a shared FastAPI backend. Shortcode: [ollama_chat tenant="auto"].

== Installation ==
1. Upload the `ollama-chat` folder to `/wp-content/plugins/`.
2. Activate the plugin.
3. Go to Settings > Ollama Chat and set API Base URL and Public Key.
4. Add `[ollama_chat tenant="auto"]` to any page.

For broader WordPress integration patterns (server-to-server pull, push/webhooks, reverse proxy), see `monorepo/docs/WP_INTEGRATION.md`.
