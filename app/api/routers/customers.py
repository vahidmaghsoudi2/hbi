from typing import Optional, Any, Dict, List
from collections import defaultdict
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_customer_id
from app.core.authorization import require_any_role, get_roles_for_subject
from app.models.user_role import ROLE_EDITOR, ROLE_ADMIN, ROLE_PO
from app.core.audit import audit_event
from app.interface.facades import CustomerFacade
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.feedback_service import FeedbackService
from app.models.case import Case


router = APIRouter()

# Managerial roles for customer lookup (owner Admin + pilot Editor/PO).
_MANAGERIAL_LOOKUP = (ROLE_EDITOR, ROLE_ADMIN, ROLE_PO)

# Public guest bootstrap rate limit (process-local; Pilot hardening)
_guest_rate_limit: Dict[str, List[float]] = defaultdict(list)
_GUEST_RATE_WINDOW = 60  # seconds
_GUEST_RATE_MAX = 10
