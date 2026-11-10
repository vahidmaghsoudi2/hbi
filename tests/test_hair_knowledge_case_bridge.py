from dataclasses import replace

import pytest

from app.domain.hair_catalog_identity_lookup import CatalogIdentity
from app.domain.hair_knowledge_case_bridge import (
    HairCaseSnapshot,
    HairDependency,
    HairKnowledgeCaseBridge,
    assess_dependency_reuse,
    build_approved_catalog_knowledge_package,
    build_catalog_identity_rule,
)


def _package_and_rule():
    package = build_approved_catalog_knowledge_package()
    assert package is not None
    return package, build_catalog_identity_rule(package)


def _case(**overrides):
    values = {
        "case_id": "SYNTHETIC-CASE-001",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "service_kind": "CATALOG_READY",
        "catalog_identity": CatalogIdentity(
            brand="بیجورکا",
            series="طبیعی",
            shade_number="۱",
            shade_name="مشکی",
        ),
        "synthetic_data": True,
    }
    values.update(overrides)
    return HairCaseSnapshot(**values)


def _run(case=None, package=None, rule=None):
    if package is None or rule is None:
        package, rule = _package_and_rule()
    return HairKnowledgeCaseBridge().run(
        case=case or _case(),
        package=package,
        rule=rule,
        run_id="SYNTHETIC-RUN-001",
    )


def test_approved_package_is_bound_to_the_current_88_row_hbi_snapshot():
    package, _ = _package_and_rule()
    assert package.status == "PO_APPROVED"
    assert package.snapshot_id.startswith("hbi-hair-catalog-snapshot-")
    assert package.ingestion_id.startswith("hbi-hair-catalog-ingestion-")
    assert len(package.content_sha256) == 64
    assert package.claims
    assert all(claim.source_sha256 == package.content_sha256 for claim in package.claims)


def test_synthetic_case_runs_through_reasoning_engine_with_full_lineage():
    result = _run()
    assert result.status == "CONTEXT_READY_FOR_CATALOG_IDENTITY_REASONING"
    assert result.reason_code == "SYNTHETIC_CASE_BOUND_TO_APPROVED_CATALOG_KNOWLEDGE"
    assert result.case_id == "SYNTHETIC-CASE-001"
    assert result.package_id
    assert result.package_version
    assert result.rule_id == "HAIR-CATALOG-IDENTITY-EXACT"
    assert result.snapshot_id
    assert result.content_sha256
    assert result.dependencies
    assert result.reasoning_result["domain"] == "HAIR"
    assert result.reasoning_result["case_id"] == result.case_id
    assert result.reasoning_result["persistence"] == "COMPUTED_ONLY"
    assert result.reasoning_result["evidence_refs"]
    assert result.display_allowed is False
    assert result.recommendation is None
    assert result.persistence == "COMPUTED_ONLY"


def test_no_real_customer_case_can_enter_the_bridge():
    result = _run(_case(case_id="CASE-REAL-001", synthetic_data=False))
    assert result.status == "STOP_DATA_POLICY"
    assert result.reason_code == "REAL_CLIENT_DATA_BLOCKED_BY_PO_66_09"
    assert result.reasoning_result is None


def test_case_id_must_be_explicitly_synthetic_even_when_flag_is_true():
    result = _run(_case(case_id="CASE-001", synthetic_data=True))
    assert result.status == "STOP_DATA_POLICY"


def test_only_catalog_ready_service_is_allowed():
    result = _run(_case(service_kind="COMBINATION_CONSULT"))
    assert result.status == "STOP_OUT_OF_DOMAIN"


def test_unversioned_case_or_goal_is_stopped():
    result = _run(_case(case_version="", goal_version="goal-v1"))
    assert result.status == "STOP_DATA_GAP"
    assert result.reason_code == "CASE_OR_GOAL_VERSION_MISSING"


def test_missing_identity_field_is_data_gap_not_inferred():
    identity = CatalogIdentity(
        brand="بیجورکا", series="طبیعی", shade_number="۱", shade_name=None
    )
    result = _run(_case(catalog_identity=identity))
    assert result.status == "STOP_DATA_GAP"
    assert "shade_name" in result.reason_code


def test_identity_not_in_approved_snapshot_is_knowledge_gap():
    identity = CatalogIdentity(
        brand="بیجورکا",
        series="طبیعی",
        shade_number="NOT-IN-CATALOG",
        shade_name="نامشخص",
    )
    result = _run(_case(catalog_identity=identity))
    assert result.status == "STOP_KNOWLEDGE_GAP"
    assert result.reason_code == "CASE_IDENTITY_NOT_IN_PO_APPROVED_CATALOG_SNAPSHOT"


def test_tampered_package_hash_is_rejected():
    package, rule = _package_and_rule()
    tampered = replace(package, content_sha256="0" * 64)
    result = _run(package=tampered, rule=rule)
    assert result.status == "STOP_KNOWLEDGE_GAP"
    assert result.reason_code == "KNOWLEDGE_PACKAGE_SNAPSHOT_MISMATCH"


def test_unapproved_claim_is_rejected():
    package, rule = _package_and_rule()
    claim = replace(package.claims[0], status="DRAFT")
    tampered = replace(package, claims=(claim,))
    result = _run(package=tampered, rule=rule)
    assert result.status == "STOP_KNOWLEDGE_GAP"
    assert result.reason_code == "KNOWLEDGE_CLAIM_NOT_APPROVED_OR_TRACEABLE"


def test_claim_outside_catalog_identity_scope_is_rejected():
    package, rule = _package_and_rule()
    claim = replace(package.claims[0], scope="CHEMICAL_FORMULATION")
    tampered = replace(package, claims=(claim,))
    result = _run(package=tampered, rule=rule)
    assert result.status == "STOP_KNOWLEDGE_GAP"


def test_rule_must_be_active():
    package, rule = _package_and_rule()
    result = _run(package=package, rule=replace(rule, status="DRAFT"))
    assert result.status == "STOP_KNOWLEDGE_GAP"
    assert result.reason_code == "RULE_NOT_ACTIVE_WITHIN_APPROVED_CATALOG_SCOPE"


def test_chemical_rule_is_never_activated_by_this_bridge():
    package, rule = _package_and_rule()
    chemical_rule = replace(
        rule,
        scope="CHEMICAL_SAFETY",
        logic_key="FORMULATION_OR_SAFETY_RULE",
    )
    result = _run(package=package, rule=chemical_rule)
    assert result.status == "STOP_KNOWLEDGE_GAP"


def test_rule_release_reference_must_match_accepted_catalog_scope():
    package, rule = _package_and_rule()
    result = _run(package=package, rule=replace(rule, release_reference="UNAPPROVED"))
    assert result.status == "STOP_KNOWLEDGE_GAP"


def test_rule_cannot_reference_claim_outside_knowledge_package():
    package, rule = _package_and_rule()
    result = _run(package=package, rule=replace(rule, claim_ids=("unknown-claim",)))
    assert result.status == "STOP_KNOWLEDGE_GAP"


def test_run_never_carries_acceptance_execution_consent_or_specialist_review():
    result = _run()
    assert result.inherited_acceptance is False
    assert result.inherited_execution_consent is False
    assert result.inherited_specialist_review is False


def test_goal_version_change_always_invalidates_previous_run():
    result = _run()
    changed = tuple(
        HairDependency(dep.kind, dep.dependency_id, "goal-v2")
        if dep.kind == "GOAL" else dep
        for dep in result.dependencies
    )
    decision = assess_dependency_reuse(
        previous_run=result, current_dependencies=changed
    )
    assert decision.status == "INVALIDATE"
    assert decision.reason_code == "EFFECTIVE_DEPENDENCY_CHANGE_REQUIRES_FRESH_RUN"
    assert decision.approval_state_carried is False
    assert decision.execution_consent_carried is False


def test_unknown_dependency_impact_fails_closed_as_unresolved():
    result = _run()
    changed = tuple(
        HairDependency(dep.kind, dep.dependency_id, "package-v2")
        if dep.kind == "KNOWLEDGE_PACKAGE" else dep
        for dep in result.dependencies
    )
    decision = assess_dependency_reuse(
        previous_run=result, current_dependencies=changed
    )
    assert decision.status == "UNRESOLVED"
    assert decision.unresolved_dependencies == ("KNOWLEDGE_PACKAGE:hair-catalog:" + result.snapshot_id,)


def test_explicitly_effective_knowledge_change_invalidates_run():
    result = _run()
    changed = tuple(
        HairDependency(dep.kind, dep.dependency_id, "package-v2")
        if dep.kind == "KNOWLEDGE_PACKAGE" else dep
        for dep in result.dependencies
    )
    key = next(dep.key for dep in result.dependencies if dep.kind == "KNOWLEDGE_PACKAGE")
    decision = assess_dependency_reuse(
        previous_run=result,
        current_dependencies=changed,
        impact_by_key={key: "EFFECTIVE"},
    )
    assert decision.status == "INVALIDATE"


def test_assessed_non_effective_change_preserves_only_computation_reuse():
    result = _run()
    changed = tuple(
        HairDependency(dep.kind, dep.dependency_id, "metadata-v2")
        if dep.kind == "KNOWLEDGE_PACKAGE" else dep
        for dep in result.dependencies
    )
    key = next(dep.key for dep in result.dependencies if dep.kind == "KNOWLEDGE_PACKAGE")
    decision = assess_dependency_reuse(
        previous_run=result,
        current_dependencies=changed,
        impact_by_key={key: "NON_EFFECTIVE"},
    )
    assert decision.status == "PRESERVE"
    assert decision.approval_state_carried is False
    assert decision.execution_consent_carried is False
    assert decision.specialist_review_carried is False


def test_identical_dependencies_preserve_computed_result_only():
    result = _run()
    decision = assess_dependency_reuse(
        previous_run=result, current_dependencies=result.dependencies
    )
    assert decision.status == "PRESERVE"
    assert decision.reason_code == "NO_DEPENDENCY_VERSION_CHANGED"


def test_engine_context_is_not_a_customer_record_or_persisted_case():
    result = _run()
    assert "customer_id" not in result.reasoning_result
    assert result.reasoning_result["persistence"] == "COMPUTED_ONLY"
    assert result.reasoning_result["display_allowed"] is False
    assert result.reasoning_result["recommendations"] == []
