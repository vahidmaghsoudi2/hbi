from app.domain.hair_color_final_knowledge_document import knowledge_document_status, required_sections

def test_final_document_registry_pending_specialist_review():
    a=knowledge_document_status()
    assert a.status=="documented_pending_specialist_review"
    assert not a.customer_use_allowed and a.specialist_approval_required

def test_document_registry_has_all_thirteen_sections():
    assert len(required_sections())==13

def test_status_is_not_product_or_runtime_readiness():
    assert knowledge_document_status().customer_use_allowed is False
