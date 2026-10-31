"""ProductKnowledge rebuild from Evidence — version-aware, role-preserving, domain-scoped."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.product_knowledge_repository import ProductKnowledgeRepository
from app.services.base import BaseService

# Operator / analyst role vocabulary (must round-trip through rebuild).
ALLOWED_INGREDIENT_ROLES = frozenset(
    {"CORE", "SUPPORT", "CLAIM-LINK", "RISK", "TECH", "UNKNOWN"}
)

# Fields that affect whole-product knowledge status when in unresolved CONFLICT.
BLOCKING_KNOWLEDGE_FIELDS = frozenset(
    {
        "ingredients",
        "ingredient_roles",
        "ingredient_role",
        "known_use_cases",
        "use_case",
        "contraindications",
        "usage_instructions",
        "usage_instruction",
        "usage",
        "manufacturer_claims",
        "manufacturer_claim",
        "claimed_benefits",
        "benefit",
        "other_attributes",
        "other_attribute",
    }
)

# Identity-level fields: conflict here is product identity, not knowledge merge noise.
IDENTITY_FIELDS = frozenset(
    {
        "brand",
        "product_name",
        "barcode",
        "gtin",
        "barcode_gtin",
        "variant",
        "size_value",
        "size_unit",
        "packaging_version",
        "market_region",
    }
)


def version_scope_key(
    *,
    evidence_market: Optional[str],
    product_market: Optional[str],
    packaging_version: Optional[str],
) -> str:
    """Build a non-guessing scope key. Empty segments stay empty (not defaulted to IR)."""
    market = (evidence_market or product_market or "").strip()
    pack = (packaging_version or "").strip()
    return f"market={market}|pack={pack}"


def parse_role_entries(claim: str) -> List[Dict[str, str]]:
    """
    Structured role entries only.

    Accepts:
    - JSON list [{"ingredient": "...", "role": "CORE"}, ...]
    - Explicit "Name:ROLE" / "Name=ROLE" comma segments

    Plain legacy lists such as "humectant, emollient" (no delimiter / no JSON)
    return [] so callers can keep the pre-existing comma-string contract.
    Invalid explicit roles become UNKNOWN (explicit), never dropped silently.
    """
    claim = (claim or "").strip()
    if not claim:
        return []
    if claim.startswith("["):
        try:
            data = json.loads(claim)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, list):
            out: List[Dict[str, str]] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                ing = str(item.get("ingredient") or item.get("name") or "").strip()
                role = str(item.get("role") or "UNKNOWN").strip().upper()
                if role not in ALLOWED_INGREDIENT_ROLES:
                    role = "UNKNOWN"
                if ing:
                    out.append({"ingredient": ing, "role": role})
            return out
        return []
    entries: List[Dict[str, str]] = []
    for part in claim.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            name, role = part.split(":", 1)
        elif "=" in part:
            name, role = part.split("=", 1)
        else:
            # Legacy free-text token — not a structured Ingredient/Role pair.
            continue
        role_u = role.strip().upper()
        if role_u not in ALLOWED_INGREDIENT_ROLES:
            role_u = "UNKNOWN"
        name = name.strip()
        if name:
            entries.append({"ingredient": name, "role": role_u})
    return entries


def parse_legacy_role_tokens(claim: str) -> List[str]:
    """Comma-separated free-text role labels without Ingredient:ROLE mapping."""
    claim = (claim or "").strip()
    if not claim or claim.startswith("["):
        return []
    # Preserve unstructured segments even when the same claim also contains
    # explicit Name:ROLE / Name=ROLE pairs. Mixed input must never drop tokens.
    tokens: List[str] = []
    for part in claim.split(","):
        part = part.strip()
        if part and ":" not in part and "=" not in part:
            tokens.append(part)
    return tokens


class ProductKnowledgeService(BaseService[ProductKnowledge, ProductKnowledgeRepository]):
    def __init__(self, db: Session):
        super().__init__(ProductKnowledgeRepository(db), db)
        self.evidence_repo = EvidenceRepository(db)

    def get_or_create(self, product_id: str) -> ProductKnowledge:
        knowledge = self.repository.find_by_product(product_id)
        if not knowledge:
            knowledge = self.repository.create(
                product_knowledge_id=f"PK-{product_id}",
                product_id=product_id,
            )
        return knowledge

    _QA_APPROVED = frozenset({"APPROVED", "VERIFIED"})

    def update_from_evidence(self, product_id: str) -> ProductKnowledge:
        """Rebuild ProductKnowledge from approved Evidence with version isolation."""
        knowledge = self.get_or_create(product_id)
        # Tests may construct the service via __new__ without BaseService.__init__.
        db = getattr(self, "db", None)
        product = None
        if db is not None:
            product = db.query(Product).filter(Product.product_id == product_id).first()
        evidences = self.evidence_repo.find_by_product(product_id)

        product_market = getattr(product, "market_region", None) if product else None
        packaging_version = getattr(product, "packaging_version", None) if product else None

        scopes: Dict[str, List[Evidence]] = {}
        for ev in evidences:
            key = version_scope_key(
                evidence_market=getattr(ev, "market_region", None),
                product_market=product_market,
                packaging_version=packaging_version,
            )
            scopes.setdefault(key, []).append(ev)

        preferred = version_scope_key(
            evidence_market=None,
            product_market=product_market,
            packaging_version=packaging_version,
        )
        if preferred in scopes:
            primary_list = scopes[preferred]
            other_scopes = {k: v for k, v in scopes.items() if k != preferred}
        elif len(scopes) == 1:
            primary_list = next(iter(scopes.values()))
            other_scopes = {}
        else:
            primary_list = []
            other_scopes = scopes

        approved: List[Evidence] = []
        ingredients: Set[str] = set()
        role_map: Dict[str, str] = {}
        role_conflicts: Set[str] = set()
        legacy_role_tokens: Set[str] = set()
        benefits: Set[str] = set()
        use_cases: Set[str] = set()
        contraindications: Set[str] = set()
        usage_instructions: Set[str] = set()
        manufacturer_claims: Set[str] = set()
        other_attributes: Dict[str, Any] = {}
        evidence_refs: List[str] = []
        domain_status: Dict[str, str] = {}
        domain_has_approved: Dict[str, bool] = {}
        domain_has_conflict: Dict[str, bool] = {}
        domain_has_evaluated_empty: Dict[str, bool] = {}
        domain_has_out_of_scope: Set[str] = set()

        def touch_domain(field: str, *, approved_hit: bool = False, conflict: bool = False, evaluated: bool = False):
            d = (field or "general").strip().lower() or "general"
            if approved_hit:
                domain_has_approved[d] = True
            if conflict:
                domain_has_conflict[d] = True
            if evaluated:
                domain_has_evaluated_empty[d] = True

        def ingest(ev: Evidence, *, allow_content: bool) -> None:
            qa = (getattr(ev, "qa_status", None) or "").strip().upper()
            conflict = (getattr(ev, "conflict_status", None) or "NONE").strip().upper()
            field = (ev.field or "").strip()
            field_l = field.lower()
            claim = (ev.claim or "").strip()

            if conflict == "CONFLICT":
                touch_domain(field_l or "general", conflict=True, evaluated=True)
                return

            if qa not in self._QA_APPROVED:
                if qa in {"REJECTED", "INVALID"}:
                    touch_domain(field_l or "general", evaluated=True)
                return

            if not allow_content:
                touch_domain(field_l or "general", evaluated=True)
                return

            approved.append(ev)
            touch_domain(field_l or "general", approved_hit=True, evaluated=True)

            if field_l == "ingredients" and claim:
                ingredients.update([i.strip() for i in claim.split(",") if i.strip()])
            elif field_l in ("ingredient_roles", "ingredient_role") and claim:
                structured = parse_role_entries(claim)
                if structured:
                    for entry in structured:
                        ing = entry["ingredient"]
                        role = entry["role"]
                        prev = role_map.get(ing)
                        if ing in role_conflicts:
                            # Once two distinct known roles conflict, never let a
                            # later row arbitrarily restore one of them.
                            ingredients.add(ing)
                            continue
                        if prev and prev != role:
                            if prev == "UNKNOWN":
                                role_map[ing] = role
                            elif role == "UNKNOWN":
                                pass
                            else:
                                touch_domain("ingredient_roles", conflict=True)
                                role_map.pop(ing, None)
                                role_conflicts.add(ing)
                        else:
                            role_map[ing] = role
                        ingredients.add(ing)
                # Mixed structured + legacy input is retained without guessing that
                # a legacy label is an ingredient or assigning it a fabricated role.
                for token in parse_legacy_role_tokens(claim):
                    legacy_role_tokens.add(token)
            elif field_l in ("claimed_benefits", "benefit") and claim:
                benefits.update([b.strip() for b in claim.split(",") if b.strip()])
            elif field_l in ("known_use_cases", "use_case") and claim:
                use_cases.update([u.strip() for u in claim.split(",") if u.strip()])
            elif field_l == "contraindications" and claim:
                contraindications.update([c.strip() for c in claim.split(",") if c.strip()])
            elif field_l in ("usage_instructions", "usage_instruction", "usage") and claim:
                usage_instructions.update([u.strip() for u in claim.split(",") if u.strip()])
            elif field_l in ("other_attributes", "other_attribute") and claim:
                if claim.startswith("{"):
                    try:
                        obj = json.loads(claim)
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                other_attributes[str(k)] = v
                        else:
                            other_attributes.setdefault("_entries", [])
                            if isinstance(other_attributes["_entries"], list):
                                other_attributes["_entries"].append(claim)
                    except json.JSONDecodeError:
                        other_attributes.setdefault("_unparsed", [])
                        if isinstance(other_attributes.get("_unparsed"), list):
                            other_attributes["_unparsed"].append(claim)
                else:
                    for part in claim.split(";"):
                        part = part.strip()
                        if not part:
                            continue
                        if ":" in part:
                            k, v = part.split(":", 1)
                            other_attributes[k.strip()] = v.strip()
                        else:
                            other_attributes.setdefault("_entries", [])
                            if isinstance(other_attributes["_entries"], list):
                                other_attributes["_entries"].append(part)
            elif (
                field_l in ("manufacturer_claims", "manufacturer_claim")
                and claim
                and (getattr(ev, "claim_type", None) or "").strip().upper() == "MANUFACTURER_CLAIM"
            ):
                manufacturer_claims.update([m.strip() for m in claim.split(",") if m.strip()])
            elif (
                field_l == "claim"
                and (getattr(ev, "claim_type", None) or "").strip().upper() == "MANUFACTURER_CLAIM"
                and claim
            ):
                manufacturer_claims.update([m.strip() for m in claim.split(",") if m.strip()])

            if ev.claim_id:
                evidence_refs.append(ev.claim_id)

        for ev in primary_list:
            ingest(ev, allow_content=True)

        for _key, ev_list in other_scopes.items():
            for ev in ev_list:
                qa = (getattr(ev, "qa_status", None) or "").strip().upper()
                conflict = (getattr(ev, "conflict_status", None) or "NONE").strip().upper()
                field_l = (ev.field or "general").strip().lower()
                # Evidence from another market/version must never inject its
                # conflict verdict into this ProductKnowledge scope. It can,
                # however, make an otherwise populated domain PARTIAL because
                # potentially relevant evidence was deliberately excluded.
                if field_l in BLOCKING_KNOWLEDGE_FIELDS and (
                    conflict == "CONFLICT" or qa in self._QA_APPROVED
                ):
                    domain_has_out_of_scope.add(field_l)

        all_domains = set(domain_has_approved) | set(domain_has_conflict) | set(domain_has_evaluated_empty) | set(domain_status)
        for d in all_domains:
            if domain_has_conflict.get(d):
                domain_status[d] = "CONFLICT"
            elif d in domain_has_out_of_scope:
                domain_status[d] = "PARTIAL"
            elif domain_has_approved.get(d):
                domain_status[d] = "SUPPORTED"
            elif domain_has_evaluated_empty.get(d) or d in domain_status:
                domain_status[d] = domain_status.get(d) or "UNKNOWN"

        if not all_domains and not evidences:
            overall: Optional[str] = None
        elif not all_domains and evidences:
            overall = "UNKNOWN"
        elif any(domain_status.get(d) == "CONFLICT" for d in domain_status if d in BLOCKING_KNOWLEDGE_FIELDS or d == "ingredient_roles"):
            overall = "CONFLICT"
        elif any(domain_status.get(d) == "CONFLICT" for d in domain_status if d in IDENTITY_FIELDS):
            overall = "CONFLICT" if not any(domain_status.get(d) == "SUPPORTED" for d in BLOCKING_KNOWLEDGE_FIELDS) else "PARTIAL"
        elif any(domain_status.get(d) == "SUPPORTED" for d in domain_status):
            if any(domain_status.get(d) in {"UNKNOWN", "PARTIAL"} for d in domain_status):
                overall = "PARTIAL"
            else:
                overall = "SUPPORTED"
        else:
            overall = "UNKNOWN"

        if role_map:
            roles_payload = [
                {"ingredient": ing, "role": role_map[ing]} for ing in sorted(role_map.keys())
            ]
            ingredient_roles_value = json.dumps(roles_payload, ensure_ascii=False)
            if legacy_role_tokens:
                # Keep mixed legacy labels in the neutral catch-all instead of
                # misclassifying them as ingredients or silently dropping them.
                other_attributes["_legacy_ingredient_role_tokens"] = sorted(legacy_role_tokens)
        elif legacy_role_tokens:
            # Preserve pre-structured Product Intake contract: plain comma list.
            ingredient_roles_value = ", ".join(sorted(legacy_role_tokens))
        else:
            ingredient_roles_value = None

        update_data = {
            "ingredients": ", ".join(sorted(ingredients)) if ingredients else None,
            "ingredient_roles": ingredient_roles_value,
            "claimed_benefits": ", ".join(sorted(benefits)) if benefits else None,
            "known_use_cases": ", ".join(sorted(use_cases)) if use_cases else None,
            "contraindications": ", ".join(sorted(contraindications)) if contraindications else None,
            "usage_instructions": ", ".join(sorted(usage_instructions)) if usage_instructions else None,
            "manufacturer_claims": ", ".join(sorted(manufacturer_claims)) if manufacturer_claims else None,
            "other_attributes": json.dumps(other_attributes, ensure_ascii=False) if other_attributes else None,
            "evidence_refs": ", ".join(evidence_refs) if evidence_refs else None,
            "evidence_status": overall,
            "domain_evidence_status": json.dumps(domain_status, ensure_ascii=False) if domain_status else None,
            "knowledge_confidence": self._calculate_confidence_from_evidences(approved),
        }

        updated = self.repository.update_knowledge(product_id, **update_data)
        if not updated:
            updated = self.repository.create(
                product_knowledge_id=f"PK-{product_id}",
                product_id=product_id,
                **update_data,
            )
        return updated

    def _calculate_confidence_from_evidences(self, evidences: List[Evidence]) -> float:
        if not evidences:
            return 0.0
        strength_map = {
            "STRONG": 0.9,
            "MODERATE": 0.6,
            "WEAK": 0.3,
            "UNVERIFIED": 0.1,
        }
        total_weight = 0.0
        count = 0
        for ev in evidences:
            strength = ev.evidence_strength or "UNVERIFIED"
            weight = strength_map.get(strength, 0.1)
            total_weight += weight
            count += 1
        avg = total_weight / count if count > 0 else 0.0
        return round(avg, 2)
