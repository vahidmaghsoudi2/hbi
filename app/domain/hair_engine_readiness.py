"""Shared, typed readiness vocabulary for Hair advice gates.

Readiness is a server-owned operational signal. Client request data and
synthetic fixtures must never be treated as proof that a production engine
is healthy.
"""
from enum import Enum


class EngineReadiness(str, Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"


__all__ = ["EngineReadiness"]
