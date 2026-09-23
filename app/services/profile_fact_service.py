"""Business rules for versioned customer Profile Facts."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.profile_fact import (
    PROFILE_FACT_KEYS,
    PROVENANCES,
    STATUSES,
    VALUE_STATES,
    ProfileFact,
)
from app.services.mutation_log_service import MutationLogService


class ProfileFactService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = MutationLogService(db)

    def _get(self, fact_id: str) -> ProfileFact:
        fact = self.db.get(ProfileFact, fact_id)
        if fact is None:
            raise ValueError("ProfileFact not found")
        return fact

    def _require_customer_consent(self, customer_id: str) -> None:
        from app.models.customer import Customer
        customer = self.db.get(Customer, customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        if customer.consent_to_store_data != 1:
            raise ValueError("Customer consent is required for ProfileFact storage")

    @staticmethod
    def _validate_inputs(attribute_key: str, value: Optional[str], value_state: str,
                         provenance: str, status: str) -> None:
        if attribute_key not in PROFILE_FACT_KEYS:
            raise ValueError("Unsupported ProfileFact attribute_key")
        if value_state not in VALUE_STATES:
            raise ValueError("Invalid ProfileFact value_state")
        if provenance not in PROVENANCES:
            raise ValueError("Invalid ProfileFact provenance")
        if status not in STATUSES:
            raise ValueError("Invalid ProfileFact status")
        if value_state == "KNOWN" and (value is None or not str(value).strip()):
            raise ValueError("KNOWN ProfileFact requires a non-empty value")

    @staticmethod
    def _snapshot(fact: ProfileFact) -> dict[str, Any]:
        return {
            "profile_fact_id": fact.profile_fact_id,
            "customer_id": fact.customer_id,
            "attribute_key": fact.attribute_key,
            "value": fact.value,
            "value_state": fact.value_state,
            "provenance": fact.provenance,
            "status": fact.status,
            "supersedes_fact_id": fact.supersedes_fact_id,
        }

    def create(
        self,
        *,
        customer_id: str,
        authorized_customer_id: str,
        attribute_key: str,
        value: Optional[str],
        value_state: str = "KNOWN",
        provenance: str = "CUSTOMER",
        actor_id: str,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> ProfileFact:
        if authorized_customer_id != customer_id:
            raise ValueError("Customer ownership mismatch")
        self._require_customer_consent(customer_id)
        self._validate_inputs(attribute_key, value, value_state, provenance, "ACTIVE")

        fact = ProfileFact(
            profile_fact_id=f"PF-{uuid.uuid4().hex}",
            customer_id=customer_id,
            attribute_key=attribute_key,
            value=value.strip() if isinstance(value, str) else value,
            value_state=value_state,
            provenance=provenance,
            status="ACTIVE",
        )
        self.db.add(fact)
        self.db.flush()

        self.audit.append(
            actor_id=actor_id,
            actor_role=actor_role,
            action="CREATE",
            target_entity="ProfileFact",
            target_id=fact.profile_fact_id,
            before=None,
            after=self._snapshot(fact),
            reason=reason,
            resulting_state="ACTIVE",
        )
        return fact

    def supersede(
        self,
        *,
        fact_id: str,
        authorized_customer_id: str,
        value: Optional[str],
        value_state: str,
        provenance: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> ProfileFact:
        current = self._get(fact_id)
        if authorized_customer_id != current.customer_id:
            raise ValueError("Customer ownership mismatch")
        self._require_customer_consent(current.customer_id)
        if current.status != "ACTIVE":
            raise ValueError("Only ACTIVE ProfileFact can be superseded")
        self._validate_inputs(current.attribute_key, value, value_state, provenance, "ACTIVE")

        before = self._snapshot(current)
        replacement = ProfileFact(
            profile_fact_id=f"PF-{uuid.uuid4().hex}",
            customer_id=current.customer_id,
            attribute_key=current.attribute_key,
            value=value.strip() if isinstance(value, str) else value,
            value_state=value_state,
            provenance=provenance,
            status="ACTIVE",
            supersedes_fact_id=current.profile_fact_id,
        )
        current.status = "SUPERSEDED"
        self.db.add(replacement)
        self.db.flush()

        self.audit.append(
            actor_id=actor_id,
            actor_role=actor_role,
            action="SUPERSEDE",
            target_entity="ProfileFact",
            target_id=replacement.profile_fact_id,
            before=before,
            after=self._snapshot(replacement),
            reason=reason,
            resulting_state="ACTIVE",
        )
        return replacement

    def revoke(
        self,
        *,
        fact_id: str,
        authorized_customer_id: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> ProfileFact:
        fact = self._get(fact_id)
        if authorized_customer_id != fact.customer_id:
            raise ValueError("Customer ownership mismatch")
        before = self._snapshot(fact)
        fact.status = "REVOKED"
        self.db.flush()

        self.audit.append(
            actor_id=actor_id,
            actor_role=actor_role,
            action="REVOKE",
            target_entity="ProfileFact",
            target_id=fact.profile_fact_id,
            before=before,
            after=self._snapshot(fact),
            reason=reason,
            resulting_state="REVOKED",
        )
        return fact

    def list_active(self, customer_id: str, authorized_customer_id: str) -> list[ProfileFact]:
        if authorized_customer_id != customer_id:
            raise ValueError("Customer ownership mismatch")
        self._require_customer_consent(customer_id)
        return (
            self.db.query(ProfileFact)
            .filter(
                ProfileFact.customer_id == customer_id,
                ProfileFact.status == "ACTIVE",
            )
            .order_by(ProfileFact.created_at.asc())
            .all()
        )
