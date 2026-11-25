import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.routers.cases import ConsultationContextRequest
from app.services.case_service import CaseService


class FakeSession:
    def flush(self):
        return None


class FakeCaseRepository:
    def __init__(self, case):
        self.case = case

    def get_by_id(self, case_id):
        return self.case if self.case and self.case.case_id == case_id else None


def make_service(raw_evidence_gaps=None):
    case = SimpleNamespace(
        case_id="CASE_TEST",
        customer_id="CUSTOMER_TEST",
        evidence_gaps=raw_evidence_gaps,
    )
    service = CaseService(FakeSession())
    service.repository = FakeCaseRepository(case)
    return service, case


def test_consultation_context_round_trips_as_case_owned_json():
    service, case = make_service()
    context = {
        "affected_areas": ["cheek", "forehead"],
        "duration": "two weeks",
        "severity": 6,
        "aggravating_factors": ["sun exposure"],
        "current_products": ["cleanser"],
        "notes": None,
    }

    service.save_consultation_context("CASE_TEST", context)

    assert json.loads(case.evidence_gaps)["consultation_v1"] == context
    assert service.get_consultation_context("CASE_TEST") == context


def test_consultation_context_preserves_legacy_evidence_gaps_value():
    service, case = make_service("legacy gap note")
    context = {
        "affected_areas": [],
        "duration": None,
        "severity": None,
        "aggravating_factors": [],
        "current_products": [],
        "notes": None,
    }

    service.save_consultation_context("CASE_TEST", context)

    saved = json.loads(case.evidence_gaps)
    assert saved["legacy_value"] == "legacy gap note"
    assert saved["consultation_v1"] == context


def test_consultation_context_rejects_severity_outside_customer_scale():
    with pytest.raises(ValidationError):
        ConsultationContextRequest(severity=11)
