import re
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_problem_link import ProductProblemLink
from app.repositories.product_problem_link_repository import ProductProblemLinkRepository


class ProductProblemLinkService:
    """Create/read-only service for the first ProductProblemLink foundation.

    This phase intentionally has no status-transition operation, no API route,
    and no Recommendation integration. SUPPORTED is not a persistable state.
    """

    ALLOWED_ROLES = frozenset({
        "presentation",
        "context",
        "clinical_anchor",
        "sequela",
    })
    ALLOWED_STATUSES = frozenset({"CANDIDATE", "NOT_LINKED", "DEFERRED"})
    ALLOWED_VARIANTS = frozenset({"COLOR", "NON_COLOR", "UNKNOWN"})
    PROBLEM_MAP_VERSION = "SKIN_PROBLEM_SPACE_MAP_V0.1"

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductProblemLinkRepository(db)

    @staticmethod
    def _required_text(value: Optional[str], field: str) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise ValidationError(f"{field} is required; use UNKNOWN when not established.")
        return normalized

    @staticmethod
    def _validate_problem_id(problem_id: str) -> None:
        match = re.fullmatch(r"P(\d{2})", problem_id)
        if not match or not 1 <= int(match.group(1)) <= 61:
            raise ValidationError(
                "problem_id must reference an existing P01-P61 identifier in the owner-designated Map."
            )

    def create_link(
        self,
        *,
        product_id: str,
        evidence_id: str,
        claim_id: str,
        problem_id: str,
        problem_type: str,
        problem_definition_ref: str,
        relationship_role: str,
        relationship_status: str,
        semantic_basis: str,
        limitations: str,
        decision_basis: str,
        problem_map_version: str = PROBLEM_MAP_VERSION,
        variant: str = "UNKNOWN",
        market_region: str = "UNKNOWN",
    ) -> ProductProblemLink:
        product_id = self._required_text(product_id, "product_id")
        evidence_id = self._required_text(evidence_id, "evidence_id")
        claim_id = self._required_text(claim_id, "claim_id")
        problem_id = self._required_text(problem_id, "problem_id").upper()
        problem_type = self._required_text(problem_type, "problem_type")
        problem_definition_ref = self._required_text(
            problem_definition_ref, "problem_definition_ref"
        )
        semantic_basis = self._required_text(semantic_basis, "semantic_basis")
        limitations = self._required_text(limitations, "limitations")
        decision_basis = self._required_text(decision_basis, "decision_basis")
        problem_map_version = self._required_text(
            problem_map_version, "problem_map_version"
        )
        market_region = self._required_text(market_region, "market_region").upper()
        variant = self._required_text(variant, "variant").upper()
        relationship_role = self._required_text(
            relationship_role, "relationship_role"
        ).lower()
        relationship_status = self._required_text(
            relationship_status, "relationship_status"
        ).upper()

        self._validate_problem_id(problem_id)
        if problem_map_version != self.PROBLEM_MAP_VERSION:
            raise ValidationError(
                f"Unsupported problem_map_version: {problem_map_version}"
            )
        if problem_id == "P22":
            raise ValidationError(
                "P22 is Context/reference only and must not receive an independent ProductProblemLink."
            )
        if relationship_role not in self.ALLOWED_ROLES:
            raise ValidationError(
                f"Invalid relationship_role. Allowed: {sorted(self.ALLOWED_ROLES)}"
            )
        if relationship_status == "SUPPORTED":
            raise ValidationError(
                "SUPPORTED is disabled in this implementation phase; all evidence, identity, "
                "canonical-definition, and semantic gates require a separately approved transition design."
            )
        if relationship_status not in self.ALLOWED_STATUSES:
            raise ValidationError(
                f"Invalid relationship_status. Allowed: {sorted(self.ALLOWED_STATUSES)}"
            )
        if variant not in self.ALLOWED_VARIANTS:
            raise ValidationError(
                f"Invalid variant. Allowed: {sorted(self.ALLOWED_VARIANTS)}"
            )

        product = self.db.query(Product).filter(Product.product_id == product_id).first()
        if product is None:
            raise NotFoundError(f"Product {product_id} not found.")

        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.evidence_id == evidence_id)
            .first()
        )
        if evidence is None:
            raise NotFoundError(f"Evidence {evidence_id} not found.")
        if evidence.product_id != product_id:
            raise ValidationError("Evidence must belong to the same product as the link.")
        if not evidence.claim_id or evidence.claim_id != claim_id:
            raise ValidationError("claim_id must exactly match the selected Evidence claim_id.")
        if (evidence.conflict_status or "NONE").strip().upper() == "CONFLICT":
            raise ValidationError("Conflicted Evidence cannot anchor a ProductProblemLink.")
        if (evidence.qa_status or "PENDING").strip().upper() == "REJECTED":
            raise ValidationError("Rejected Evidence cannot anchor a ProductProblemLink.")

        product_market = (product.market_region or "").strip().upper()
        evidence_market = (evidence.market_region or "").strip().upper()
        if product_market and product_market != "UNKNOWN" and product_market != market_region:
            raise ValidationError("Link market_region does not match the Product market.")
        if evidence_market and evidence_market != "UNKNOWN" and evidence_market != market_region:
            raise ValidationError("Link market_region does not match the Evidence market.")

        duplicate_scope = {
            "product_id": product_id,
            "evidence_id": evidence_id,
            "problem_id": problem_id,
            "relationship_role": relationship_role,
            "variant": variant,
            "market_region": market_region,
        }
        if self.repository.find_duplicate_scope(**duplicate_scope):
            raise ConflictError("A ProductProblemLink already exists for this evidence/problem scope.")

        try:
            return self.repository.create(
                link_id=f"PPL-{uuid.uuid4().hex}",
                product_id=product_id,
                variant=variant,
                market_region=market_region,
                claim_id=claim_id,
                evidence_id=evidence_id,
                problem_id=problem_id,
                problem_type=problem_type,
                problem_definition_ref=problem_definition_ref,
                relationship_role=relationship_role,
                relationship_status=relationship_status,
                semantic_basis=semantic_basis,
                limitations=limitations,
                decision_basis=decision_basis,
                problem_map_version=problem_map_version,
            )
        except Exception:
            self.db.rollback()
            raise

    def list_by_product(self, product_id: str) -> List[ProductProblemLink]:
        return self.repository.list_by_product(product_id)

    def list_by_problem(self, problem_id: str) -> List[ProductProblemLink]:
        problem_id = self._required_text(problem_id, "problem_id").upper()
        self._validate_problem_id(problem_id)
        return self.repository.list_by_problem(problem_id)
