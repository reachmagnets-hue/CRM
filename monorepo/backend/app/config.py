from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv


def _parse_map(env_val: str, pair_sep: str = ";", kv_sep: str = ":", list_sep: str = ",") -> Dict[str, List[str]]:
    """Parse env like "site_a:example.com,www.example.com;site_b:foo.com" into dict.
    Returns mapping of key -> list[str].
    """
    result: Dict[str, List[str]] = {}
    if not env_val:
        return result
    for pair in env_val.split(pair_sep):
        pair = pair.strip()
        if not pair:
            continue
        if kv_sep not in pair:
            continue
        k, v = pair.split(kv_sep, 1)
        result[k.strip()] = [item.strip() for item in v.split(list_sep) if item.strip()]
    return result


@dataclass
class Settings:
    api_public_keys: List[str]
    admin_api_key: str
    ollama_base: str
    ollama_model: str
    embed_model: str
    store: str
    chroma_dir: str
    pinecone_api_key: str | None
    pinecone_index: str | None
    data_dir: str
    rate_limit: str
    tenant_domains: Dict[str, List[str]]
    tenant_origins: Dict[str, List[str]]
    twilio_voice_webhook_base: str | None
    booking_pages: Dict[str, List[str]]
    twilio_number_map: Dict[str, List[str]]


def get_settings() -> Settings:
    # Load environment variables from a .env file if present
    # Must run before reading any os.getenv to ensure values are available when running locally
    load_dotenv(override=True)
    api_public_keys_env = os.getenv("API_PUBLIC_KEYS", "").strip()
    api_public_keys = [k.strip() for k in api_public_keys_env.split(",") if k.strip()]
    return Settings(
        api_public_keys=api_public_keys,
        admin_api_key=os.getenv("ADMIN_API_KEY", ""),
        ollama_base=os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3"),
        embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        store=os.getenv("STORE", "chroma"),
        chroma_dir=os.getenv("CHROMA_DIR", "./chroma"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY", "") or None,
        pinecone_index=os.getenv("PINECONE_INDEX", "") or None,
        data_dir=os.getenv("DATA_DIR", "./data"),
        rate_limit=os.getenv("RATE_LIMIT", "20/minute"),
        tenant_domains=_parse_map(os.getenv("TENANT_DOMAINS", "")),
        tenant_origins=_parse_map(os.getenv("TENANT_ORIGINS", "")),
        twilio_voice_webhook_base=os.getenv("TWILIO_VOICE_WEBHOOK_BASE", "") or None,
        booking_pages=_parse_map(os.getenv("BOOKING_PAGES", "")),
    # Map tenant_id -> list of Twilio numbers (e.g. "+15551234567,+15557654321")
    twilio_number_map=_parse_map(os.getenv("TWILIO_NUMBER_MAP", "")),
    )


SETTINGS = get_settings()
