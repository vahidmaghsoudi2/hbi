from app.domain.hair_color_approved_corrections import CorrectionProposal, assess_correction

def p(**overrides):
    values=dict(correction_id="corr-1",topic_id="SR12",description="Clarify service-history rule",specialist_record_ref="review-1",
      evidence_refs=("e1",),specialist_accepted_within_scope=True,po_approved=True,po_approval_ref="PO-1",
      baseline_version="v1",target_version="v2",scope_note="history compatibility",apply_receipt="")
    values.update(overrides)
    return CorrectionProposal(**values)

def test_pending_specialist_blocks_correction():
    assert assess_correction(p(specialist_accepted_within_scope=False)).status=="pending_specialist_review"

def test_missing_po_approval_blocks_correction():
    assert assess_correction(p(po_approved=False,po_approval_ref="")).status=="pending_PO_approval"

def test_valid_approvals_prepare_but_do_not_claim_applied():
    assert assess_correction(p()).status=="approved_ready_to_apply"

def test_apply_receipt_required_for_applied_state():
    assert assess_correction(p(apply_receipt="commit-abc")).status=="applied_with_trace"

def test_same_version_rejected():
    assert assess_correction(p(target_version="v1")).status=="invalid_version_change"

def test_incomplete_proposal_rejected():
    assert assess_correction(p(evidence_refs=())).status=="incomplete_proposal"

def test_missing_scope_or_review_reference_rejected():
    assert assess_correction(p(scope_note="")).status=="incomplete_proposal"
    assert assess_correction(p(specialist_record_ref="")).status=="incomplete_proposal"

def test_invalid_object_fail_closed():
    assert assess_correction(None).status=="invalid_proposal"

def test_applied_state_receipt_does_not_claim_receipt_verified():
    assert "does not independently verify" in assess_correction(p(apply_receipt="commit")).message
