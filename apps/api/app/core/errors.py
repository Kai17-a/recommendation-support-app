from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """API設計で定めるエラー応答を生成するための例外。"""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = dict(details or {})


async def api_error_handler(_: Request, error: Exception) -> JSONResponse:
    assert isinstance(error, ApiError)
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
                "request_id": str(uuid4()),
            }
        },
    )
