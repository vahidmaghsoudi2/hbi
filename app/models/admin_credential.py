from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlalchemy.sql import func

from app.models.base import Base


class AdminCredential(Base):
    __tablename__ = "AdminCredential"

    credential_id = Column(String, primary_key=True)
    subject_id = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (UniqueConstraint("subject_id", "username", name="uq_admincredential_subject_username"),)
