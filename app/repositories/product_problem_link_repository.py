from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product_problem_link import ProductProblemLink
from app.models.product_problem_link_assessment_event import ProductProblemLinkAssessmentEvent


class ProductProblemLinkRepository:
    """Narrow append/read persistence surface; no update/delete operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> ProductProblemLink:
        record = ProductProblemLink(**fields)
        self.db.add(record)
        self.db.flush()
        return record

    def get_by_id(self, link_id: str) -> Optional[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(ProductProblemLink.link_id == link_id).first()

    def find_by_idempotency_key(self, key: str) -> Optional[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(ProductProblemLink.idempotency_key == key).first()

    def find_legacy_duplicate_scope(self, **scope) -> Optional[ProductProblemLink]:
        # Market is legacy metadata, not part of a consultation-link identity.
        scope.pop("market_region", None)
        return self.db.query(ProductProblemLink).filter_by(
            **scope, assertion_key=None
        ).first()

    def find_successor(self, link_id: str) -> Optional[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(
            ProductProblemLink.supersedes_link_id == link_id
        ).order_by(ProductProblemLink.created_at.asc()).first()

    def find_by_assertion_revision(self, assertion_key: str, revision_no: int):
        return self.db.query(ProductProblemLink).filter_by(
            assertion_key=assertion_key, revision_no=revision_no
        ).first()

    def latest_for_assertion(self, assertion_key: str):
        return (
            self.db.query(ProductProblemLink)
            .filter(ProductProblemLink.assertion_key == assertion_key)
            .order_by(ProductProblemLink.revision_no.desc())
            .first()
        )

    def list_by_product(self, product_id: str) -> List[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(
            ProductProblemLink.product_id == product_id
        ).order_by(ProductProblemLink.created_at.asc(), ProductProblemLink.link_id.asc()).all()

    def list_by_problem(self, problem_id: str) -> List[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(
            ProductProblemLink.problem_id == problem_id
        ).order_by(ProductProblemLink.created_at.asc(), ProductProblemLink.link_id.asc()).all()

    def list_assertion_revisions(self, assertion_key: str) -> List[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(
            ProductProblemLink.assertion_key == assertion_key
        ).order_by(ProductProblemLink.revision_no.asc()).all()

    def append_event(self, **fields):
        event = ProductProblemLinkAssessmentEvent(**fields)
        self.db.add(event)
        self.db.flush()
        return event

    def list_events(self, link_ids: list[str]):
        if not link_ids:
            return []
        return self.db.query(ProductProblemLinkAssessmentEvent).filter(
            ProductProblemLinkAssessmentEvent.link_id.in_(link_ids)
        ).order_by(ProductProblemLinkAssessmentEvent.timestamp.asc(),
                   ProductProblemLinkAssessmentEvent.event_id.asc()).all()

    def list_latest_candidate_rows(self, problem_id: str):
        """Return current CANDIDATE revisions joined to their Product and Evidence.

        Superseded revisions are never surfaced. Legacy unversioned rows are
        included only when they have no successor assessment.
        """
        from sqlalchemy import and_, exists, func, or_, select
        from sqlalchemy.orm import aliased

        from app.models.evidence import Evidence
        from app.models.product import Product

        current = ProductProblemLink
        revision = aliased(ProductProblemLink)
        latest_revision_no = (
            select(func.max(revision.revision_no))
            .where(revision.assertion_key == current.assertion_key)
            .correlate(current)
            .scalar_subquery()
        )
        has_successor = exists(
            select(1).where(ProductProblemLink.supersedes_link_id == current.link_id)
        )
        current_revision = or_(
            and_(
                current.assertion_key.is_not(None),
                current.revision_no == latest_revision_no,
            ),
            and_(current.assertion_key.is_(None), ~has_successor),
        )
        return (
            self.db.query(current, Product, Evidence)
            .join(Product, Product.product_id == current.product_id)
            .join(Evidence, Evidence.evidence_id == current.evidence_id)
            .filter(
                current.problem_id == problem_id,
                current.relationship_status == "CANDIDATE",
                current.problem_map_version == "SKIN_PROBLEM_SPACE_MAP_V0.1",
                current_revision,
            )
            .order_by(current.created_at.desc(), current.link_id.asc())
            .all()
        )
