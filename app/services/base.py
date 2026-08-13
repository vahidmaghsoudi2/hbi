from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType, db: Session):
        self.repository = repository
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.repository.get_by_id(id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.repository.get_all(skip, limit)

    def create(self, **kwargs) -> ModelType:
        return self.repository.create(**kwargs)

    def update(self, id: str, **kwargs) -> Optional[ModelType]:
        return self.repository.update(id, **kwargs)

    def delete(self, id: str) -> bool:
        return self.repository.delete(id)

    def count(self) -> int:
        return self.repository.count()
