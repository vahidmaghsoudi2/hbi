import hashlib
import json
import re
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_problem_link import ProductProblemLink
from app.repositories.product_problem_link_repository import ProductProblemLinkRepository


class ProductProblemLinkService:
    """Append-only assessment service. Reassessment always creates a successor row."""

    ALLOWED_ROLES = frozenset({"presentation", "context", "clinical_anchor", "sequela"})
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
            raise ValidationError(f"{field} is required.")
        return normalized

    @staticmethod
    def _validate_problem_id(problem_id: str) -> None:
        match = re.fullmatch(r"P(\d{2})", problem_id)
        if not match or not 1 <= int(match.group(1)) <= 61:
            raise ValidationError("problem_id must reference an existing P01-P61 identifier.")

    @staticmethod
    def _snapshot(row):
        if row is None:
            return None
        fields = (
            "link_id", "product_id", "evidence_id", "claim_id", "problem_id",
            "problem_type", "problem_definition_ref", "relationship_role",
            "relationship_status", "feature_basis", "outcome", "semantic_basis",
            "limitations", "decision_basis", "problem_map_version", "variant",
            "market_region", "assertion_key", "revision_no", "supersedes_link_id",
        )
        return {key: getattr(row, key) for key in fields}

    @staticmethod
    def _family_key(data):
        stable = {key: data[key] for key in (
            "product_id", "evidence_id", "claim_id", "problem_id",
            "relationship_role", "variant", "market_region", "problem_map_version",
            "feature_basis", "outcome",
        )}
        raw = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _fingerprint(data):
        stable = {k: v for k, v in data.items() if k != "idempotency_key"}
        raw = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _normalize_and_validate(self, data):
        text_fields = (
            "product_id", "evidence_id", "claim_id", "problem_id", "problem_type",
            "problem_definition_ref", "feature_basis", "outcome", "semantic_basis",
            "limitations", "decision_basis", "reason", "problem_map_version",
            "market_region", "variant", "relationship_role", "relationship_status",
            "idempotency_key",
        )
        for field in text_fields:
            data[field] = self._required_text(data.get(field), field)
        data["problem_id"] = data["problem_id"].upper()
        data["market_region"] = data["market_region"].upper()
        data["variant"] = data["variant"].upper()
        data["relationship_role"] = data["relationship_role"].lower()
        data["relationship_status"] = data["relationship_status"].upper()
        if len(data["idempotency_key"]) < 8:
            raise ValidationError("idempotency_key must contain at least 8 characters.")
        self._validate_problem_id(data["problem_id"])
        if data["problem_map_version"] != self.PROBLEM_MAP_VERSION:
            raise ValidationError(f"Unsupported problem_map_version: {data['problem_map_version']}")
        if data["problem_id"] == "P22":
            raise ValidationError("P22 is Context/reference only and must not receive an independent ProductProblemLink.")
        if data["relationship_role"] not in self.ALLOWED_ROLES:
            raise ValidationError(f"Invalid relationship_role. Allowed: {sorted(self.ALLOWED_ROLES)}")
        if data["relationship_status"] == "SUPPORTED":
            raise ValidationError("SUPPORTED is disabled; this service cannot approve suitability or recommendations.")
        if data["relationship_status"] not in self.ALLOWED_STATUSES:
            raise ValidationError(f"Invalid relationship_status. Allowed: {sorted(self.ALLOWED_STATUSES)}")
        if data["variant"] not in self.ALLOWED_VARIANTS:
            raise ValidationError(f"Invalid variant. Allowed: {sorted(self.ALLOWED_VARIANTS)}")
        product = self.db.query(Product).filter(Product.product_id == data["product_id"]).first()
        if product is None:
            raise NotFoundError(f"Product {data['product_id']} not found.")
        evidence = self.db.query(Evidence).filter(Evidence.evidence_id == data["evidence_id"]).first()
        if evidence is None:
            raise NotFoundError(f"Evidence {data['evidence_id']} not found.")
        if evidence.product_id != data["product_id"]:
            raise ValidationError("Evidence must belong to the same product as the link.")
        if not evidence.claim_id or evidence.claim_id != data["claim_id"]:
            raise ValidationError("claim_id must exactly match the selected Evidence claim_id.")
        if (evidence.conflict_status or "NONE").strip().upper() == "CONFLICT":
            raise ValidationError("Conflicted Evidence cannot anchor a ProductProblemLink.")
        if (evidence.qa_status or "PENDING").strip().upper() == "REJECTED":
            raise ValidationError("Rejected Evidence cannot anchor a ProductProblemLink.")
        product_market = (product.market_region or "").strip().upper()
        evidence_market = (evidence.market_region or "").strip().upper()
        if product_market and product_market != "UNKNOWN" and product_market != data["market_region"]:
            raise ValidationError("Link market_region does not match the Product market.")
        if evidence_market and evidence_market != "UNKNOWN" and evidence_market != data["market_region"]:
            raise ValidationError("Link market_region does not match the Evidence market.")

    def _existing_idempotent(self, key, fingerprint):
        existing = self.repository.find_by_idempotency_key(key)
        if existing is None:
            return None
        if existing.request_fingerprint != fingerprint:
            raise ConflictError("idempotency_key was already used with a different request.")
        return existing

    def _persist(self, data, *, actor_id, actor_role, predecessor=None):
        actor_id = self._required_text(actor_id, "authenticated actor_id")
        assertion_key = self._family_key(data)
        latest = self.repository.latest_for_assertion(assertion_key)
        if predecessor is None and latest is not None:
            raise ConflictError("This assertion already exists; use the reassessment endpoint.")
        if predecessor is not None and latest is not None and latest.link_id != predecessor.link_id:
            raise ConflictError("This assertion revision already exists or is not the latest.")
        revision_no = 1
        if predecessor is not None and latest is not None and latest.link_id == predecessor.link_id:
            revision_no = (predecessor.revision_no or 0) + 1
        fingerprint = self._fingerprint(data)
        row = self.repository.create(
            link_id=f"PPL-{uuid.uuid4().hex}",
            product_id=data["product_id"], variant=data["variant"],
            market_region=data["market_region"], claim_id=data["claim_id"],
            evidence_id=data["evidence_id"], problem_id=data["problem_id"],
            problem_type=data["problem_type"],
            problem_definition_ref=data["problem_definition_ref"],
            relationship_role=data["relationship_role"],
            relationship_status=data["relationship_status"],
            feature_basis=data["feature_basis"], outcome=data["outcome"],
            semantic_basis=data["semantic_basis"], limitations=data["limitations"],
            decision_basis=data["decision_basis"],
            problem_map_version=data["problem_map_version"],
            assertion_key=assertion_key, revision_no=revision_no,
            supersedes_link_id=predecessor.link_id if predecessor else None,
            idempotency_key=data["idempotency_key"], request_fingerprint=fingerprint,
        )
        self.repository.append_event(
            event_id=f"PPLE-{uuid.uuid4().hex}", link_id=row.link_id,
            assertion_key=assertion_key, revision_no=revision_no,
            actor_id=actor_id, actor_role=actor_role,
            event_type="ASSESSMENT_CREATED" if predecessor is None else "ASSESSMENT_REVISED",
            reason=data["reason"],
            before_state=json.dumps(self._snapshot(predecessor), ensure_ascii=False, default=str) if predecessor else None,
            after_state=json.dumps(self._snapshot(row), ensure_ascii=False, default=str),
            correlation_id=data["idempotency_key"],
        )
        return row

    def create_link(self, *, actor_id="UNIT_TEST_ACTOR", actor_role="UNIT_TEST", **payload):
        data = dict(payload)
        self._normalize_and_validate(data)
        fingerprint = self._fingerprint(data)
        existing = self._existing_idempotent(data["idempotency_key"], fingerprint)
        if existing is not None:
            return existing
        legacy = self.repository.find_legacy_duplicate_scope(
            product_id=data["product_id"], evidence_id=data["evidence_id"],
            problem_id=data["problem_id"], relationship_role=data["relationship_role"],
            variant=data["variant"], market_region=data["market_region"],
        )
        if legacy is not None:
            raise ConflictError("A legacy assessment exists for this scope; use its reassessment endpoint.")
        try:
            return self._persist(data, actor_id=actor_id, actor_role=actor_role)
        except IntegrityError as exc:
            raise ConflictError("Assessment uniqueness or idempotency constraint was violated.") from exc

    def reassess_link(self, link_id: str, *, expected_revision_no: Optional[int],
                      actor_id: str, actor_role: Optional[str], **payload):
        predecessor = self.repository.get_by_id(link_id)
        if predecessor is None:
            raise NotFoundError(f"ProductProblemLink {link_id} not found.")
        data = dict(payload)
        self._normalize_and_validate(data)
        fingerprint = self._fingerprint(data)
        existing = self._existing_idempotent(data["idempotency_key"], fingerprint)
        if existing is not None:
            return existing
        if predecessor.revision_no is None:
            if expected_revision_no is not None:
                raise ConflictError("Legacy assessment has no assigned revision number; expected_revision_no must be omitted.")
        elif expected_revision_no != predecessor.revision_no:
            raise ConflictError("Stale assessment revision; reload the latest revision before reassessing.")
        if self.repository.find_successor(predecessor.link_id) is not None:
            raise ConflictError("This assessment already has a successor; reassess the latest assessment.")
        immutable_scope = ("product_id", "problem_id", "relationship_role", "variant", "market_region")
        if any(getattr(predecessor, field) != data[field] for field in immutable_scope):
            raise ValidationError("Reassessment must keep the same product/problem/role/variant/market scope.")
        if predecessor.assertion_key:
            latest_old = self.repository.latest_for_assertion(predecessor.assertion_key)
            if latest_old is not None and latest_old.link_id != predecessor.link_id:
                raise ConflictError("The supplied assessment is not the latest revision.")
        try:
            return self._persist(data, actor_id=actor_id, actor_role=actor_role, predecessor=predecessor)
        except IntegrityError as exc:
            raise ConflictError("Assessment revision or idempotency constraint was violated.") from exc

    def list_by_product(self, product_id: str) -> List[ProductProblemLink]:
        return self.repository.list_by_product(product_id)

    def list_by_problem(self, problem_id: str) -> List[ProductProblemLink]:
        problem_id = self._required_text(problem_id, "problem_id").upper()
        self._validate_problem_id(problem_id)
        return self.repository.list_by_problem(problem_id)

    def history(self, link_id: str):
        row = self.repository.get_by_id(link_id)
        if row is None:
            raise NotFoundError(f"ProductProblemLink {link_id} not found.")
        revisions = [row]
        seen = {row.link_id}
        cursor = row
        while cursor.supersedes_link_id:
            cursor = self.repository.get_by_id(cursor.supersedes_link_id)
            if cursor is None or cursor.link_id in seen:
                break
            revisions.insert(0, cursor)
            seen.add(cursor.link_id)
        cursor = row
        while True:
            cursor = self.repository.find_successor(cursor.link_id)
            if cursor is None or cursor.link_id in seen:
                break
            revisions.append(cursor)
            seen.add(cursor.link_id)
        events = self.repository.list_events([item.link_id for item in revisions])
        return {"assessments": revisions, "events": events}
