from __future__ import annotations

import time
from fastapi import APIRouter

from ..models.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ts=time.time(), version="0.1.0")


@router.get("/api/v1/health", response_model=HealthResponse)
def health_v1() -> HealthResponse:
    # Alias for consistency with other API routes
    return HealthResponse(ts=time.time(), version="0.1.0")
