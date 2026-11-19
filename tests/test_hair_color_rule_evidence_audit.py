from app.domain.hair_color_rule_evidence_audit import EvidenceAuditInput, audit_rule_evidence

def test_owner_rule_is_owner_defined_not_scientific():
    a=audit_rule_evidence(EvidenceAuditInput("r1","owner_defined","owner_decision","decision-1"))
    assert a.status=="owner_defined_not_scientific" and a.claim_allowed

def test_catalog_identity_does_not_support_chemistry():
    a=audit_rule_evidence(EvidenceAuditInput("r2","catalog_identity","catalog_snapshot","catalog-1"))
    assert a.status=="identity_only"

def test_product_claim_requires_exact_identity_official_doc_and_review():
    a=audit_rule_evidence(EvidenceAuditInput("r3","product_specific","official_document","doc-1",True,True,"high"))
    assert a.status=="supported_for_review"

def test_product_claim_without_exact_identity_blocked():
    a=audit_rule_evidence(EvidenceAuditInput("r3","product_specific","official_document","doc-1",False,True,"high"))
    assert not a.claim_allowed and a.status=="product_evidence_pending"

def test_product_claim_without_specialist_review_blocked():
    a=audit_rule_evidence(EvidenceAuditInput("r3","product_specific","official_document","doc-1",True,False,"high"))
    assert a.status=="awaiting_specialist_review"

def test_general_scientific_claim_requires_credible_source_and_review():
    a=audit_rule_evidence(EvidenceAuditInput("r4","general_scientific","scientific_source","paper-1",False,True,"high"))
    assert a.status=="supported_for_review"

def test_general_claim_low_quality_blocked():
    a=audit_rule_evidence(EvidenceAuditInput("r4","general_scientific","social_observation","post-1",False,True,"low"))
    assert a.status=="evidence_quality_unverified"

def test_specialist_rule_requires_review_source():
    a=audit_rule_evidence(EvidenceAuditInput("r5","specialist_rule","scientific_source","source-1",False,False,"high"))
    assert a.status=="awaiting_specialist_review"

def test_anecdote_is_signal_only():
    a=audit_rule_evidence(EvidenceAuditInput("r6","anecdotal","social_observation","post-1"))
    assert a.status=="anecdotal_signal_only" and not a.claim_allowed

def test_missing_reference_blocks_claim():
    a=audit_rule_evidence(EvidenceAuditInput("r7","general_scientific","scientific_source",""))
    assert a.status=="evidence_pending" and not a.claim_allowed

def test_source_mismatch_blocked():
    a=audit_rule_evidence(EvidenceAuditInput("r8","catalog_identity","owner_decision","decision-1"))
    assert a.status=="source_mismatch"

def test_invalid_record_fail_closed():
    assert audit_rule_evidence(None).status=="invalid_input"
