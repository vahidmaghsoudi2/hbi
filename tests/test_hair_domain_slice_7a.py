"""Slice 7-A synthetic unit tests for the HBI hair domain.

These tests cover only pure domain contracts:
- first-release service-scope guard;
- exact, versioned catalog identity lookup;
- output lineage and dependency-based invalidation;
- controlled presentation and factual event construction.

All inputs are synthetic. No API, database, live catalog, chemical rule,
personal suitability, or service-execution behavior is tested or authorized.
"""
import unittest

from app.domain.hair_service_scope import evaluate_hair_service_scope
from app.domain.hair_catalog_identity_lookup import (
    CatalogIdentity,
    CatalogReference,
    DependencyChange,
    lookup_catalog_identity,
    build_catalog_decision_output,
    assess_output_invalidation,
    decide_catalog_output_presentation,
    build_catalog_occurred_event,
)

URL = "https://raeaka.com/product/رنگ-موی-بیجورکا-سِری-طبیعی-شماره-1-مشکی/"
ALBUM_URL = "https://raeaka.com/آلبوم-رنگ-مو-بیجورکا/"
CAPTURE = "2026-11-09T14:00:00+03:30"
SHA = "a" * 64


def identity(**changes):
    values = dict(
        brand="Bijourka",
        series="طبیعی",
        shade_number="1",
        shade_name="مشکی",
        size_value="100",
        size_unit="ml",
    )
    values.update(changes)
    return CatalogIdentity(**values)


def reference(**changes):
    values = dict(
        source_kind="RAEAKA_BIJOURKA_CATALOG",
        approval_status="PO_APPROVED",
        url=URL,
        edition_label="synthetic-test-edition-1",
        captured_at=CAPTURE,
        content_sha256=SHA,
    )
    values.update(changes)
    return CatalogReference(**values)


def lookup(expected=None, observed=None, ref=None, service="CATALOG_READY"):
    return lookup_catalog_identity(
        service_kind=service,
        expected=expected or identity(),
        observed=observed or identity(),
        reference=ref or reference(),
    )


def output_for(
    result=None,
    ref=None,
    expected=None,
    observed=None,
    output_id="test-output-1",
):
    ref = ref or reference()
    expected = expected or identity()
    observed = observed or identity()
    result = result or lookup(expected, observed, ref)
    return build_catalog_decision_output(
        service_kind="CATALOG_READY",
        result=result,
        reference_id="synthetic-reference-1",
        reference=ref,
        expected=expected,
        observed=observed,
        provenance=("synthetic-fixture",),
        evidence_reference_pointers=("synthetic://evidence/1",),
        decision_output_id=output_id,
    )


class TestHairServiceScope(unittest.TestCase):
    def test_exact_catalog_ready_allowed(self):
        decision = evaluate_hair_service_scope("CATALOG_READY")
        self.assertTrue(decision.allowed)
        self.assertIsNone(decision.stop_class)

    def test_combination_consult_rejected(self):
        decision = evaluate_hair_service_scope("COMBINATION_CONSULT")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.stop_class, "OUT_OF_DOMAIN")

    def test_missing_service_is_data_gap(self):
        self.assertEqual(
            evaluate_hair_service_scope(None).stop_class,
            "DATA_GAP",
        )

    def test_blank_service_is_data_gap(self):
        self.assertEqual(
            evaluate_hair_service_scope("  ").stop_class,
            "DATA_GAP",
        )

    def test_case_variant_rejected(self):
        self.assertEqual(
            evaluate_hair_service_scope("catalog_ready").stop_class,
            "OUT_OF_DOMAIN",
        )

    def test_whitespace_variant_rejected(self):
        self.assertEqual(
            evaluate_hair_service_scope(" CATALOG_READY").stop_class,
            "OUT_OF_DOMAIN",
        )

    def test_non_string_rejected(self):
        self.assertEqual(
            evaluate_hair_service_scope(123).stop_class,
            "OUT_OF_DOMAIN",
        )


class TestCatalogLookup(unittest.TestCase):
    def test_exact_versioned_identity_matches(self):
        result = lookup()
        self.assertEqual(result.outcome, "MATCH")
        self.assertTrue(result.traceability_complete)
        self.assertEqual(len(result.matched_fields), 6)

    def test_versioned_field_conflict_is_mismatch(self):
        result = lookup(observed=identity(shade_name="قهوه‌ای"))
        self.assertEqual(result.outcome, "MISMATCH")
        self.assertIn("shade_name", result.mismatched_fields)

    def test_unknown_edition_is_inconclusive(self):
        result = lookup(ref=reference(edition_label="نامشخص"))
        self.assertEqual(result.outcome, "INCONCLUSIVE")
        self.assertEqual(result.stop_class, "KNOWLEDGE_GAP")

    def test_unversioned_conflict_is_not_definitive_mismatch(self):
        result = lookup(
            observed=identity(shade_number="2"),
            ref=reference(edition_label=None),
        )
        self.assertEqual(result.outcome, "INCONCLUSIVE")
        self.assertIn("shade_number", result.mismatched_fields)

    def test_missing_required_field_stops(self):
        result = lookup(expected=identity(size_value=" "))
        self.assertEqual(result.outcome, "STOP")
        self.assertEqual(result.stop_class, "DATA_GAP")
        self.assertIn("expected.size_value", result.missing_fields)

    def test_wrong_service_stops_out_of_domain(self):
        result = lookup(service="COMBINATION_CONSULT")
        self.assertEqual(result.outcome, "STOP")
        self.assertEqual(result.stop_class, "OUT_OF_DOMAIN")

    def test_unapproved_url_stops(self):
        result = lookup(ref=reference(url="https://example.com/catalog"))
        self.assertEqual(result.outcome, "STOP")
        self.assertEqual(result.stop_class, "KNOWLEDGE_GAP")

    def test_unapproved_host_stops(self):
        result = lookup(
            ref=reference(url="https://raeaka.com.evil.example/catalog")
        )
        self.assertEqual(result.outcome, "STOP")

    def test_query_string_url_stops(self):
        result = lookup(ref=reference(url=URL + "?x=1"))
        self.assertEqual(result.outcome, "STOP")

    def test_timezone_missing_capture_is_inconclusive(self):
        result = lookup(
            ref=reference(captured_at="2026-11-09T14:00:00")
        )
        self.assertEqual(result.outcome, "INCONCLUSIVE")
        self.assertFalse(result.traceability_complete)

    def test_malformed_hash_is_inconclusive(self):
        result = lookup(ref=reference(content_sha256="not-a-hash"))
        self.assertEqual(result.outcome, "INCONCLUSIVE")

    def test_album_reference_is_accepted(self):
        result = lookup(ref=reference(url=ALBUM_URL))
        self.assertEqual(result.outcome, "MATCH")


class TestOutputAndInvalidation(unittest.TestCase):
    def test_output_preserves_lineage_and_no_inherited_approval(self):
        output = output_for()
        self.assertEqual(output.inherited_approval_state, "NONE")
        self.assertEqual(output.version_label, "synthetic-test-edition-1")
        self.assertEqual(output.outcome, "MATCH")

    def test_unversioned_inconclusive_output_can_be_built_but_withheld(self):
        ref = reference(edition_label="unknown")
        result = lookup(ref=ref)

        self.assertEqual(result.outcome, "INCONCLUSIVE")

        output = output_for(result=result, ref=ref)
        self.assertEqual(output.outcome, "INCONCLUSIVE")

        decision = decide_catalog_output_presentation(output)
        self.assertFalse(decision.display_allowed)
        self.assertEqual(decision.status, "WITHHOLD_INCONCLUSIVE")

    def test_effective_dependency_invalidates(self):
        output = output_for()
        decision = assess_output_invalidation(
            output,
            (DependencyChange("catalog_item.shade_name", "EFFECTIVE"),),
        )
        self.assertEqual(decision, "INVALIDATE")

    def test_non_effective_change_preserves(self):
        output = output_for()
        decision = assess_output_invalidation(
            output,
            (DependencyChange("catalog_item.shade_name", "NON_EFFECTIVE"),),
        )
        self.assertEqual(decision, "PRESERVE")

    def test_unknown_dependency_impact_unresolved(self):
        output = output_for()
        decision = assess_output_invalidation(
            output,
            (DependencyChange("catalog_item.shade_name", "UNKNOWN"),),
        )
        self.assertEqual(decision, "UNRESOLVED")

    def test_unrelated_dependency_does_not_invalidate(self):
        output = output_for()
        decision = assess_output_invalidation(
            output,
            (DependencyChange("unrelated.note", "EFFECTIVE"),),
        )
        self.assertEqual(decision, "PRESERVE")


class TestDisplayAndEvents(unittest.TestCase):
    def test_versioned_match_is_displayable_as_identity_only(self):
        decision = decide_catalog_output_presentation(output_for())
        self.assertTrue(decision.display_allowed)
        self.assertEqual(decision.status, "IDENTITY_MATCH_DISPLAYABLE")
        self.assertIn("ایمنی", decision.public_message_fa)

    def test_inconclusive_output_is_withheld(self):
        ref = reference(edition_label=None)
        output = output_for(ref=ref, result=lookup(ref=ref))
        decision = decide_catalog_output_presentation(output)
        self.assertFalse(decision.display_allowed)
        self.assertEqual(decision.status, "WITHHOLD_INCONCLUSIVE")

    def test_mismatch_message_prohibits_service_execution_use(self):
        observed = identity(shade_number="2")
        result = lookup(observed=observed)
        output = output_for(result=result, observed=observed)
        decision = decide_catalog_output_presentation(output)
        self.assertTrue(decision.display_allowed)
        self.assertIn("اجرا", decision.public_message_fa)

    def test_output_presented_requires_same_displayable_output(self):
        output = output_for()
        event = build_catalog_occurred_event(
            event_kind="OUTPUT_PRESENTED",
            occurred_at=CAPTURE,
            actor_kind="SYSTEM",
            decision_output_id=output.decision_output_id,
            evidence_reference_pointer="synthetic://presentation/1",
            display_output=output,
        )
        self.assertEqual(event.event_kind, "OUTPUT_PRESENTED")

    def test_output_presented_rejects_different_output_id(self):
        output = output_for()
        with self.assertRaises(ValueError):
            build_catalog_occurred_event(
                event_kind="OUTPUT_PRESENTED",
                occurred_at=CAPTURE,
                actor_kind="SYSTEM",
                decision_output_id="different-output",
                evidence_reference_pointer="synthetic://presentation/1",
                display_output=output,
            )

    def test_event_requires_timezone_aware_time(self):
        with self.assertRaises(ValueError):
            build_catalog_occurred_event(
                event_kind="CLIENT_QUESTION_RECORDED",
                occurred_at="2026-11-09T14:00:00",
                actor_kind="CLIENT",
                decision_output_id="test-output",
                evidence_reference_pointer="synthetic://event/1",
            )

    def test_event_requires_evidence_pointer(self):
        with self.assertRaises(ValueError):
            build_catalog_occurred_event(
                event_kind="CLIENT_ACCEPTANCE_RECORDED",
                occurred_at=CAPTURE,
                actor_kind="CLIENT",
                decision_output_id="test-output",
                evidence_reference_pointer=" ",
            )

    def test_event_actor_must_match_event_kind(self):
        with self.assertRaises(ValueError):
            build_catalog_occurred_event(
                event_kind="CLIENT_ACCEPTANCE_RECORDED",
                occurred_at=CAPTURE,
                actor_kind="SYSTEM",
                decision_output_id="test-output",
                evidence_reference_pointer="synthetic://event/1",
            )

    def test_acceptance_and_execution_consent_are_distinct_events(self):
        accepted = build_catalog_occurred_event(
            event_kind="CLIENT_ACCEPTANCE_RECORDED",
            occurred_at=CAPTURE,
            actor_kind="CLIENT",
            decision_output_id="test-output",
            evidence_reference_pointer="synthetic://acceptance/1",
        )
        consent = build_catalog_occurred_event(
            event_kind="EXECUTION_CONSENT_RECORDED",
            occurred_at=CAPTURE,
            actor_kind="CLIENT",
            decision_output_id="test-output",
            evidence_reference_pointer="synthetic://consent/1",
        )
        self.assertNotEqual(accepted.event_kind, consent.event_kind)


if __name__ == "__main__":
    unittest.main(verbosity=2)
