from typing import Optional
from sqlalchemy.orm import Session
from app.models.product_knowledge import ProductKnowledge
from app.repositories.base import BaseRepository


class ProductKnowledgeRepository(BaseRepository[ProductKnowledge]):
    def __init__(self, db: Session):
        super().__init__(ProductKnowledge, db)

    def find_by_product(self, product_id: str) -> Optional[ProductKnowledge]:
        return self.db.query(ProductKnowledge).filter(
            ProductKnowledge.product_id == product_id
        ).first()

    def update_knowledge(self, product_id: str, **fields) -> Optional[ProductKnowledge]:
        knowledge = self.find_by_product(product_id)
        if not knowledge:
            return None
        for key, value in fields.items():
            if hasattr(knowledge, key) and value is not None:
                setattr(knowledge, key, value)
        self.db.flush()
        return knowledge
