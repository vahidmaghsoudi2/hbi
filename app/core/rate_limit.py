"""In-memory rate limiting for single-instance Pilot/Production hardening.

No Redis required at current stage. Thread-safe enough for uvicorn single worker
or multi-worker with process-local counters (acceptable interim control).
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# path prefix -> (max_requests, window_seconds)
_LIMITS: Dict[str, Tuple[int, int]] = {
    "/api/v1/auth/pilot-token": (20, 60),
    "/api/v1/auth/login": (10, 60),
    "/api/v1/auth/refresh": (30, 60),
    "/api/v1/recommendations/generate": (60, 60),
}

_lock = threading.Lock()
_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


def _match_limit(path: str):
    for prefix, limit in _LIMITS.items():
        if path == prefix or path.rstrip("/") == prefix.rstrip("/"):
            return limit
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        limit = _match_limit(path)
        if limit is None:
            return await call_next(request)

        max_req, window = limit
        key = f"{_client_key(request)}:{path}"
        now = time.monotonic()

        with _lock:
            q = _buckets[key]
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= max_req:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": f"Too many requests. Limit {max_req}/{window}s.",
                        }
                    },
                    headers={"Retry-After": str(window)},
                )
            q.append(now)

        return await call_next(request)
