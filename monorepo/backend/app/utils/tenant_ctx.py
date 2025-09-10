from __future__ import annotations

from contextvars import ContextVar

_tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)


def set_current_tenant(tenant_id: str | None) -> None:
    _tenant_id_var.set(tenant_id)


def get_current_tenant() -> str | None:
    return _tenant_id_var.get()
