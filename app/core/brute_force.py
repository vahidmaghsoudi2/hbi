"""In-memory failed-attempt / lockout tracker (stdlib only).

Protects pilot-token (and future login) against credential/customer_id probing.
Single-instance interim control — Redis can replace the store later without
changing the call sites.
"""
from __future__ import annotations

import threading
import time
from typing import Dict, Optional, Tuple

# max failed attempts within window → lockout_seconds
MAX_FAILURES = 5
WINDOW_SECONDS = 300  # 5 minutes
LOCKOUT_SECONDS = 900  # 15 minutes

_lock = threading.Lock()
# key -> (failure_timestamps, lockout_until_monotonic)
_store: Dict[str, Tuple[list, float]] = {}


def _now() -> float:
    return time.monotonic()


def is_locked(key: str) -> Optional[int]:
    """Return remaining lockout seconds, or None if not locked."""
    with _lock:
        entry = _store.get(key)
        if not entry:
            return None
        _failures, lockout_until = entry
        remaining = int(lockout_until - _now())
        if remaining > 0:
            return remaining
        return None


def record_failure(key: str) -> Optional[int]:
    """Record a failed attempt. Returns remaining lockout seconds if now locked."""
    with _lock:
        now = _now()
        failures, lockout_until = _store.get(key, ([], 0.0))
        if lockout_until > now:
            return int(lockout_until - now)

        # drop old failures outside window
        failures = [t for t in failures if t > now - WINDOW_SECONDS]
        failures.append(now)

        if len(failures) >= MAX_FAILURES:
            lockout_until = now + LOCKOUT_SECONDS
            _store[key] = (failures, lockout_until)
            return LOCKOUT_SECONDS

        _store[key] = (failures, 0.0)
        return None


def clear_failures(key: str) -> None:
    with _lock:
        _store.pop(key, None)


def make_key(client_ip: str, customer_id: str) -> str:
    return f"{client_ip}|{customer_id}"
