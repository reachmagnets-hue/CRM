from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, DateTime, create_engine, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from ..config import SETTINGS
from ..utils.tenant_ctx import get_current_tenant
from pathlib import Path


class Base(DeclarativeBase):
    pass


class ChatLog(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    question: Mapped[str] = mapped_column(Text())
    answer: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    data_json: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class CallLog(Base):
    __tablename__ = "calls"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    from_number: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    transcript: Mapped[str] = mapped_column(Text())
    service_intent: Mapped[Optional[str]] = mapped_column(String(128))
    outcome: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    metadata_json: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class AdsCampaign(Base):
    __tablename__ = "ads_campaigns"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True)
    campaign_json: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class AdsInsight(Base):
    __tablename__ = "ads_insights"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True)
    insights_json: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)


class SiteCredential(Base):
    __tablename__ = "site_credentials"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(255), index=True)
    platform: Mapped[str] = mapped_column(String(64), index=True)
    credentials_json: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("site_id", "platform", name="uq_site_platform"),)


_engines: dict[str, Any] = {}


def _get_engine():
    tenant = get_current_tenant() or "default"
    if tenant in _engines:
        return _engines[tenant]

    # Priority: tenant-specific DSN -> default DSN -> sqlite fallback
    dsn = None
    # TENANT_SQL_DSN is a mapping tenant -> [DSN]
    tmap = SETTINGS.tenant_sql_dsn.get(tenant) if SETTINGS.tenant_sql_dsn else None
    if tmap and len(tmap) > 0:
        dsn = tmap[0]
    if not dsn:
        dsn = SETTINGS.default_sql_dsn
    if not dsn:
        db_name = f"{tenant}.db" if tenant and tenant != "default" else "central.db"
        db_path = Path(SETTINGS.data_dir) / db_name
        db_path.parent.mkdir(parents=True, exist_ok=True)
        dsn = f"sqlite:///{db_path}"

    engine = create_engine(dsn, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    _engines[tenant] = engine
    return engine


def open_session() -> Session:
    engine = _get_engine()
    return Session(engine)
