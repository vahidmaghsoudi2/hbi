"""Synthetic-only bridge between approved Hair catalog knowledge and the reasoning engine.

This is the Row 68 vertical slice. It is deliberately limited to CATALOG_READY
catalog identity. It does not connect real customer records, persist outputs,
activate formulation/safety rules, recommend chemical actions, or predict
hair-color outcomes. The existing reasoning engine remains COMPUTED_ONLY.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence
import re

from app.domain.hair_catalog_identity_lookup import CatalogIdentity
from app.domain.hair_data_governance import is_permitted_synthetic_case
from app.domain.hair_catalog_provider import (
    approved_catalog_contains_identity,
    load_approved_hair_catalog_reference,
)
from app.reasoning.reasoning_engine import ENGINE_VERSION, ReasoningEngine


ClaimStatus = Literal["DRAFT", "REVIEWED", "PO_APPROVED", "REJECTED", "REVOKED"]
RuleStatus = Literal["DRAFT", "REVIEWED", "APPROVED", "ACTIVE", "RETIRED"]
RuleScope = Literal["CATALOG_IDENTITY"]
DependencyImpact = Literal["EFFECTIVE", "NON_EFFECTIVE", "UNKNOWN"]
ReuseStatus = Literal["PRESERVE", "INVALIDATE", "UNRESOLVED"]

_REQUIRED_IDENTITY_FIELDS = ("brand", "series", "shade_number", "shade_name")
_ALLOWED_RULE_SCOPE = "CATALOG_IDENTITY"
_ALLOWED_RULE_LOGIC = "EXACT_CATALOG_IDENTITY_FIELDS"
_ALLOWED_RULE_RELEASE = "PO-66-10"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class HairKnowledgeClaim:
    """A traceable catalog-identity claim; never a chemistry or safety claim."""

    claim_id: str
    scope: str
    status: ClaimStatus
    claim_type: str
    source_url: str
    source_sha256: str


@dataclass(frozen=True)
class HairKnowledgePackage:
    """Immutable HBI package envelope bound to one validated catalog snapshot."""

    package_id: str
    version: str
    status: str
    snapshot_id: str
    ingestion_id: str
    source_url: str
    content_sha256: str
    claims: tuple[HairKnowledgeClaim, ...]


@dataclass(frozen=True)
class HairRuleDefinition:
    """A narrow registry entry; only the already-approved catalog identity rule is executable."""

    rule_id: str
    version: str
    scope: str
    status: RuleStatus
    logic_key: str
    claim_ids: tuple[str, ...]
    release_reference: str


@dataclass(frozen=True)
class HairCaseSnapshot:
    """A synthetic, versioned case projection containing catalog identity only."""

    case_id: str
    case_version: str
    goal_version: str
    service_kind: str
    catalog_identity: CatalogIdentity
    synthetic_data: bool


@dataclass(frozen=True)
class HairDependency:
    kind: str
    dependency_id: str
    version: str

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.dependency_id}"


@dataclass(frozen=True)
class HairDecisionRun:
    """Computed-only run envelope with immutable source and dependency lineage."""

    run_id: str
    status: str
    reason_code: str
    case_id: str
    case_version: str
    goal_version: str
    package_id: str | None
    package_version: str | None
    rule_id: str | None
    rule_version: str | None
    snapshot_id: str | None
    content_sha256: str | None
    engine_version: str
    dependencies: tuple[HairDependency, ...]
    reasoning_result: Mapping[str, Any] | None
    persistence: Literal["COMPUTED_ONLY"] = "COMPUTED_ONLY"
    display_allowed: bool = False
    recommendation: None = None
    inherited_acceptance: bool = False
    inherited_execution_consent: bool = False
    inherited_specialist_review: bool = False


@dataclass(frozen=True)
class DependencyReuseDecision:
    status: ReuseStatus
    reason_code: str
    changed_dependencies: tuple[str, ...]
    unresolved_dependencies: tuple[str, ...]
    approval_state_carried: bool = False
    execution_consent_carried: bool = False
    specialist_review_carried: bool = False


def build_approved_catalog_knowledge_package() -> HairKnowledgePackage | None:
    """Build the package envelope from the validated HBI 88-row catalog snapshot.

    The package version is HBI-owned (snapshot ID + content hash). It does not
    invent or infer a publisher edition/revision and does not add chemistry.
    """
    loaded = load_approved_hair_catalog_reference()
    if loaded is None:
        return None
    reference_id, reference = loaded
    if (
        not reference.snapshot_id
        or not reference.ingestion_id
        or not reference.content_sha256
        or not _SHA256_RE.fullmatch(reference.content_sha256)
    ):
        return None

    claim = HairKnowledgeClaim(
        claim_id=f"catalog-identity:{reference.snapshot_id}",
        scope=_ALLOWED_RULE_SCOPE,
        status="PO_APPROVED",
        claim_type="EVIDENCE",
        source_url=reference.url,
        source_sha256=reference.content_sha256,
    )
    return HairKnowledgePackage(
        package_id=f"hair-catalog:{reference_id}",
        version=f"{reference.snapshot_id}:{reference.content_sha256[:12]}",
        status="PO_APPROVED",
        snapshot_id=reference.snapshot_id,
        ingestion_id=reference.ingestion_id,
        source_url=reference.url,
        content_sha256=reference.content_sha256,
        claims=(claim,),
    )


def build_catalog_identity_rule(
    package: HairKnowledgePackage,
) -> HairRuleDefinition:
    """Represent the existing PO-approved exact catalog-identity contract."""
    return HairRuleDefinition(
        rule_id="HAIR-CATALOG-IDENTITY-EXACT",
        version="1",
        scope=_ALLOWED_RULE_SCOPE,
        status="ACTIVE",
        logic_key=_ALLOWED_RULE_LOGIC,
        claim_ids=tuple(claim.claim_id for claim in package.claims),
        release_reference=_ALLOWED_RULE_RELEASE,
    )


def _validate_package(package: HairKnowledgePackage) -> tuple[bool, str]:
    loaded = load_approved_hair_catalog_reference()
    if loaded is None:
        return False, "APPROVED_CATALOG_SNAPSHOT_UNAVAILABLE"
    reference_id, reference = loaded
    if package.status != "PO_APPROVED" or not package.version.strip():
        return False, "KNOWLEDGE_PACKAGE_NOT_APPROVED_OR_VERSIONED"
    if (
        package.snapshot_id != reference.snapshot_id
        or package.ingestion_id != reference.ingestion_id
        or package.source_url != reference.url
        or package.content_sha256 != reference.content_sha256
        or package.package_id != f"hair-catalog:{reference_id}"
    ):
        return False, "KNOWLEDGE_PACKAGE_SNAPSHOT_MISMATCH"
    if not package.claims:
        return False, "KNOWLEDGE_PACKAGE_HAS_NO_CLAIMS"
    for claim in package.claims:
        if (
            claim.status != "PO_APPROVED"
            or claim.scope != _ALLOWED_RULE_SCOPE
            or claim.claim_type != "EVIDENCE"
            or claim.source_url != package.source_url
            or claim.source_sha256 != package.content_sha256
            or not claim.claim_id.strip()
        ):
            return False, "KNOWLEDGE_CLAIM_NOT_APPROVED_OR_TRACEABLE"
    return True, "KNOWLEDGE_PACKAGE_VALIDATED"


def _validate_rule(
    rule: HairRuleDefinition,
    package: HairKnowledgePackage,
) -> tuple[bool, str]:
    package_claim_ids = {claim.claim_id for claim in package.claims}
    if (
        rule.status != "ACTIVE"
        or rule.scope != _ALLOWED_RULE_SCOPE
        or rule.logic_key != _ALLOWED_RULE_LOGIC
        or rule.release_reference != _ALLOWED_RULE_RELEASE
        or not rule.version.strip()
        or not rule.rule_id.strip()
        or not rule.claim_ids
        or not set(rule.claim_ids).issubset(package_claim_ids)
    ):
        return False, "RULE_NOT_ACTIVE_WITHIN_APPROVED_CATALOG_SCOPE"
    return True, "CATALOG_IDENTITY_RULE_VALIDATED"


def _dependencies(
    case: HairCaseSnapshot,
    package: HairKnowledgePackage,
    rule: HairRuleDefinition,
) -> tuple[HairDependency, ...]:
    return (
        HairDependency("CASE", case.case_id, case.case_version),
        HairDependency("GOAL", case.case_id, case.goal_version),
        HairDependency("KNOWLEDGE_PACKAGE", package.package_id, package.version),
        HairDependency("RULE", rule.rule_id, rule.version),
        HairDependency("CATALOG_SNAPSHOT", package.snapshot_id, package.content_sha256),
    )


def _blocked_run(
    *,
    run_id: str,
    case: HairCaseSnapshot,
    reason_code: str,
    status: str,
    package: HairKnowledgePackage | None = None,
    rule: HairRuleDefinition | None = None,
) -> HairDecisionRun:
    return HairDecisionRun(
        run_id=run_id,
        status=status,
        reason_code=reason_code,
        case_id=case.case_id,
        case_version=case.case_version,
        goal_version=case.goal_version,
        package_id=package.package_id if package else None,
        package_version=package.version if package else None,
        rule_id=rule.rule_id if rule else None,
        rule_version=rule.version if rule else None,
        snapshot_id=package.snapshot_id if package else None,
        content_sha256=package.content_sha256 if package else None,
        engine_version=ENGINE_VERSION,
        dependencies=(
            _dependencies(case, package, rule)
            if package is not None and rule is not None
            else ()
        ),
        reasoning_result=None,
    )


class HairKnowledgeCaseBridge:
    """Connect one synthetic HAIR case to approved catalog knowledge and ReasoningEngine."""

    def __init__(self, reasoning_engine: ReasoningEngine | None = None):
        self.reasoning_engine = reasoning_engine or ReasoningEngine()

    def run(
        self,
        *,
        case: HairCaseSnapshot,
        package: HairKnowledgePackage,
        rule: HairRuleDefinition,
        run_id: str,
    ) -> HairDecisionRun:
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("run_id must be a non-empty stable identifier")
        if not isinstance(case, HairCaseSnapshot):
            raise TypeError("case must be a HairCaseSnapshot")
        if not isinstance(package, HairKnowledgePackage):
            raise TypeError("package must be a HairKnowledgePackage")
        if not isinstance(rule, HairRuleDefinition):
            raise TypeError("rule must be a HairRuleDefinition")

        if case.service_kind != "CATALOG_READY":
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_OUT_OF_DOMAIN",
                reason_code="SERVICE_KIND_OUTSIDE_ROW_68_CATALOG_SCOPE",
                package=package, rule=rule,
            )
        if not is_permitted_synthetic_case(case_id=case.case_id, synthetic_data=case.synthetic_data):
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_DATA_POLICY",
                reason_code="REAL_CLIENT_DATA_BLOCKED_BY_PO_66_09",
                package=package, rule=rule,
            )
        if not case.case_version.strip() or not case.goal_version.strip():
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_DATA_GAP",
                reason_code="CASE_OR_GOAL_VERSION_MISSING",
                package=package, rule=rule,
            )

        package_ok, package_reason = _validate_package(package)
        if not package_ok:
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_KNOWLEDGE_GAP",
                reason_code=package_reason, package=package, rule=rule,
            )
        rule_ok, rule_reason = _validate_rule(rule, package)
        if not rule_ok:
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_KNOWLEDGE_GAP",
                reason_code=rule_reason, package=package, rule=rule,
            )

        identity = case.catalog_identity
        if not isinstance(identity, CatalogIdentity):
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_DATA_GAP",
                reason_code="CASE_CATALOG_IDENTITY_INVALID",
                package=package, rule=rule,
            )
        missing = tuple(
            field for field in _REQUIRED_IDENTITY_FIELDS
            if not isinstance(getattr(identity, field), str)
            or not getattr(identity, field).strip()
        )
        if missing:
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_DATA_GAP",
                reason_code="CASE_CATALOG_IDENTITY_INCOMPLETE:" + ",".join(missing),
                package=package, rule=rule,
            )
        if not approved_catalog_contains_identity(
            identity, expected_content_sha256=package.content_sha256
        ):
            return _blocked_run(
                run_id=run_id, case=case, status="STOP_KNOWLEDGE_GAP",
                reason_code="CASE_IDENTITY_NOT_IN_PO_APPROVED_CATALOG_SNAPSHOT",
                package=package, rule=rule,
            )

        evidence_list: list[dict[str, Any]] = []
        for claim in package.claims:
            evidence_list.append({
                "evidence_id": claim.claim_id,
                "claim_id": claim.claim_id,
                "field": claim.scope,
                "claim": "PO-approved catalog identity metadata only",
                "claim_type": claim.claim_type,
                "target_type": claim.claim_type,
                "source_reference": claim.source_url,
                "source_type": "APPROVED_HBI_KNOWLEDGE_PACKAGE",
                "qa_status": claim.status,
            })
        for field in _REQUIRED_IDENTITY_FIELDS:
            value = getattr(identity, field)
            evidence_list.append({
                "evidence_id": f"{case.case_id}:{field}:{case.case_version}",
                "field": field,
                "claim": value,
                "claim_type": "FACT",
                "target_type": "FACT",
                "source_reference": f"synthetic://{case.case_id}/{field}",
                "source_type": "SYNTHETIC_CASE_SNAPSHOT",
                "qa_status": "SYNTHETIC_ONLY",
            })

        knowledge_snapshot = {
            "domain": "HAIR",
            "service_kind": "CATALOG_READY",
            "package_id": package.package_id,
            "package_version": package.version,
            "package_status": package.status,
            "snapshot_id": package.snapshot_id,
            "ingestion_id": package.ingestion_id,
            "content_sha256": package.content_sha256,
            "claim_ids": [claim.claim_id for claim in package.claims],
            "rule_id": rule.rule_id,
            "rule_version": rule.version,
            "rule_scope": rule.scope,
        }
        raw_result = self.reasoning_engine.run(
            product_id=f"HAIR_CASE::{case.case_id}",
            product_knowledge_snapshot=knowledge_snapshot,
            evidence_list=evidence_list,
        )
        reasoning_result = dict(raw_result)
        reasoning_result.pop("product_id", None)
        reasoning_result["case_id"] = case.case_id
        reasoning_result["domain"] = "HAIR"
        reasoning_result["context_type"] = "SYNTHETIC_CASE"
        reasoning_result["recommendations"] = []
        reasoning_result["display_allowed"] = False

        return HairDecisionRun(
            run_id=run_id,
            status="CONTEXT_READY_FOR_CATALOG_IDENTITY_REASONING",
            reason_code="SYNTHETIC_CASE_BOUND_TO_APPROVED_CATALOG_KNOWLEDGE",
            case_id=case.case_id,
            case_version=case.case_version,
            goal_version=case.goal_version,
            package_id=package.package_id,
            package_version=package.version,
            rule_id=rule.rule_id,
            rule_version=rule.version,
            snapshot_id=package.snapshot_id,
            content_sha256=package.content_sha256,
            engine_version=ENGINE_VERSION,
            dependencies=_dependencies(case, package, rule),
            reasoning_result=reasoning_result,
        )


def assess_dependency_reuse(
    *,
    previous_run: HairDecisionRun,
    current_dependencies: Sequence[HairDependency],
    impact_by_key: Mapping[str, DependencyImpact] | None = None,
) -> DependencyReuseDecision:
    """Apply C10 dependency invalidation; never transfer approvals or consent."""
    previous = {dependency.key: dependency.version for dependency in previous_run.dependencies}
    current = {dependency.key: dependency.version for dependency in current_dependencies}
    all_keys = sorted(set(previous) | set(current))
    changed = tuple(
        key for key in all_keys if previous.get(key) != current.get(key)
    )
    if not changed:
        return DependencyReuseDecision(
            status="PRESERVE",
            reason_code="NO_DEPENDENCY_VERSION_CHANGED",
            changed_dependencies=(),
            unresolved_dependencies=(),
        )

    impacts = impact_by_key or {}
    unresolved: list[str] = []
    effective: list[str] = []
    for key in changed:
        kind = key.split(":", 1)[0]
        if kind == "GOAL":
            effective.append(key)
            continue
        impact = impacts.get(key, "UNKNOWN")
        if impact == "EFFECTIVE":
            effective.append(key)
        elif impact == "UNKNOWN":
            unresolved.append(key)

    if effective:
        return DependencyReuseDecision(
            status="INVALIDATE",
            reason_code="EFFECTIVE_DEPENDENCY_CHANGE_REQUIRES_FRESH_RUN",
            changed_dependencies=changed,
            unresolved_dependencies=tuple(unresolved),
        )
    if unresolved:
        return DependencyReuseDecision(
            status="UNRESOLVED",
            reason_code="DEPENDENCY_IMPACT_NOT_ESTABLISHED_FAIL_CLOSED",
            changed_dependencies=changed,
            unresolved_dependencies=tuple(unresolved),
        )
    return DependencyReuseDecision(
        status="PRESERVE",
        reason_code="ALL_CHANGED_DEPENDENCIES_ASSESSED_NON_EFFECTIVE",
        changed_dependencies=changed,
        unresolved_dependencies=(),
    )


__all__ = [
    "HairKnowledgeClaim",
    "HairKnowledgePackage",
    "HairRuleDefinition",
    "HairCaseSnapshot",
    "HairDependency",
    "HairDecisionRun",
    "DependencyReuseDecision",
    "HairKnowledgeCaseBridge",
    "build_approved_catalog_knowledge_package",
    "build_catalog_identity_rule",
    "assess_dependency_reuse",
]
