"""Prepared specialist-review package manifest; delivery is not claimed."""
from __future__ import annotations
from dataclasses import dataclass
from app.domain.hair_color_specialist_review_inventory import review_inventory

@dataclass(frozen=True)
class ReviewPackageTopic:
    topic_id: str
    document_refs: tuple[str,...]
    review_questions: tuple[str,...]
    evidence_request: str

PACKAGE_TOPICS=(
    ReviewPackageTopic("SR01",("docs/homepage/encyclopedia/hair-color/foundation/01-levels-and-underlying-pigments.md","docs/homepage/encyclopedia/hair-color/foundation/06-factors-affecting-color-result.md","docs/homepage/encyclopedia/hair-color/consultation/13-current-base-role.md","docs/homepage/encyclopedia/hair-color/consultation/16-regional-hair-state.md","docs/homepage/encyclopedia/hair-color/consultation/31-missing-data-test-gates.md"),("Are descriptive level/pigment statements within the evidence limits?","Which image-only statements must remain uncertain?"),"Review scope and evidence; no inferred pigment/chemistry from photos."),
    ReviewPackageTopic("SR02",("docs/homepage/encyclopedia/hair-color/foundation/02-color-wheel-neutralization.md","docs/homepage/encyclopedia/hair-color/foundation/05-underlying-pigment-tone-selection.md"),("Are general color-wheel/neutralization principles accurate?","What conditions or exceptions require stopping?"),"Scientific sources and specialist review for any rule claim."),
    ReviewPackageTopic("SR03",("docs/homepage/encyclopedia/hair-color/foundation/03-tone-families.md","docs/homepage/encyclopedia/hair-color/catalog/10-bijourka-color-families.md"),("Are tone-family terms defined accurately?","Which catalog labels are only names, not technical assertions?"),"Terminology evidence and boundaries."),
    ReviewPackageTopic("SR04",("docs/homepage/encyclopedia/hair-color/foundation/04-depth-hue-intensity.md",),("Are depth/hue/reflect/intensity distinctions accurate and usable?"),"Evidence and definitions; scope of measurement."),
    ReviewPackageTopic("SR05",("docs/homepage/encyclopedia/hair-color/foundation/05-underlying-pigment-tone-selection.md","docs/homepage/encyclopedia/hair-color/foundation/06-factors-affecting-color-result.md"),("Are underlying-pigment/tone selection principles valid?","What is prohibited without product/hair evidence?"),"Rule-level source and specialist decision."),
    ReviewPackageTopic("SR06",("docs/homepage/encyclopedia/hair-color/foundation/06-factors-affecting-color-result.md",),("Are factor relationships accurate and appropriately limited?"),"Evidence and applicable scope."),
    ReviewPackageTopic("SR07",("docs/homepage/encyclopedia/hair-color/catalog/10-bijourka-color-families.md",),("Review raw catalog labels versus provisional editorial groups."), "Catalog identity evidence; group mappings are provisional."),
    ReviewPackageTopic("SR08",("docs/homepage/encyclopedia/hair-color/catalog/09-bijourka-numbering-rules.md","docs/homepage/encyclopedia/hair-color/catalog/11-owner-defined-rules.md"),("Review raw code/alias boundaries and special exceptions."), "Owner decisions and catalog identity only; no chemical inference."),
    ReviewPackageTopic("SR09",("docs/homepage/encyclopedia/hair-color/catalog/11-owner-defined-rules.md",),("Confirm scope of Natural Extra owner-defined rule; identify any technical claims requiring separate review."), "Owner rule is not scientific evidence."),
    ReviewPackageTopic("SR10",("docs/homepage/encyclopedia/hair-color/consultation/14-client-target-color.md","docs/homepage/encyclopedia/hair-color/consultation/17-family-selection-logic.md","docs/homepage/encyclopedia/hair-color/consultation/18-option-selection-logic.md","docs/homepage/encyclopedia/hair-color/consultation/19-proposal-limitations.md"),("Review feasibility criteria and what can be said independently versus specialist referral."), "Evidence-backed feasibility criteria; no formula/outcome oracle."),
    ReviewPackageTopic("SR11",("docs/homepage/encyclopedia/hair-color/consultation/16-regional-hair-state.md",),("Review regional capture fields and interpretation limits."), "Observed/reported data boundaries; no photo inference."),
    ReviewPackageTopic("SR12",("docs/homepage/encyclopedia/hair-color/consultation/15-service-history.md",),("Review service-history categories and compatibility stop conditions."), "Traceable product/service history and review limits."),
    ReviewPackageTopic("SR13",("docs/homepage/encyclopedia/hair-color/catalog/07-bijourka-catalog-identity-stabilization.md","docs/homepage/encyclopedia/hair-color/catalog/08-bijourka-19-series-structure.md","docs/homepage/encyclopedia/hair-color/consultation/35-rule-evidence-audit.md"),("Review identity and evidence requirements for product-specific claims."), "Exact identity and official evidence are required for product-specific claims."),
    ReviewPackageTopic("SR14",("docs/homepage/encyclopedia/hair-color/consultation/17-family-selection-logic.md","docs/homepage/encyclopedia/hair-color/consultation/18-option-selection-logic.md","docs/homepage/encyclopedia/hair-color/consultation/24-rejected-suggestion-control.md","docs/homepage/encyclopedia/hair-color/consultation/32-invalid-conflicting-options.md"),("Review goal-fit/technical validity ranking criteria and alternatives behavior."), "Valid evidence-backed candidate criteria and rank rationale."),
    ReviewPackageTopic("SR15",("docs/homepage/encyclopedia/hair-color/consultation/19-proposal-limitations.md","docs/homepage/encyclopedia/hair-color/consultation/28-gap-and-engine-failure-handling.md","docs/homepage/encyclopedia/hair-color/consultation/30-specialist-scenarios.md","docs/homepage/encyclopedia/hair-color/consultation/34-stop-failure-scenarios.md"),("Review safety, test, stop/referral criteria and manufacturer-instruction boundaries."), "Official safety/instruction evidence; no diagnosis or unsafe formula claims."),
)

@dataclass(frozen=True)
class PackageReadiness:
    status: str
    topic_ids: tuple[str,...]
    missing_topics: tuple[str,...]
    missing_documents: tuple[str,...]
    delivery_status: str
    message: str

def prepare_review_package()->PackageReadiness:
    ids=tuple(x.topic_id for x in PACKAGE_TOPICS)
    inventory_ids=tuple(x.topic_id for x in review_inventory())
    missing=tuple(x for x in inventory_ids if x not in ids)
    docs=tuple(dict.fromkeys(d for x in PACKAGE_TOPICS for d in x.document_refs))
    absent=()
    # Path verification is performed separately by the package build/repository audit.
    if missing or len(ids)!=len(set(ids)):
        return PackageReadiness("package_incomplete",ids,missing,absent,"not_sent","Review topic coverage incomplete.")
    return PackageReadiness("package_prepared",ids,(),absent,"prepared_not_sent",
        "Review package prepared with topic scope and document references; no specialist delivery or review is claimed.")

def review_package_topics()->tuple[ReviewPackageTopic,...]:
    return PACKAGE_TOPICS
