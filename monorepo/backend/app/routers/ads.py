from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth import require_admin_key, require_site_auth, resolve_tenant
from ..services.db import open_session, SiteCredential, AdsCampaign, AdsInsight
from ..services.crypto import encrypt_json
from ..services.ads_google import GoogleAdsAdapter
from ..services.ads_meta import MetaAdsAdapter

router = APIRouter(tags=["ads"], dependencies=[Depends(require_site_auth)])


@router.post("/ads/credentials", dependencies=[Depends(require_admin_key)])
async def upsert_credentials(request: Request, platform: str, credentials: dict):
    site_id = resolve_tenant(request)
    import json, datetime
    blob = encrypt_json(json.dumps(credentials))
    with open_session() as session:
        row = (
            session.query(SiteCredential)
            .filter(SiteCredential.site_id == site_id, SiteCredential.platform == platform)
            .one_or_none()
        )
        now = datetime.datetime.utcnow()
        if row is None:
            row = SiteCredential(site_id=site_id, platform=platform, credentials_json=blob, created_at=now, updated_at=now)
            session.add(row)
        else:
            row.credentials_json = blob
            row.updated_at = now
        session.commit()
    return {"ok": True}


@router.post("/ads/campaigns", dependencies=[Depends(require_admin_key)])
async def create_campaign(request: Request, platform: str, campaign: dict):
    site_id = resolve_tenant(request)
    import json
    with open_session() as session:
        session.add(AdsCampaign(site_id=site_id, platform=platform, campaign_json=json.dumps(campaign)))
        session.commit()
    return {"ok": True}


@router.get("/ads/campaigns")
async def list_campaigns(request: Request, platform: str | None = None, limit: int = 50):
    site_id = resolve_tenant(request)
    with open_session() as session:
        q = session.query(AdsCampaign).filter(AdsCampaign.site_id == site_id)
        if platform:
            q = q.filter(AdsCampaign.platform == platform)
        rows = q.order_by(AdsCampaign.id.desc()).limit(limit).all()
    return {"campaigns": [{"id": r.id, "platform": r.platform, "created_at": r.created_at.isoformat()} for r in rows]}


@router.post("/ads/insights", dependencies=[Depends(require_admin_key)])
async def ingest_insights(request: Request, platform: str, insights: dict):
    site_id = resolve_tenant(request)
    import json
    with open_session() as session:
        session.add(AdsInsight(site_id=site_id, platform=platform, insights_json=json.dumps(insights)))
        session.commit()
    return {"ok": True}


@router.get("/ads/insights")
async def list_insights(request: Request, platform: str | None = None, limit: int = 50):
    site_id = resolve_tenant(request)
    with open_session() as session:
        q = session.query(AdsInsight).filter(AdsInsight.site_id == site_id)
        if platform:
            q = q.filter(AdsInsight.platform == platform)
        rows = q.order_by(AdsInsight.id.desc()).limit(limit).all()
    return {"insights": [{"id": r.id, "platform": r.platform, "created_at": r.created_at.isoformat()} for r in rows]}


@router.post("/ads/providers/insights", dependencies=[Depends(require_admin_key)])
async def fetch_provider_insights(request: Request, platform: str, params: dict | None = None):
    site_id = resolve_tenant(request)
    adapter = {"google": GoogleAdsAdapter(), "meta": MetaAdsAdapter()}.get(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    try:
        data = adapter.get_insights(site_id, params or {})
    except Exception as e:
        # Return stub info when credentials not provided yet
        data = {"ok": False, "error": str(e), "insights": {"spend": 0, "clicks": 0, "impressions": 0}}
    return data


@router.post("/ads/providers/campaigns", dependencies=[Depends(require_admin_key)])
async def create_provider_campaign(request: Request, platform: str, campaign: dict):
    site_id = resolve_tenant(request)
    adapter = {"google": GoogleAdsAdapter(), "meta": MetaAdsAdapter()}.get(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    try:
        data = adapter.create_campaign(site_id, campaign)
    except Exception as e:
        data = {"ok": False, "error": str(e)}
    return data
