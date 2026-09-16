"""Mission B — Gallery client contract.

Proves frontend API client exposes Override and Feedback entry points
expected by RecommendationPage. Does not run a browser; verifies wiring surface.
"""
import ast
from pathlib import Path


CLIENT = Path(__file__).resolve().parents[1] / "frontend" / "src" / "api" / "client.ts"
PAGE = Path(__file__).resolve().parents[1] / "frontend" / "src" / "pages" / "RecommendationPage.tsx"


def test_client_exports_specialist_functions():
    text = CLIENT.read_text(encoding="utf-8")
    assert "export function createSpecialistOverride" in text
    assert "export function listOverridesByCase" in text
    assert "export function createFeedback" in text
    assert "export function listFeedbackByCase" in text
    assert "/specialist/overrides" in text
    assert "/specialist/feedback" in text


def test_recommendation_page_wires_override_and_feedback():
    text = PAGE.read_text(encoding="utf-8")
    assert "createSpecialistOverride" in text
    assert "createFeedback" in text
    assert "Override: Accept" in text or "onOverride" in text
    assert "Feedback" in text
    assert "FOLLOW_UP_NEEDED" in text or "Follow-up" in text
