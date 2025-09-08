from __future__ import annotations

from typing import Protocol, Any, Dict


class AdsAdapter(Protocol):
    platform: str

    def create_campaign(self, site_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def get_insights(self, site_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        ...


class DummyAdsAdapter:
    platform = "dummy"

    def create_campaign(self, site_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "campaign": campaign}

    def get_insights(self, site_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "insights": {"spend": 0, "clicks": 0}}
