import os
import uuid

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.admin_credential import AdminCredential
from app.models.user_role import UserRole, ROLE_ADMIN


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def configured_admin_credentials() -> tuple[str, str] | None:
    username = os.getenv("HBI_ADMIN_USERNAME")
    password = os.getenv("HBI_ADMIN_PASSWORD")
    if not username or not password:
        return None
    return username.strip(), password


def ensure_admin_account(db: Session) -> AdminCredential | None:
    configured = configured_admin_credentials()
    if configured is None:
        return None
    username, password = configured
    subject_id = os.getenv("HBI_ADMIN_SUBJECT", "USR_ADMIN")
    credential = db.query(AdminCredential).filter(AdminCredential.username == username).first()
    if credential is None:
        credential = AdminCredential(
            credential_id=f"ADMIN-CRED-{uuid.uuid4().hex[:12]}",
            subject_id=subject_id,
            username=username,
            password_hash=pwd_context.hash(password),
        )
        db.add(credential)
    else:
        credential.subject_id = subject_id
    role = db.query(UserRole).filter(
        UserRole.subject_id == subject_id,
        UserRole.role == ROLE_ADMIN,
    ).first()
    if role is None:
        db.add(UserRole(
            user_role_id=f"UR-{subject_id}-{ROLE_ADMIN}",
            subject_id=subject_id,
            role=ROLE_ADMIN,
        ))
    db.commit()
    return credential


def verify_admin_password(credential: AdminCredential, password: str) -> bool:
    return pwd_context.verify(password, credential.password_hash)
