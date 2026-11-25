"""Read-only retrieval of current ProductProblemLink candidates for human review.

This service is intentionally separate from RecommendationService. A CANDIDATE
link is a review queue item, never a suitability decision or recommendation.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.repositories.product_problem_link_repository import ProductProblemLinkRepository


class ProductProblemCandidateRetrievalService:
    PROBLEM_MAP_VERSION = "SKIN_PROBLEM_SPACE_MAP_V0.1"

    def __init__(self, db: Session):
        self.repository = ProductProblemLinkRepository(db)

    @staticmethod
    def _normalize_problem_id(problem_id: str) -> str:
        value = (problem_id or "").strip().upper()
        match = re.fullmatch(r"P(\d{2})", value)
        if not match or not 1 <= int(match.group(1)) <= 61:
            raise ValidationError("problem_id must reference an existing P01-P61 identifier.")
        if value == "P22":
            raise ValidationError(
                "P22 is Context/reference only and cannot be retrieved as an independent product candidate."
            )
        return value

    @staticmethod
    def _known_scope(value: Optional[str]) -> Optional[str]:
        normalized = (value or "").strip().upper()
        return normalized if normalized and normalized != "UNKNOWN" else None

    def retrieve(
        self,
        problem_id: str,
        *,
        market_region: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> Dict[str, Any]:
        problem_id = self._normalize_problem_id(problem_id)
        market_filter = self._known_scope(market_region)
        variant_filter = self._known_scope(variant)
        if variant_filter and variant_filter not in {"COLOR", "NON_COLOR"}:
            raise ValidationError("variant filter must be COLOR or NON_COLOR.")

        rows = self.repository.list_latest_candidate_rows(problem_id)
        candidates: List[Dict[str, Any]] = []
        excluded_integrity_count = 0

        for link, product, evidence in rows:
            if market_filter and (link.market_region or "").strip().upper() != market_filter:
                continue
            if variant_filter and (link.variant or "").strip().upper() != variant_filter:
                continue

            # Defend the read path against legacy/manual rows that bypassed service validation.
            if evidence.product_id != link.product_id or not evidence.claim_id or evidence.claim_id != link.claim_id:
                excluded_integrity_count += 1
                continue
            link_market = self._known_scope(link.market_region)
            product_market = self._known_scope(product.market_region)
            evidence_market = self._known_scope(evidence.market_region)
            if (
                (product_market and link_market and product_market != link_market)
                or (evidence_market and link_market and evidence_market != link_market)
            ):
                excluded_integrity_count += 1
                continue

            blockers: List[str] = []
            if (product.identity_status or "").strip().upper() != "VERIFIED":
                blockers.append("PRODUCT_IDENTITY_NOT_VERIFIED")
            if (product.qa_verdict or "").strip().upper() != "VALID":
                blockers.append("PRODUCT_QA_NOT_VALID")
            if (product.status or "").strip().upper() != "ACTIVE":
                blockers.append("PRODUCT_NOT_ACTIVE")
            if (evidence.qa_status or "").strip().upper() != "VERIFIED":
                blockers.append("EVIDENCE_NOT_VERIFIED")
            if (evidence.conflict_status or "NONE").strip().upper() == "CONFLICT":
                blockers.append("EVIDENCE_CONFLICT")
            if (link.variant or "").strip().upper() == "UNKNOWN":
                blockers.append("VARIANT_UNKNOWN")

            candidates.append({
                "link_id": link.link_id,
                "product_id": product.product_id,
                "brand": product.brand,
                "product_name": product.product_name,
                "product_identity_status": product.identity_status,
                "product_qa_verdict": product.qa_verdict,
                "product_lifecycle_status": product.status,
                "evidence_id": evidence.evidence_id,
                "claim_id": evidence.claim_id,
                "evidence_claim": evidence.claim,
                "evidence_claim_type": evidence.claim_type,
                "evidence_source_type": evidence.source_type,
                "evidence_source_reference": evidence.source_reference,
                "evidence_market_region": evidence.market_region,
                "evidence_qa_status": evidence.qa_status,
                "evidence_conflict_status": evidence.conflict_status,
                "problem_id": link.problem_id,
                "problem_type": link.problem_type,
                "problem_definition_ref": link.problem_definition_ref,
                "problem_map_version": link.problem_map_version,
                "relationship_role": link.relationship_role,
                "relationship_status": link.relationship_status,
                "variant": link.variant,
                "market_region": link.market_region,
                "feature_basis": link.feature_basis,
                "outcome": link.outcome,
                "semantic_basis": link.semantic_basis,
                "limitations": link.limitations,
                "decision_basis": link.decision_basis,
                "revision_no": link.revision_no,
                "supersedes_link_id": link.supersedes_link_id,
                "review_gate": "HUMAN_REVIEW_ONLY",
                "product_gate_blockers": blockers,
                "product_gate_status": "BLOCKED" if blockers else "REVIEWABLE_NOT_APPROVED",
            })

        return {
            "problem_id": problem_id,
            "problem_map_version": self.PROBLEM_MAP_VERSION,
            "retrieval_mode": "CURRENT_CANDIDATES_ONLY",
            "review_gate": "HUMAN_REVIEW_ONLY",
            "recommendation_eligible": False,
            "candidate_count": len(candidates),
            "excluded_integrity_count": excluded_integrity_count,
            "candidates": candidates,
        }
