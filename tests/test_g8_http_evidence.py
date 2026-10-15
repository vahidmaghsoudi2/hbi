import asyncio
import json
from pathlib import Path

from app.g8_http_evidence import G8RawHttpEvidenceMiddleware


def test_middleware_writes_paired_redacted_request_response(tmp_path: Path):
    async def app(scope, receive, send):
        message = await receive()
        assert message["body"] == b'{"username":"pilot","password":"do-not-store"}'
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"application/json"), (b"set-cookie", b"session=secret")],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"ok":true,"access_token":"response-secret"}',
            "more_body": False,
        })

    middleware = G8RawHttpEvidenceMiddleware(app, str(tmp_path))

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"username":"pilot","password":"do-not-store"}',
            "more_body": False,
        }

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "http_version": "1.1",
        "headers": [
            (b"content-type", b"application/json"),
            (b"authorization", b"Bearer request-secret"),
        ],
    }
    asyncio.run(middleware(scope, receive, send))

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    record = json.loads(files[0].read_text(encoding="utf-8"))
    assert record["schema"] == "hbi.g8.raw-http.v1"
    assert record["request"]["complete"] is True
    assert record["response"]["complete"] is True
    assert record["response"]["status"] == 200
    serialized = json.dumps(record)
    for secret in ("do-not-store", "request-secret", "response-secret", "session=secret"):
        assert secret not in serialized
    assert record["request"]["body"]["sha256_observed_bytes"]
    assert record["response"]["body"]["sha256_observed_bytes"]
    assert sent[-1]["type"] == "http.response.body"


def test_middleware_is_opt_in_when_no_output_directory():
    calls = []

    async def app(scope, receive, send):
        calls.append("called")

    middleware = G8RawHttpEvidenceMiddleware(app, "")
    asyncio.run(middleware({"type": "http", "method": "GET", "path": "/"}, None, None))
    assert calls == ["called"]


def test_middleware_forwards_disconnect_after_request_replay(tmp_path: Path):
    received = []

    async def app(scope, receive, send):
        first = await receive()
        received.append(first)
        assert first["type"] == "http.request"
        assert first["body"] == b'{"pilot":true}'

        second = await receive()
        received.append(second)
        assert second["type"] == "http.disconnect"

        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    messages = [
        {"type": "http.request", "body": b'{"pilot":true}', "more_body": False},
        {"type": "http.disconnect"},
    ]

    async def receive():
        if messages:
            return messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message):
        pass

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/g8-regression-test",
        "http_version": "1.1",
        "headers": [(b"content-type", b"application/json")],
    }

    middleware = G8RawHttpEvidenceMiddleware(app, str(tmp_path))
    asyncio.run(middleware(scope, receive, send))

    assert [message["type"] for message in received] == [
        "http.request",
        "http.disconnect",
    ]
    assert len(list(tmp_path.glob("*.json"))) == 1
