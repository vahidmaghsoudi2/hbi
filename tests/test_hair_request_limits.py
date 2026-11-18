import asyncio

from app.core.hair_request_limits import HairRequestSizeLimitMiddleware


def _run_middleware(path, headers, messages, max_bytes=8):
    captured = []

    async def app(scope, receive, send):
        request = await receive()
        captured.append(("app", request.get("body", b"")))
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"accepted"})

    queue = list(messages)

    async def receive():
        if queue:
            return queue.pop(0)
        return {"type": "http.disconnect"}

    async def send(message):
        captured.append(("send", message))

    scope = {
        "type": "http",
        "path": path,
        "headers": headers,
        "method": "POST",
    }
    asyncio.run(HairRequestSizeLimitMiddleware(app, max_bytes=max_bytes)(scope, receive, send))
    return captured


def _response(captured):
    return [item[1] for item in captured if item[0] == "send"]


def test_content_length_over_limit_is_rejected_without_reading_or_echoing_body():
    sentinel = b"PRIVATE-BODY-SENTINEL"
    captured = _run_middleware(
        "/api/v1/hair/dialogue/turn",
        [(b"content-length", str(len(sentinel)).encode())],
        [{"type": "http.request", "body": sentinel, "more_body": False}],
    )
    assert not any(item[0] == "app" for item in captured)
    messages = _response(captured)
    assert messages[0]["status"] == 413
    assert sentinel not in messages[1]["body"]


def test_streamed_body_over_limit_is_rejected_without_content_length():
    sentinel = b"PRIVATE-CHUNK-SENTINEL"
    captured = _run_middleware(
        "/api/v1/hair/specialist-preview",
        [],
        [
            {"type": "http.request", "body": sentinel[:10], "more_body": True},
            {"type": "http.request", "body": sentinel[10:], "more_body": False},
        ],
    )
    assert not any(item[0] == "app" for item in captured)
    messages = _response(captured)
    assert messages[0]["status"] == 413
    assert sentinel not in messages[1]["body"]


def test_body_within_limit_is_replayed_to_endpoint():
    body = b'{"ok":1}'
    captured = _run_middleware(
        "/api/v1/hair/dialogue/turn",
        [(b"content-length", str(len(body)).encode())],
        [{"type": "http.request", "body": body, "more_body": False}],
    )
    assert ("app", body) in captured
    assert _response(captured)[0]["status"] == 200


def test_non_hair_endpoint_is_not_affected_by_hair_specific_limit():
    body = b"X" * 100
    captured = _run_middleware(
        "/api/v1/products",
        [(b"content-length", str(len(body)).encode())],
        [{"type": "http.request", "body": body, "more_body": False}],
    )
    assert ("app", body) in captured
    assert _response(captured)[0]["status"] == 200
