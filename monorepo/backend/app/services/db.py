from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, create_engine, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from ..config import SETTINGS
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


_engine = None


def _get_engine():
    global _engine
    if _engine is not None:
        return _engine
    dsn = SETTINGS.default_sql_dsn
    if not dsn:
        # Dev fallback to SQLite in DATA_DIR when MySQL DSN is not yet configured
        db_path = Path(SETTINGS.data_dir) / "central.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        dsn = f"sqlite:///{db_path}"
    _engine = create_engine(dsn, pool_pre_ping=True)
    Base.metadata.create_all(_engine)
    return _engine


def open_session() -> Session:
    engine = _get_engine()
    return Session(engine)
