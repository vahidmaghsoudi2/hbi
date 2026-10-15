"""Opt-in, secret-redacting HTTP evidence capture for the isolated G8 pilot.

Enabled only when G8_RAW_HTTP_EVIDENCE_DIR is explicitly set by the pilot runner.
Credential-bearing headers/fields are never persisted; body hashes bind the sanitized
record to the bytes observed by the ASGI boundary without exposing secret values.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

MAX_BODY_BYTES = 2 * 1024 * 1024
_SECRET_KEY = re.compile(r"(password|passwd|secret|token|authorization|cookie|api[_-]?key|credential|refresh[_-]?token|access[_-]?token)", re.I)
_SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie", "set-cookie", "x-api-key"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _safe_headers(raw_headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in raw_headers:
        name = key.decode("latin-1")
        if name.lower() in _SENSITIVE_HEADERS:
            result[name] = "[REDACTED]"
        else:
            result[name] = value.decode("latin-1")[:4096]
    return result


def _redact(value):
    if isinstance(value, dict):
        return {str(key): ("[REDACTED]" if _SECRET_KEY.search(str(key)) else _redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        # Avoid leaking inline bearer/basic credentials in otherwise innocuous text.
        return re.sub(r"(?i)\b(bearer|basic)\s+[^\s\"']+", r"\1 [REDACTED]", value)
    return value


def _body_record(body: bytes, headers: dict[str, str]) -> dict:
    content_type = next((v for k, v in headers.items() if k.lower() == "content-type"), "").lower()
    record = {
        "sha256_observed_bytes": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
        "captured": len(body) <= MAX_BODY_BYTES,
        "representation": None,
    }
    if len(body) > MAX_BODY_BYTES:
        record["representation"] = "[OMITTED: BODY EXCEEDS 2 MiB CAPTURE LIMIT]"
        return record
    if not body:
        record["representation"] = ""
    elif "json" in content_type:
        try:
            record["representation"] = _redact(json.loads(body.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            record["captured"] = False
            record["representation"] = "[OMITTED: INVALID JSON BODY]"
    elif "application/x-www-form-urlencoded" in content_type:
        try:
            pairs = parse_qsl(body.decode("utf-8"), keep_blank_values=True)
            record["representation"] = urlencode([(k, "[REDACTED]" if _SECRET_KEY.search(k) else v) for k, v in pairs])
        except UnicodeDecodeError:
            record["captured"] = False
            record["representation"] = "[OMITTED: INVALID FORM BODY]"
    elif content_type.startswith("text/") or "xml" in content_type:
        text = body.decode("utf-8", errors="replace")
        if re.search(r"(?i)(password|passwd|client_secret|access_token|refresh_token)\s*[:=]", text):
            record["captured"] = False
            record["representation"] = "[OMITTED: POSSIBLE SECRET IN TEXT BODY]"
        else:
            record["representation"] = text
    else:
        record["representation"] = "[OMITTED: NON-TEXT BODY; HASH AND SIZE RETAINED]"
    return record


class G8RawHttpEvidenceMiddleware:
    """ASGI middleware that records paired request/response evidence when opted in."""

    def __init__(self, app, output_dir: str | None = None):
        self.app = app
        self.output_dir = output_dir or os.getenv("G8_RAW_HTTP_EVIDENCE_DIR", "")
        self.enabled = bool(self.output_dir)

    async def __call__(self, scope, receive, send):
        if not self.enabled or scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        started = time.monotonic()
        request_id = uuid.uuid4().hex
        request_timestamp = _utc_now()
        request_chunks: list[bytes] = []
        response_chunks: list[bytes] = []
        response_status = None
        response_headers: dict[str, str] = {}
        response_started = False
        response_complete = False
        request_complete = False
        scope_headers = _safe_headers(scope.get("headers", []))
        scope_path = scope.get("path", "")
        method = scope.get("method", "UNKNOWN")

        async def wrapped_receive():
            nonlocal request_complete
            message = await receive()
            if message["type"] == "http.request":
                request_chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    request_complete = True
            return message

        async def wrapped_send(message):
            nonlocal response_status, response_headers, response_started, response_complete
            if message["type"] == "http.response.start":
                response_started = True
                response_status = message.get("status")
                response_headers = _safe_headers(message.get("headers", []))
            elif message["type"] == "http.response.body":
                response_chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    response_complete = True
            await send(message)

        try:
            await self.app(scope, wrapped_receive, wrapped_send)
        finally:
            request_body = b"".join(request_chunks)
            response_body = b"".join(response_chunks)
            record = {
                "schema": "hbi.g8.raw-http.v1",
                "request_id": request_id,
                "started_at_utc": request_timestamp,
                "finished_at_utc": _utc_now(),
                "duration_ms": round((time.monotonic() - started) * 1000, 3),
                "request": {
                    "method": method,
                    "path": scope_path,
                    "http_version": scope.get("http_version"),
                    "headers": scope_headers,
                    "complete": request_complete,
                    "body": _body_record(request_body, scope_headers),
                },
                "response": {
                    "status": response_status,
                    "headers": response_headers,
                    "started": response_started,
                    "complete": response_complete,
                    "body": _body_record(response_body, response_headers),
                },
            }
            try:
                output = Path(self.output_dir)
                output.mkdir(parents=True, exist_ok=True)
                target = output / f"{request_timestamp.replace(':', '').replace('-', '')}-{request_id}.json"
                temp = target.with_suffix(".tmp")
                temp.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                temp.replace(target)
            except Exception:
                # Fail closed: the runner's finalizer will reject a session with no
                # valid complete paired artifacts. Do not mask the original response.
                pass
