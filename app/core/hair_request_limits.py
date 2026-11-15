"""Bounded request-body guard for synthetic Hair HTTP endpoints.

The guard buffers only the configured maximum plus one byte, handles requests
without Content-Length, and returns a constant response without reflecting input.
"""
from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

MAX_HAIR_REQUEST_BYTES = 16 * 1024
_HAIR_LIMITED_PATHS = {
    "/api/v1/hair/dialogue/turn",
    "/api/v1/hair/specialist-preview",
}


class HairRequestSizeLimitMiddleware:
    def __init__(self, app: Callable[..., Awaitable[Any]], max_bytes: int = MAX_HAIR_REQUEST_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") not in _HAIR_LIMITED_PATHS:
            await self.app(scope, receive, send)
            return

        headers = {
            key.lower(): value
            for key, value in scope.get("headers", [])
        }
        raw_length = headers.get(b"content-length")
        if raw_length is not None:
            try:
                if int(raw_length) > self.max_bytes:
                    await self._reject(send)
                    return
            except (TypeError, ValueError):
                await self._reject(send)
                return

        chunks: list[bytes] = []
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunk = message.get("body", b"")
            total += len(chunk)
            if total > self.max_bytes:
                await self._reject(send)
                return
            chunks.append(chunk)
            if not message.get("more_body", False):
                break

        body = b"".join(chunks)
        replayed = False

        async def replay_receive():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _reject(send):
        body = json.dumps(
            {"detail": "Request body exceeds the allowed size."}
        ).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        })
        await send({"type": "http.response.body", "body": body})
