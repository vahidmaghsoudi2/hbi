from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.product_problem_link import ProductProblemLink


class ProductProblemLinkRepository:
    """Narrow persistence surface; no generic update/delete operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> ProductProblemLink:
        record = ProductProblemLink(**fields)
        self.db.add(record)
        self.db.flush()
        return record

    def find_duplicate_scope(self, **scope) -> Optional[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter_by(**scope).first()

    def get_by_id(self, link_id: str) -> Optional[ProductProblemLink]:
        return self.db.query(ProductProblemLink).filter(
            ProductProblemLink.link_id == link_id
        ).first()

    def list_by_product(self, product_id: str) -> List[ProductProblemLink]:
        return (
            self.db.query(ProductProblemLink)
            .filter(ProductProblemLink.product_id == product_id)
            .order_by(ProductProblemLink.created_at.asc(), ProductProblemLink.link_id.asc())
            .all()
        )

    def list_by_problem(self, problem_id: str) -> List[ProductProblemLink]:
        return (
            self.db.query(ProductProblemLink)
            .filter(ProductProblemLink.problem_id == problem_id)
            .order_by(ProductProblemLink.created_at.asc(), ProductProblemLink.link_id.asc())
            .all()
        )
