"""ProfileFact implementation contract tests for the v0.1 schema gate."""
import pytest

from app.database import SessionLocal, init_db
from app.models.profile_fact import ProfileFact
from app.models.product_mutation_log import ProductMutationLog
from app.services.customer_service import CustomerService
from app.services.profile_fact_service import ProfileFactService


@pytest.fixture()
def db():
    init_db()
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def customer(db, consent=1):
    return CustomerService(db).register_guest(
        name="ProfileFact Test",
        consent_to_store_data=consent,
    )


def test_create_requires_consent(db):
    c = customer(db, consent=0)
    with pytest.raises(ValueError, match="consent"):
        ProfileFactService(db).create(
            customer_id=c.customer_id,
            authorized_customer_id=c.customer_id,
            attribute_key="skin_profile",
            value="چرب",
            actor_id=c.customer_id,
        )


def test_create_valid_fact_and_audit(db):
    c = customer(db)
    svc = ProfileFactService(db)
    fact = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="skin_profile",
        value="چرب",
        provenance="CUSTOMER",
        actor_id=c.customer_id,
        reason="customer-confirmed",
    )
    assert fact.status == "ACTIVE"
    assert fact.value_state == "KNOWN"

    logs = (
        db.query(ProductMutationLog)
        .filter(
            ProductMutationLog.target_entity == "ProfileFact",
            ProductMutationLog.target_id == fact.profile_fact_id,
        )
        .all()
    )
    assert len(logs) == 1
    assert logs[0].actor_id == c.customer_id
    assert logs[0].reason == "customer-confirmed"


def test_invalid_key_and_known_empty_value_rejected(db):
    c = customer(db)
    svc = ProfileFactService(db)
    with pytest.raises(ValueError, match="attribute_key"):
        svc.create(
            customer_id=c.customer_id,
            authorized_customer_id=c.customer_id,
            attribute_key="favorite_color",
            value="red",
            actor_id=c.customer_id,
        )
    with pytest.raises(ValueError, match="non-empty"):
        svc.create(
            customer_id=c.customer_id,
            authorized_customer_id=c.customer_id,
            attribute_key="skin_profile",
            value=" ",
            actor_id=c.customer_id,
        )


def test_non_known_state_may_have_no_value(db):
    c = customer(db)
    fact = ProfileFactService(db).create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="concerns",
        value=None,
        value_state="PREFER_NOT_TO_SAY",
        actor_id=c.customer_id,
    )
    assert fact.value is None


def test_supersession_is_same_customer_and_versioned(db):
    c1 = customer(db)
    c2 = customer(db)
    svc = ProfileFactService(db)
    first = svc.create(
        customer_id=c1.customer_id,
        authorized_customer_id=c1.customer_id,
        attribute_key="age_range",
        value="25-34",
        actor_id=c1.customer_id,
    )
    replacement = svc.supersede(
        fact_id=first.profile_fact_id,
        authorized_customer_id=c1.customer_id,
        value="35-44",
        value_state="KNOWN",
        provenance="CUSTOMER",
        actor_id=c1.customer_id,
        reason="customer-updated",
    )
    assert first.status == "SUPERSEDED"
    assert replacement.customer_id == c1.customer_id
    assert replacement.supersedes_fact_id == first.profile_fact_id

    with pytest.raises(ValueError, match="ownership"):
        svc.supersede(
            fact_id=first.profile_fact_id,
            authorized_customer_id=c2.customer_id,
            value="45-54",
            value_state="KNOWN",
            provenance="CUSTOMER",
            actor_id=c2.customer_id,
        )

    with pytest.raises(ValueError, match="ownership"):
        svc.supersede(
            fact_id=replacement.profile_fact_id,
            authorized_customer_id=c2.customer_id,
            value="45-54",
            value_state="KNOWN",
            provenance="CUSTOMER",
            actor_id=c2.customer_id,
        )


def test_supersede_requires_active_current_fact(db):
    c = customer(db)
    svc = ProfileFactService(db)
    first = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="skin_profile",
        value="خشک",
        actor_id=c.customer_id,
    )
    replacement = svc.supersede(
        fact_id=first.profile_fact_id,
        authorized_customer_id=c.customer_id,
        value="مختلط",
        value_state="KNOWN",
        provenance="CUSTOMER",
        actor_id=c.customer_id,
    )
    assert replacement.status == "ACTIVE"

    with pytest.raises(ValueError, match="ACTIVE"):
        svc.supersede(
            fact_id=first.profile_fact_id,
            authorized_customer_id=c.customer_id,
            value="چرب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            actor_id=c.customer_id,
        )


def test_revoke_is_audited(db):
    c = customer(db)
    svc = ProfileFactService(db)
    fact = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="concerns",
        value="لک",
        actor_id=c.customer_id,
    )
    svc.revoke(
        fact_id=fact.profile_fact_id,
        authorized_customer_id=c.customer_id,
        actor_id=c.customer_id,
        reason="customer-withdrew",
    )
    assert fact.status == "REVOKED"
    logs = (
        db.query(ProductMutationLog)
        .filter(ProductMutationLog.target_entity == "ProfileFact")
        .order_by(ProductMutationLog.timestamp.asc())
        .all()
    )
    assert [x.action for x in logs][-1] == "REVOKE"


def test_all_value_states_are_supported(db):
    c = customer(db)
    svc = ProfileFactService(db)
    for attribute_key, value_state in [
        ("skin_profile", "KNOWN"),
        ("hair_profile", "UNKNOWN"),
        ("scalp_profile", "PREFER_NOT_TO_SAY"),
        ("age_range", "NOT_APPLICABLE"),
    ]:
        fact = svc.create(
            customer_id=c.customer_id,
            authorized_customer_id=c.customer_id,
            attribute_key=attribute_key,
            value="value" if value_state == "KNOWN" else None,
            value_state=value_state,
            actor_id=c.customer_id,
        )
        assert fact.value_state == value_state


def test_invalid_provenance_and_status_are_rejected(db):
    c = customer(db)
    svc = ProfileFactService(db)
    with pytest.raises(ValueError, match="provenance"):
        svc.create(
            customer_id=c.customer_id,
            authorized_customer_id=c.customer_id,
            attribute_key="skin_profile",
            value="چرب",
            provenance="OTHER",
            actor_id=c.customer_id,
        )
    with pytest.raises(ValueError, match="status"):
        svc._validate_inputs("skin_profile", "چرب", "KNOWN", "CUSTOMER", "UNKNOWN")


def test_revoke_remains_possible_after_consent_withdrawal(db):
    c = customer(db)
    svc = ProfileFactService(db)
    fact = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="concerns",
        value="لک",
        actor_id=c.customer_id,
    )
    c.consent_to_store_data = 0
    svc.revoke(
        fact_id=fact.profile_fact_id,
        authorized_customer_id=c.customer_id,
        actor_id=c.customer_id,
        reason="consent-withdrawn",
    )
    assert fact.status == "REVOKED"


def test_list_active_excludes_revoked(db):
    c = customer(db)
    svc = ProfileFactService(db)
    active = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="skin_profile",
        value="خشک",
        actor_id=c.customer_id,
    )
    revoked = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="concerns",
        value="لک",
        actor_id=c.customer_id,
    )
    svc.revoke(
        fact_id=revoked.profile_fact_id,
        authorized_customer_id=c.customer_id,
        actor_id=c.customer_id,
        reason="test",
    )
    listed = svc.list_active(c.customer_id, c.customer_id)
    assert [x.profile_fact_id for x in listed] == [active.profile_fact_id]


def test_supersede_requires_consent(db):
    c = customer(db)
    svc = ProfileFactService(db)
    fact = svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="skin_profile",
        value="خشک",
        actor_id=c.customer_id,
    )
    c.consent_to_store_data = 0
    with pytest.raises(ValueError, match="consent"):
        svc.supersede(
            fact_id=fact.profile_fact_id,
            authorized_customer_id=c.customer_id,
            value="مختلط",
            value_state="KNOWN",
            provenance="CUSTOMER",
            actor_id=c.customer_id,
        )


def test_list_active_requires_consent(db):
    c = customer(db)
    svc = ProfileFactService(db)
    svc.create(
        customer_id=c.customer_id,
        authorized_customer_id=c.customer_id,
        attribute_key="skin_profile",
        value="خشک",
        actor_id=c.customer_id,
    )
    c.consent_to_store_data = 0
    with pytest.raises(ValueError, match="consent"):
        svc.list_active(c.customer_id, c.customer_id)
