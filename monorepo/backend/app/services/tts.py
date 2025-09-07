from __future__ import annotations

import subprocess
import uuid
from pathlib import Path

from ..config import SETTINGS


def synthesize_to_file(text: str, voice: str = "en_US-amy") -> str:
    """Synthesize text using Piper CLI and return public URL path.
    Requires Piper installed and configured; this is a placeholder interface.
    """
    audio_dir = Path(SETTINGS.data_dir) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    out = audio_dir / f"{uuid.uuid4()}.wav"
    try:
        # TODO: integrate actual Piper command; placeholder writes empty wav
        out.write_bytes(b"RIFF\x00\x00\x00\x00WAVEfmt ")
    except Exception:
        out.write_bytes(b"")
    # The file will be served via /static/audio in dev or Nginx in prod
    return f"/static/audio/{out.name}"
