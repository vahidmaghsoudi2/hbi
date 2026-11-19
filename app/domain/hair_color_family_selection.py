"""Explicit target-family selection; catalog labels are not technical suitability."""
from __future__ import annotations
from dataclasses import dataclass
from app.domain.hair_catalog_families import known_catalog_family_labels

MAX_FAMILY_CHOICES = 3
CATALOG_FAMILY_LABELS = known_catalog_family_labels()

@dataclass(frozen=True)
class FamilySelection:
    selected_labels: tuple[str, ...]
    status: str
    invalid_labels: tuple[str, ...]
    message: str
    selection_source: str = "client_explicit"
    ranking_basis: str = "client_order_only"

def select_target_families(labels: object, source: object = "client_explicit") -> FamilySelection:
    if source != "client_explicit":
        return FamilySelection((), "invalid_source", (), "Only explicitly client-selected labels are accepted here.")
    if not isinstance(labels, (tuple, list)):
        return FamilySelection((), "needs_clarification", (), "Provide an explicit list of target catalog-family labels.")
    if not labels:
        return FamilySelection((), "needs_clarification", (), "No target family was selected; ask for clarification.")
    if any(not isinstance(label, str) or not label for label in labels):
        return FamilySelection((), "invalid_labels", (), "Family labels must be non-empty exact strings.")
    invalid = tuple(label for label in labels if label not in CATALOG_FAMILY_LABELS)
    if invalid:
        return FamilySelection((), "family_unrecognized", invalid, "Unknown or non-catalog family labels remain unclassified; clarify without fuzzy matching.")
    if len(set(labels)) != len(labels):
        return FamilySelection((), "invalid_labels", (), "Duplicate family labels are not accepted.")
    if len(labels) > MAX_FAMILY_CHOICES:
        return FamilySelection((), "too_many_choices", (), "More than three explicit target-family choices were supplied; clarify priorities instead of truncating.")
    chosen = tuple(labels)
    return FamilySelection(chosen, "families_recorded_for_review",
        (), "Explicit target-family preference recorded in client order. No technical fit, feasibility, or result is inferred.")
