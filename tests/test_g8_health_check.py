from __future__ import annotations

import urllib.request

from scripts import run_g8_isolated_pilot as runner


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _Opener:
    def __init__(self):
        self.calls = []

    def open(self, url, timeout):
        self.calls.append((url, timeout))
        return _Response()


def test_health_check_bypasses_environment_proxies(monkeypatch):
    opener = _Opener()
    handlers = []

    def fake_build_opener(*handlers_arg):
        handlers.extend(handlers_arg)
        return opener

    monkeypatch.setattr(urllib.request, "build_opener", fake_build_opener)

    ready, detail = runner._health_check()

    assert ready is True
    assert detail == "HTTP 200"
    assert len(handlers) == 1
    assert isinstance(handlers[0], urllib.request.ProxyHandler)
    assert handlers[0].proxies == {}
    assert opener.calls == [(runner.HEALTH_URL, 1)]
