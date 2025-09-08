from __future__ import annotations

from typing import Protocol, Any, Dict


class TelephonyAdapter(Protocol):
    provider: str

    def make_call(self, site_id: str, to_number: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def parse_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...


class DummyTelephonyAdapter:
    provider = "dummy"

    def make_call(self, site_id: str, to_number: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True}

    def parse_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data
