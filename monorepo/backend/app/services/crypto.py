from __future__ import annotations

import base64
from typing import Optional

from ..config import SETTINGS

try:
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover
    Fernet = None  # type: ignore


def _get_fernet():
    if not SETTINGS.crypto_secret or Fernet is None:
        return None
    key = SETTINGS.crypto_secret
    # Allow plain secret to be converted to a fernet key via base64 padding if needed
    try:
        fkey = key if key.startswith("gAAAA") else base64.urlsafe_b64encode(key.encode("utf-8")).decode("utf-8")
        return Fernet(fkey)
    except Exception:  # pragma: no cover
        return None


def encrypt_json(plaintext: str) -> str:
    f = _get_fernet()
    if not f:
        return plaintext
    return f.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_json(ciphertext: str) -> str:
    f = _get_fernet()
    if not f:
        return ciphertext
    try:
        return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except Exception:
        return ciphertext
