from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple, Optional

from fastapi import UploadFile

from ..config import SETTINGS


def save_upload(tenant_id: str, file: UploadFile, customer_id: Optional[str] = None) -> Tuple[str, Path]:
    ext = Path(file.filename or "").suffix.lower()
    doc_id = str(uuid.uuid4())
    base_dir = Path(SETTINGS.data_dir) / "docs" / tenant_id
    tenant_dir = base_dir / customer_id if customer_id else base_dir
    try:
        tenant_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fallback to a local writable directory for tests or restricted envs
        fallback = Path("./data_fallback") / "docs" / tenant_id
        tenant_dir = fallback / customer_id if customer_id else fallback
        tenant_dir.mkdir(parents=True, exist_ok=True)
    dest = tenant_dir / f"{doc_id}{ext}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return doc_id, dest


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pdfminer.high_level import extract_text as pdf_extract

        return pdf_extract(str(path))
    elif ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    elif ext in {".docx"}:
        try:
            import docx  # python-docx

            doc = docx.Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""
    return ""
