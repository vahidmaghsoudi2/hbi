"""P4 P0 — Governance constants: fields, actions, transitions, permissions."""
from __future__ import annotations
from typing import Dict, FrozenSet, Set, Tuple
from app.models.user_role import ROLE_ADMIN, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA

PRODUCT_GOVERNANCE_KEYS: FrozenSet[str] = frozenset({
    "status", "identity_status", "identity_confidence", "identity_source_refs",
    "qa_verdict", "qa_reviewed_at", "qa_notes",
})

PRODUCT_INFORMATIONAL_KEYS: FrozenSet[str] = frozenset({
    "brand", "product_name", "variant", "size_value", "size_unit", "barcode_gtin",
    "market_region", "country_of_origin", "packaging_version", "category_id",
})

ACTION_CREATE = "CREATE"
ACTION_EDIT = "EDIT"
ACTION_SUBMIT = "SUBMIT"
ACTION_QA_CHANGE = "QA_CHANGE"
ACTION_APPROVE = "APPROVE"
ACTION_REJECT = "REJECT"
ACTION_ACTIVATE = "ACTIVATE"
ACTION_ARCHIVE = "ARCHIVE"
ACTION_IDENTITY_CHANGE = "IDENTITY_CHANGE"
ACTION_ENTER_QA_REVIEW = "ENTER_QA_REVIEW"

STATUS_DRAFT = "DRAFT"
STATUS_SUBMITTED = "SUBMITTED"
STATUS_QA_REVIEW = "QA_REVIEW"
STATUS_APPROVED = "APPROVED"
STATUS_ACTIVE = "ACTIVE"
STATUS_REJECTED = "REJECTED"
STATUS_ARCHIVED = "ARCHIVED"

ALLOWED_TRANSITIONS: Dict[Tuple[str, str], str] = {
    (STATUS_DRAFT, ACTION_SUBMIT): STATUS_SUBMITTED,
    (STATUS_SUBMITTED, ACTION_ENTER_QA_REVIEW): STATUS_QA_REVIEW,
    (STATUS_QA_REVIEW, ACTION_APPROVE): STATUS_APPROVED,
    (STATUS_QA_REVIEW, ACTION_REJECT): STATUS_REJECTED,
    (STATUS_APPROVED, ACTION_ACTIVATE): STATUS_ACTIVE,
    (STATUS_ACTIVE, ACTION_ARCHIVE): STATUS_ARCHIVED,
}

TRANSITION_ROLES: Dict[str, FrozenSet[str]] = {
    ACTION_SUBMIT: frozenset({ROLE_REVIEWER_QA, ROLE_PO}),
    ACTION_ENTER_QA_REVIEW: frozenset({ROLE_REVIEWER_QA, ROLE_PO}),
    ACTION_APPROVE: frozenset({ROLE_PO}),
    ACTION_REJECT: frozenset({ROLE_REVIEWER_QA, ROLE_PO}),
    ACTION_ACTIVATE: frozenset({ROLE_PO}),
    ACTION_ARCHIVE: frozenset({ROLE_PO}),
}

def can_create_product(roles: Set[str]) -> bool:
    return bool(roles & {ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO}) or ROLE_ADMIN in roles

def can_edit_informational(roles: Set[str]) -> bool:
    return bool(roles & {ROLE_EDITOR, ROLE_REVIEWER_QA, ROLE_PO}) or ROLE_ADMIN in roles

def can_view_mutation_log(roles: Set[str]) -> bool:
    return bool(roles & {ROLE_REVIEWER_QA, ROLE_PO, ROLE_ADMIN})
