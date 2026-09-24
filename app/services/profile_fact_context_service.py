"""Single read/projection boundary for ProfileFact-backed consultation context."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.customer import Customer
from app.models.profile_fact import PROFILE_FACT_KEYS, ProfileFact


CONTEXT_KEYS = frozenset({"skin_profile", "concerns"})
TRUSTED_STATUS = "ACTIVE"
UNKNOWN_STATES = frozenset({"UNKNOWN", "PREFER_NOT_TO_SAY", "NOT_APPLICABLE"})


class ProfileFactContextService:
    """Build the read-only consultation profile without changing ProfileFact state."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None or value == "":
            return False
        if isinstance(value, (list, tuple, set)):
            return any(str(item).strip() for item in value)
        return bool(str(value).strip())

    @staticmethod
    def _trace_entry(*, source: str, value: Any = None, fact_id: Optional[str] = None,
                     value_state: Optional[str] = None, provenance: Optional[str] = None) -> Dict[str, Any]:
        entry: Dict[str, Any] = {"source": source}
        if value is not None:
            entry["value"] = value
        if fact_id is not None:
            entry["profile_fact_id"] = fact_id
        if value_state is not None:
            entry["value_state"] = value_state
        if provenance is not None:
            entry["provenance"] = provenance
        return entry

    def build(self, case: Case, current_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        customer = self.db.get(Customer, case.customer_id)
        if customer is None:
            raise ValueError("Customer not found")

        current = dict(current_input or {})
        profile: Dict[str, Any] = {}
        trace: Dict[str, Any] = {
            "version": "1",
            "sources": {},
            "excluded": [],
            "conflicts": [],
            "unknowns": [],
        }

        legacy = {
            "skin_profile": getattr(customer, "skin_profile", None),
            "concerns": getattr(customer, "concerns", None),
        }

        facts = []
        if customer.consent_to_store_data == 1:
            facts = (
                self.db.query(ProfileFact)
                .filter(
                    ProfileFact.customer_id == case.customer_id,
                    ProfileFact.attribute_key.in_(CONTEXT_KEYS),
                )
                .order_by(ProfileFact.created_at.asc(), ProfileFact.profile_fact_id.asc())
                .all()
            )
        else:
            trace["excluded"].append({
                "customer_id": case.customer_id,
                "reason": "customer_consent_not_active",
            })
        active_by_key: Dict[str, list[ProfileFact]] = {key: [] for key in CONTEXT_KEYS}
        for fact in facts:
            if fact.status != TRUSTED_STATUS:
                trace["excluded"].append({
                    "profile_fact_id": fact.profile_fact_id,
                    "attribute_key": fact.attribute_key,
                    "status": fact.status,
                    "reason": "non_trusted_lifecycle_state",
                })
                continue
            active_by_key[fact.attribute_key].append(fact)

        for key in CONTEXT_KEYS:
            current_value = current.get(key)
            if self._present(current_value):
                profile[key] = current_value
                trace["sources"][key] = self._trace_entry(
                    source="CURRENT_CONSULTATION",
                    value=current_value,
                )
                continue

            active = active_by_key[key]
            if len(active) > 1:
                conflict = {
                    "attribute_key": key,
                    "state": "CONFLICTED",
                    "profile_fact_ids": [fact.profile_fact_id for fact in active],
                    "values": [fact.value for fact in active],
                    "provenances": [fact.provenance for fact in active],
                }
                trace["conflicts"].append(conflict)
                trace["sources"][key] = {
                    "source": "PROFILE_FACT",
                    "value_state": "CONFLICTED",
                    "profile_fact_ids": conflict["profile_fact_ids"],
                }
                continue

            if len(active) == 1:
                fact = active[0]
                if fact.value_state == "KNOWN":
                    profile[key] = fact.value
                    trace["sources"][key] = self._trace_entry(
                        source="PROFILE_FACT",
                        value=fact.value,
                        fact_id=fact.profile_fact_id,
                        value_state=fact.value_state,
                        provenance=fact.provenance,
                    )
                elif fact.value_state in UNKNOWN_STATES:
                    trace["unknowns"].append({
                        "attribute_key": key,
                        "value_state": fact.value_state,
                        "profile_fact_id": fact.profile_fact_id,
                        "provenance": fact.provenance,
                    })
                    trace["sources"][key] = self._trace_entry(
                        source="PROFILE_FACT",
                        fact_id=fact.profile_fact_id,
                        value_state=fact.value_state,
                        provenance=fact.provenance,
                    )
                continue

            if self._present(legacy[key]):
                profile[key] = legacy[key]
                trace["sources"][key] = self._trace_entry(
                    source="CUSTOMER_LEGACY",
                    value=legacy[key],
                )

        for key, value in current.items():
            if key not in CONTEXT_KEYS and self._present(value):
                profile[key] = value

        profile["customer_id"] = case.customer_id
        profile["_profile_fact_context"] = trace
        return profile
