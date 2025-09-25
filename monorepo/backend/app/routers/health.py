from __future__ import annotations

import time
from fastapi import APIRouter, Response

from ..models.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ts=time.time(), version="0.1.0")

@router.head("/health")
def health_head() -> Response:
    # Lightweight HEAD for load balancers and proxies
    return Response(status_code=200)


@router.get("/api/v1/health", response_model=HealthResponse)
def health_v1() -> HealthResponse:
    # Alias for consistency with other API routes
    return HealthResponse(ts=time.time(), version="0.1.0")

@router.head("/api/v1/health")
def health_v1_head() -> Response:
    return Response(status_code=200)
