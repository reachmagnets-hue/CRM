from __future__ import annotations

from typing import Any, Dict
import json

from .db import open_session, SiteCredential, AdsInsight
from .crypto import decrypt_json


class GoogleAdsAdapter:
    platform = "google"

    def _get_creds(self, site_id: str) -> Dict[str, Any]:
        with open_session() as session:
            row = (
                session.query(SiteCredential)
                .filter(SiteCredential.site_id == site_id, SiteCredential.platform == self.platform)
                .one_or_none()
            )
        if not row:
            raise RuntimeError("Google Ads credentials not found for site")
        data = json.loads(decrypt_json(row.credentials_json))
        required = ["developer_token", "client_id", "client_secret", "refresh_token", "login_customer_id"]
        for k in required:
            if not data.get(k):
                raise RuntimeError(f"Missing Google Ads credential: {k}")
        return data

    def get_insights(self, site_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: in real adapter, call Google Ads API
        # For now, return a dummy payload and store to DB
        sample = {"spend": 0, "clicks": 0, "impressions": 0}
        with open_session() as session:
            session.add(AdsInsight(site_id=site_id, platform=self.platform, insights_json=json.dumps(sample)))
            session.commit()
        return {"ok": True, "insights": sample}

    def create_campaign(self, site_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: return accepted
        return {"ok": True}
