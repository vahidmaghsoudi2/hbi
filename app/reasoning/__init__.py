"""
app.reasoning package — GATE 7-3

Exports:
- MatchScoringEngine (existing, untouched)
- ReasoningEngine (new)
- ConflictAnalyzer (new)
- ClaimValidator (new)
"""

from .scoring import MatchScoringEngine
from .reasoning_engine import ReasoningEngine
from .conflict_analyzer import ConflictAnalyzer, ConflictSeverity, ResolutionState
from .claim_validator import ClaimValidator

__all__ = [
    "MatchScoringEngine",
    "ReasoningEngine",
    "ConflictAnalyzer",
    "ConflictSeverity",
    "ResolutionState",
    "ClaimValidator",
]
