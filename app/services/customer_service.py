from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.services.base import BaseService
from datetime import datetime
import uuid


def _new_customer_id(prefix: str = "CUST") -> str:
    """شناسه یکتا حتی در ثبت‌های هم‌ثانیه (تست و گالری شلوغ)."""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:6]}"


def normalize_family_name(family_name: Optional[str]) -> str:
    """Normalize family name for identity comparison.

    Product rule: mobile is primary; family_name participates in match;
    given/first name does NOT affect identity decisions.
    Empty/missing family_name cannot confirm a match.
    """
    return " ".join((family_name or "").strip().split()).casefold()


def assert_mobile_identity_allows_bind(
    *,
    existing: Customer,
    incoming_family_name: Optional[str],
) -> None:
    """Raise if mobile-matched existing record must not be rebound.

    - Different family_name → conflict
    - Missing family_name on either side → cannot confirm; refuse silent rebind
    - First name is ignored
    """
    existing_fn = normalize_family_name(getattr(existing, "family_name", None))
    incoming_fn = normalize_family_name(incoming_family_name)
    if not existing_fn or not incoming_fn:
        raise ValueError(
            "Customer identity conflict: mobile matches an existing record but "
            "family_name is missing on one or both sides; silent rebind is not allowed"
        )
    if existing_fn != incoming_fn:
        raise ValueError(
            "Customer identity conflict: mobile matches an existing record but "
            "family_name differs; silent rebind is not allowed"
        )


class CustomerService(BaseService[Customer, CustomerRepository]):
    def __init__(self, db: Session):
        super().__init__(CustomerRepository(db), db)

    def find_by_mobile(self, mobile: str) -> Optional[Customer]:
        return self.repository.find_by_mobile(mobile)

    def find_by_name(self, name: str) -> List[Customer]:
        return self.repository.find_by_name(name)

    def get_with_cases(self, customer_id: str) -> Optional[Customer]:
        return self.repository.get_with_cases(customer_id)

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        return self.repository.get_by_id(customer_id)

    def register_customer(self, name: str, mobile: Optional[str] = None, **kwargs) -> Customer:
        if mobile:
            existing = self.find_by_mobile(mobile)
            if existing:
                raise ValueError(f"Customer with mobile {mobile} already exists")

        consent = kwargs.get("consent_to_store_data", 0)
        if consent not in (0, 1):
            raise ValueError("consent_to_store_data must be 0 or 1")

        if consent == 1 and "consent_date" not in kwargs:
            kwargs["consent_date"] = datetime.now()

        customer = self.create(
            customer_id=_new_customer_id("CUST"),
            name=name,
            mobile=mobile,
            **kwargs,
        )
        return customer

    def register_guest(self, name: str = "مهمان", **kwargs) -> Customer:
        """مشتری بدون موبایل — فروش/مشاوره سریع گالری."""
        kwargs.pop("mobile", None)
        consent = kwargs.get("consent_to_store_data", 0)
        if consent not in (0, 1):
            raise ValueError("consent_to_store_data must be 0 or 1")
        if consent == 1 and "consent_date" not in kwargs:
            kwargs["consent_date"] = datetime.now()
        return self.create(
            customer_id=_new_customer_id("CUST_GUEST"),
            name=name or "مهمان",
            mobile=None,
            **kwargs,
        )

    def record_intake(
        self,
        *,
        name: str,
        mobile: Optional[str] = None,
        concerns: Optional[str] = None,
        consent: int = 0,
        skin_profile: Optional[str] = None,
        guest: bool = False,
        family_name: Optional[str] = None,
    ) -> Customer:
        """ثبت سریع گالری: نام + موبایل/مهمان + نگرانی امروز + رضایت.

        Identity: mobile primary; family_name required to confirm same-person
        when mobile already exists. First name is not an identity key.
        """
        if consent not in (0, 1):
            raise ValueError("consent must be 0 or 1")

        fields: Dict[str, Any] = {}
        if concerns is not None:
            fields["concerns"] = concerns
        if skin_profile is not None:
            fields["skin_profile"] = skin_profile
        if family_name is not None:
            fields["family_name"] = family_name.strip() or None
        fields["consent_to_store_data"] = consent
        if consent == 1:
            fields["consent_date"] = datetime.now()

        if guest or not mobile:
            return self.register_guest(name=name, **fields)

        existing = self.find_by_mobile(mobile)
        if existing:
            assert_mobile_identity_allows_bind(
                existing=existing,
                incoming_family_name=family_name if family_name is not None else existing.family_name,
            )
            # Display name may update; identity was confirmed via mobile+family_name
            fields["name"] = name
            return self.repository.update(existing.customer_id, **fields) or existing

        return self.register_customer(
            name=name,
            mobile=mobile,
            family_name=(family_name.strip() if family_name else None),
            **{k: v for k, v in fields.items() if k != "family_name"},
        )

    def build_recommendation_profile(
        self,
        customer: Optional[Customer] = None,
        *,
        concerns: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """customer_profile برای RecommendationFacade.generate — قرارداد Qwen1."""
        profile: Dict[str, Any] = {}
        if customer is not None:
            if customer.skin_profile:
                profile["skin_profile"] = customer.skin_profile
            if customer.hair_profile:
                profile["hair_profile"] = customer.hair_profile
            if customer.scalp_profile:
                profile["scalp_profile"] = customer.scalp_profile
            if customer.age_range:
                profile["age_range"] = customer.age_range
            stored = customer.concerns
        else:
            stored = None

        if concerns is not None and concerns != "":
            profile["concerns"] = concerns
        elif stored:
            profile["concerns"] = stored
        else:
            profile["concerns"] = ""

        if extra:
            profile.update(extra)
        return profile
