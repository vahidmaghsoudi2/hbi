"""Final hair-color knowledge document registry and readiness boundary."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class KnowledgeDocumentStatus:
    document_id: str
    title: str
    status: str
    customer_use_allowed: bool
    specialist_approval_required: bool

STATUS=KnowledgeDocumentStatus(
    "HC-KNOWLEDGE-40",
    "Final HBI Hair-Color Consultation Knowledge Synthesis",
    "documented_pending_specialist_review",
    False,
    True,
)

REQUIRED_SECTIONS=(
    "1. هدف و وضعیت اعتبار",
    "2. مبانی رنگ و اصطلاحات",
    "3. کاتالوگ و هویت محصول",
    "4. ورودی‌های مشاوره",
    "5. Evidence & knowledge controls",
    "6. Consultation routing",
    "7. Option rules",
    "8. Workflow and client-decision controls",
    "9. Specialist-review status",
    "10. Corrections and release authority",
    "11. Explicitly prohibited claims/behavior at this stage",
    "12. Readiness summary",
    "13. Source documents in this roadmap",
)

def knowledge_document_status()->KnowledgeDocumentStatus:
    return STATUS

def required_sections()->tuple[str,...]:
    return REQUIRED_SECTIONS
