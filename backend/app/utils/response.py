"""Common {success, data, meta} / {success, error} response envelope (API spec S4)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException


def success(data: Any, meta: dict | None = None) -> dict:
    envelope: dict[str, Any] = {
        "success": True,
        "data": data,
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat(), **(meta or {})},
    }
    return envelope


class ApiError(HTTPException):
    """Raise from a service/route to produce the documented error envelope."""

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(
            status_code=status_code,
            detail={"success": False, "error": {"code": code, "message": message}},
        )
