"""Regional hair-state capture; descriptive records only, no photo-based inference."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class HairRegion(str, Enum):
    ROOTS = "roots"
    MID_LENGTHS = "mid_lengths"
    ENDS = "ends"
    PATCH = "patch_or_zone"

class ObservationSource(str, Enum):
    CLIENT = "client_reported"
    PROFESSIONAL = "professional_observed"
    IMAGE_ONLY = "image_only"
    DOCUMENTED = "documented"
    UNKNOWN = "unknown"

class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class RegionalHairState:
    region: HairRegion
    region_label: str
    color_description: str
    condition_description: str
    texture_description: str
    source: ObservationSource
    confidence: Confidence
    limitations: tuple[str, ...]
    conflicts: tuple[str, ...] = ()

@dataclass(frozen=True)
class RegionalStateAssessment:
    status: str
    missing_regions: tuple[str, ...]
    uncertain_regions: tuple[str, ...]
    conflict_regions: tuple[str, ...]
    message: str

EXPECTED_REGIONS = (HairRegion.ROOTS, HairRegion.MID_LENGTHS, HairRegion.ENDS)

def make_regional_state(region: object, region_label: object = "", color_description: object = "",
                        condition_description: object = "", texture_description: object = "",
                        source: object = "unknown", confidence: object = "unknown",
                        limitations: object = (), conflicts: object = ()) -> RegionalHairState | None:
    try:
        reg, src, conf = HairRegion(region), ObservationSource(source), Confidence(confidence)
    except (ValueError, TypeError):
        return None
    def safe_text(value: object) -> str:
        return value.strip() if isinstance(value, str) else ""
    lim = tuple(safe_text(x) for x in limitations if isinstance(x, str)) if isinstance(limitations, (tuple, list)) else ()
    cfl = tuple(safe_text(x) for x in conflicts if isinstance(x, str)) if isinstance(conflicts, (tuple, list)) else ()
    if src == ObservationSource.IMAGE_ONLY:
        lim = tuple(dict.fromkeys((*lim, "Image-only visual description; do not infer porosity, structure, chemical history, or exact color level.")))
        if conf != Confidence.UNKNOWN:
            conf = Confidence.LOW
    return RegionalHairState(reg, safe_text(region_label), safe_text(color_description),
        safe_text(condition_description), safe_text(texture_description), src, conf, lim, cfl)

def assess_regional_state(records: object, expected_regions: object = EXPECTED_REGIONS) -> RegionalStateAssessment:
    if not isinstance(records, (tuple, list)):
        return RegionalStateAssessment("invalid_records", tuple(str(r.value) for r in EXPECTED_REGIONS), (), (),
            "Regional records must be supplied as a list or tuple; no assessment is produced.")
    if not isinstance(expected_regions, (tuple, list)) or not expected_regions:
        return RegionalStateAssessment("invalid_scope", (), (), (),
            "Expected regions must be an explicit non-empty list; no assessment is produced.")
    try:
        expected = tuple(dict.fromkeys(HairRegion(r) for r in expected_regions))
    except (ValueError, TypeError):
        return RegionalStateAssessment("invalid_scope", (), (), (),
            "Expected region list contains invalid values; no assessment is produced.")
    if any(not isinstance(r, RegionalHairState) for r in records):
        return RegionalStateAssessment("invalid_records", tuple(r.value for r in expected), (), (),
            "Invalid regional record; dependent assessment is blocked.")
    seen = {r.region for r in records}
    missing = tuple(r.value for r in expected if r not in seen)
    uncertain = tuple(r.region.value for r in records if r.source in (ObservationSource.UNKNOWN, ObservationSource.IMAGE_ONLY)
        or r.confidence in (Confidence.LOW, Confidence.UNKNOWN))
    conflicts = tuple(r.region.value for r in records if r.conflicts)
    if conflicts:
        return RegionalStateAssessment("conflict_review", missing, uncertain, conflicts,
            "Regional observations conflict; reconcile before dependent evaluation.")
    if missing:
        return RegionalStateAssessment("needs_more_information", missing, uncertain, (),
            "Some expected regions are not recorded; request regional information.")
    if uncertain:
        return RegionalStateAssessment("limited_review", (), uncertain, (),
            "Regional records are present but uncertain or image-only; use only limited descriptive review.")
    return RegionalStateAssessment("regional_state_recorded", (), (), (),
        "Regional descriptive state captured. This is not feasibility, safety, formula, or result guidance.")
