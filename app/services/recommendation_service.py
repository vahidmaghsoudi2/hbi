import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.models.case import Case
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.evidence import Evidence
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_knowledge_repository import ProductKnowledgeRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.services.base import BaseService
from app.services.need_normalization import normalize_needs_from_factors, CANONICAL_NEEDS
from app.services.product_compatibility import product_compatibility_ids
from app.reasoning.reasoning_engine import ReasoningEngine
from app.reasoning.conflict_analyzer import ConflictSeverity

logger = logging.getLogger(__name__)

NEED_MATCH_SUFFICIENT = 0.40
