"""Canonical field taxonomy shared by Evidence and ProductKnowledge services."""

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

# Only fields with explicit downstream semantics may be reclassification targets.
RECLASSIFIABLE_EVIDENCE_FIELDS = frozenset(
    # Identity fields are conflict-classification domains, not ProductKnowledge
    # payload targets. Reclassification must not claim support for data that
    # ProductKnowledge does not persist or interpret.
    BLOCKING_KNOWLEDGE_FIELDS | {"claim"}
)

__all__ = [
    "BLOCKING_KNOWLEDGE_FIELDS",
    "IDENTITY_FIELDS",
    "RECLASSIFIABLE_EVIDENCE_FIELDS",
]
