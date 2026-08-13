from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Repository پایه با عملیات CRUD عمومی"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.flush()
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create {self.model.__name__}: {e}")

    def get_by_id(self, id: str) -> Optional[ModelType]:
        pk_column = self.model.__table__.primary_key.columns[0]
        return self.db.query(self.model).filter(pk_column == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            self.db.flush()
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update {self.model.__name__}: {e}")

    def delete(self, id: str) -> bool:
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            self.db.delete(instance)
            self.db.flush()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete {self.model.__name__}: {e}")

    def count(self) -> int:
        return self.db.query(self.model).count()

    def filter_by(self, **kwargs) -> List[ModelType]:
        return self.db.query(self.model).filter_by(**kwargs).all()
