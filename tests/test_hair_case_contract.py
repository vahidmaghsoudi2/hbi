"""Synthetic-only conformance tests for the HBI case and event contract."""
from dataclasses import replace

import pytest

from app.domain.hair_case_contract import (
    CaseEvent,
    DependencyRef,
    EventType,
    FactRecord,
    HairCaseRecord,
    HairEvaluationRun,
    KnowledgeState,
    SourceClass,
    SuggestionVersionRef,
    WORKFLOW_STATES,
    WorkflowControl,
    append_case_event,
    assess_dependency_changes,
    evaluation_matches_current_case,
)


def _fact(**overrides):
    values = {
        "fact_id": "SYNTHETIC-FACT-001",
        "field_key": "hair_history",
        "value": False,
        "knowledge_state": KnowledgeState.KNOWN,
        "source_class": SourceClass.CLIENT_REPORTED,
        "source_ref": "synthetic://case/fact-001",
        "recorded_at": "2026-11-15T10:00:00Z",
        "recorded_by": "SYNTHETIC-ACTOR-CLIENT",
    }
    values.update(overrides)
    return FactRecord(**values)


def _case(**overrides):
    values = {
        "case_id": "SYNTHETIC-CASE-001",
        "case_version": "case-v1",
        "target_version": "target-v1",
        "workflow_state": WORKFLOW_STATES[1],
        "facts": (_fact(),),
    }
    values.update(overrides)
    return HairCaseRecord(**values)


def _run(**overrides):
    values = {
        "run_id": "SYNTHETIC-RUN-001",
        "request_id": "SYNTHETIC-REQUEST-001",
        "case_id": "SYNTHETIC-CASE-001",
        "case_version": "case-v1",
        "target_version": "target-v1",
        "contract_version": "1.0",
        "engine_version": "synthetic-test",
        "started_at": "2026-11-15T10:00:00Z",
        "completed_at": "2026-11-15T10:00:01Z",
        "dependencies": (DependencyRef("CASE", "SYNTHETIC-CASE-001", "case-v1"),),
        "outcome": "SUCCESS",
    }
    values.update(overrides)
    return HairEvaluationRun(**values)


def _event(
    event_type,
    *,
    event_id="SYNTHETIC-EVENT-001",
    suggestion=None,
    payload=(),
    actor_kind="CLIENT",
):
    if event_type == EventType.QUESTION_ASKED and not payload:
        payload = (("question_ref", "SYNTHETIC-QUESTION-001"),)
    return CaseEvent(
        event_id=event_id,
        case_id="SYNTHETIC-CASE-001",
        case_version="case-v1",
        target_version="target-v1",
        event_type=event_type,
        actor_ref=f"SYNTHETIC-ACTOR-{actor_kind}",
        actor_kind=actor_kind,
        occurred_at="2026-11-15T10:00:00Z",
        correlation_ref="SYNTHETIC-CORRELATION-001",
        suggestion=suggestion,
        payload=payload,
    )


def _suggestion():
    return SuggestionVersionRef("SYNTHETIC-SUGGESTION-001", "suggestion-v1")


def test_known_false_is_valid_but_unknown_cannot_carry_a_value():
    assert _fact(value=False).value is False
    with pytest.raises(ValueError, match="Non-KNOWN facts"):
        _fact(value=False, knowledge_state=KnowledgeState.UNKNOWN)


def test_known_fact_requires_value():
    with pytest.raises(ValueError, match="KNOWN facts require a value"):
        _fact(value=None)


def test_conflict_requires_a_conflict_group_reference():
    with pytest.raises(ValueError, match="conflict_group_ref"):
        _fact(value=None, knowledge_state=KnowledgeState.CONFLICT)
    fact = _fact(
        value=None,
        knowledge_state=KnowledgeState.CONFLICT,
        conflict_group_ref="SYNTHETIC-CONFLICT-001",
    )
    assert fact.knowledge_state == KnowledgeState.CONFLICT


def test_fact_correction_keeps_explicit_supersedes_lineage():
    fact = _fact(
        fact_id="SYNTHETIC-FACT-002",
        supersedes_fact_id="SYNTHETIC-FACT-001",
    )
    assert fact.supersedes_fact_id == "SYNTHETIC-FACT-001"


def test_case_requires_synthetic_identity_and_approved_workflow_state():
    with pytest.raises(ValueError, match="synthetic identifier"):
        _case(case_id="REAL-CASE-001")
    with pytest.raises(ValueError, match="ten approved states"):
        _case(workflow_state="CLIENT_STOPPED")


def test_case_rejects_duplicate_fact_identifiers():
    with pytest.raises(ValueError, match="unique within"):
        _case(facts=(_fact(), _fact()))


def test_exact_ten_workflow_states_are_preserved():
    assert len(WORKFLOW_STATES) == 10
    assert len(set(WORKFLOW_STATES)) == 10


def test_run_is_current_only_for_exact_case_and_target_version_pair():
    run = _run()
    assert evaluation_matches_current_case(run, _case()) is True
    assert evaluation_matches_current_case(run, _case(target_version="target-v2")) is False
    assert evaluation_matches_current_case(run, _case(case_version="case-v2")) is False


def test_failed_run_is_never_current():
    run = _run(outcome="ENGINE_FAIL")
    assert evaluation_matches_current_case(run, _case()) is False


def test_run_cannot_enable_display_or_recommendations():
    with pytest.raises(ValueError, match="COMPUTED_ONLY"):
        _run(display_allowed=True)
    with pytest.raises(ValueError, match="does not permit recommendations"):
        _run(recommendation={"formula": "prohibited"})


def test_unchanged_dependencies_preserve_computed_result():
    dep = DependencyRef("CASE", "SYNTHETIC-CASE-001", "case-v1")
    result = assess_dependency_changes((dep,), (dep,), {})
    assert result.status == "PRESERVE"
    assert result.changed_dependencies == ()


def test_unknown_dependency_impact_fails_closed():
    old = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v1"),)
    new = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v2"),)
    result = assess_dependency_changes(old, new, {})
    assert result.status == "UNRESOLVED"
    assert result.unresolved_dependencies == ("RULE:SYNTHETIC-RULE-001",)


def test_explicit_effective_dependency_change_invalidates():
    old = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v1"),)
    new = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v2"),)
    result = assess_dependency_changes(
        old, new, {"RULE:SYNTHETIC-RULE-001": "EFFECTIVE"}
    )
    assert result.status == "INVALIDATE"


def test_explicit_non_effective_change_preserves_only_computation():
    old = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v1"),)
    new = (DependencyRef("RULE", "SYNTHETIC-RULE-001", "v2"),)
    result = assess_dependency_changes(
        old, new, {"RULE:SYNTHETIC-RULE-001": "NON_EFFECTIVE"}
    )
    assert result.status == "PRESERVE"


def test_added_or_removed_dependency_without_impact_is_unresolved():
    old = (DependencyRef("CASE", "SYNTHETIC-CASE-001", "v1"),)
    new = (
        DependencyRef("CASE", "SYNTHETIC-CASE-001", "v1"),
        DependencyRef("EVIDENCE", "SYNTHETIC-EVIDENCE-001", "v1"),
    )
    result = assess_dependency_changes(old, new, {})
    assert result.status == "UNRESOLVED"
    assert result.unresolved_dependencies == ("EVIDENCE:SYNTHETIC-EVIDENCE-001",)


def test_question_event_appends_without_changing_workflow_control():
    question = _event(EventType.QUESTION_ASKED)
    result = append_case_event((), question)
    assert result.events == (question,)
    assert result.workflow_control == WorkflowControl()


def test_duplicate_event_id_is_rejected():
    event = _event(EventType.QUESTION_ASKED)
    with pytest.raises(ValueError, match="duplicate event_id"):
        append_case_event((event,), replace(event, event_type=EventType.CASE_DATA_CHANGED))


def test_event_history_cannot_mix_cases():
    first = _event(EventType.QUESTION_ASKED)
    second = replace(first, event_id="SYNTHETIC-EVENT-002", case_id="SYNTHETIC-CASE-002")
    with pytest.raises(ValueError, match="one synthetic case"):
        append_case_event((first,), second)


def test_acceptance_does_not_imply_execution_consent():
    accepted = _event(
        EventType.SUGGESTION_ACCEPTED,
        suggestion=_suggestion(),
    )
    result = append_case_event((), accepted)
    assert result.events == (accepted,)
    assert not any(
        item.event_type == EventType.EXECUTION_CONSENT_GIVEN
        for item in result.events
    )


def test_rejected_suggestion_version_cannot_be_accepted_later():
    rejected = _event(
        EventType.SUGGESTION_REJECTED,
        suggestion=_suggestion(),
    )
    with pytest.raises(ValueError, match="can never be accepted again"):
        append_case_event((rejected,), _event(
            EventType.SUGGESTION_ACCEPTED,
            event_id="SYNTHETIC-EVENT-002",
            suggestion=_suggestion(),
        ))


def test_execution_consent_requires_prior_acceptance_of_exact_version():
    consent = _event(
        EventType.EXECUTION_CONSENT_GIVEN,
        suggestion=_suggestion(),
    )
    with pytest.raises(ValueError, match="prior acceptance"):
        append_case_event((), consent)
    accepted = _event(
        EventType.SUGGESTION_ACCEPTED,
        suggestion=_suggestion(),
    )
    result = append_case_event((accepted,), consent)
    assert result.events[-1] == consent


def test_service_execution_requires_review_acceptance_and_separate_consent():
    suggestion = _suggestion()
    accepted = _event(EventType.SUGGESTION_ACCEPTED, suggestion=suggestion)
    consent = _event(
        EventType.EXECUTION_CONSENT_GIVEN,
        event_id="SYNTHETIC-EVENT-002",
        suggestion=suggestion,
    )
    reviewed = _event(
        EventType.SPECIALIST_REVIEW_RECORDED,
        event_id="SYNTHETIC-EVENT-003",
        suggestion=suggestion,
        payload=(
            ("review_ref", "SYNTHETIC-REVIEW-001"),
            ("decision", "APPROVED"),
        ),
        actor_kind="SPECIALIST",
    )
    started = _event(
        EventType.SERVICE_EXECUTION_STARTED,
        event_id="SYNTHETIC-EVENT-004",
        suggestion=suggestion,
        payload=(("service_record_ref", "SYNTHETIC-SERVICE-001"),),
        actor_kind="SPECIALIST",
    )
    with pytest.raises(ValueError, match="specialist approval"):
        append_case_event((accepted, consent), started)
    result = append_case_event((accepted, consent, reviewed), started)
    assert result.events[-1] == started


def test_client_stop_blocks_workflow_transition_and_execution_steps():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    stopped = append_case_event((), stop)
    assert stopped.workflow_control.resume_blocked is True
    with pytest.raises(ValueError, match="fresh authorized restart"):
        append_case_event(
            stopped.events,
            _event(
                EventType.PERFORMED_STEP_RECORDED,
                event_id="SYNTHETIC-EVENT-002",
                suggestion=_suggestion(),
                payload=(("step_ref", "SYNTHETIC-STEP-001"),),
                actor_kind="SPECIALIST",
            ),
            stopped.workflow_control,
        )


def test_restart_requires_fresh_evaluation_and_authorization():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    stopped = append_case_event((), stop)
    invalid_restart = _event(
        EventType.WORKFLOW_RESTART_AUTHORIZED,
        event_id="SYNTHETIC-EVENT-002",
        payload=(("authorization_ref", "SYNTHETIC-AUTH-001"),),
        actor_kind="OPERATOR",
    )
    with pytest.raises(ValueError, match="fresh evaluation"):
        append_case_event(stopped.events, invalid_restart, stopped.workflow_control)


def test_authorized_fresh_restart_clears_only_the_resume_block():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    stopped = append_case_event((), stop)
    restart = _event(
        EventType.WORKFLOW_RESTART_AUTHORIZED,
        event_id="SYNTHETIC-EVENT-002",
        payload=(
            ("fresh_evaluation_ref", "SYNTHETIC-RUN-002"),
            ("authorization_ref", "SYNTHETIC-AUTH-001"),
        ),
        actor_kind="OPERATOR",
    )
    restarted = append_case_event(
        stopped.events,
        restart,
        stopped.workflow_control,
        fresh_evaluation=_run(run_id="SYNTHETIC-RUN-002"),
    )
    assert restarted.workflow_control.resume_blocked is False
    assert restarted.workflow_control.stop_event_id is None


def test_stop_is_not_relabelled_as_a_safety_workflow_state():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    result = append_case_event((), stop)
    assert result.events[-1].event_type == EventType.CLIENT_STOP_REQUESTED
    assert _case().workflow_state == WORKFLOW_STATES[1]


def test_in_memory_event_append_does_not_claim_durable_persistence():
    event = _event(EventType.QUESTION_ASKED)
    result = append_case_event((), event)
    assert result.events == (event,)
    assert not hasattr(result, "database_id")
    assert not hasattr(result, "persisted")



def test_added_dependency_is_unresolved_even_if_absence_is_claimed_non_effective():
    old = (DependencyRef("CASE", "SYNTHETIC-CASE-001", "v1"),)
    new = (
        DependencyRef("CASE", "SYNTHETIC-CASE-001", "v1"),
        DependencyRef("EVIDENCE", "SYNTHETIC-EVIDENCE-001", "v1"),
    )
    result = assess_dependency_changes(
        old, new, {"EVIDENCE:SYNTHETIC-EVIDENCE-001": "NON_EFFECTIVE"}
    )
    assert result.status == "UNRESOLVED"


def test_client_decisions_are_blocked_while_stop_request_is_active():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    stopped = append_case_event((), stop)
    with pytest.raises(ValueError, match="workflow is stopped"):
        append_case_event(
            stopped.events,
            _event(
                EventType.SUGGESTION_ACCEPTED,
                event_id="SYNTHETIC-EVENT-002",
                suggestion=_suggestion(),
            ),
            stopped.workflow_control,
        )


def test_old_acceptance_consent_and_review_do_not_survive_restart():
    suggestion = _suggestion()
    accepted = _event(EventType.SUGGESTION_ACCEPTED, suggestion=suggestion)
    consent = _event(
        EventType.EXECUTION_CONSENT_GIVEN,
        event_id="SYNTHETIC-EVENT-002",
        suggestion=suggestion,
    )
    reviewed = _event(
        EventType.SPECIALIST_REVIEW_RECORDED,
        event_id="SYNTHETIC-EVENT-003",
        suggestion=suggestion,
        payload=(
            ("review_ref", "SYNTHETIC-REVIEW-001"),
            ("decision", "APPROVED"),
        ),
        actor_kind="SPECIALIST",
    )
    stop = _event(EventType.CLIENT_STOP_REQUESTED, event_id="SYNTHETIC-EVENT-004")
    stopped = append_case_event((accepted, consent, reviewed), stop)
    restart = _event(
        EventType.WORKFLOW_RESTART_AUTHORIZED,
        event_id="SYNTHETIC-EVENT-005",
        payload=(
            ("fresh_evaluation_ref", "SYNTHETIC-RUN-002"),
            ("authorization_ref", "SYNTHETIC-AUTH-001"),
        ),
        actor_kind="OPERATOR",
    )
    restarted = append_case_event(
        stopped.events,
        restart,
        stopped.workflow_control,
        fresh_evaluation=_run(run_id="SYNTHETIC-RUN-002"),
    )
    started = _event(
        EventType.SERVICE_EXECUTION_STARTED,
        event_id="SYNTHETIC-EVENT-006",
        suggestion=suggestion,
        payload=(("service_record_ref", "SYNTHETIC-SERVICE-002"),),
        actor_kind="SPECIALIST",
    )
    with pytest.raises(ValueError, match="specialist approval"):
        append_case_event(restarted.events, started, restarted.workflow_control)


def test_decision_events_do_not_carry_across_case_or_target_versions():
    suggestion = _suggestion()
    accepted_v1 = _event(EventType.SUGGESTION_ACCEPTED, suggestion=suggestion)
    consent_v2 = replace(
        _event(
            EventType.EXECUTION_CONSENT_GIVEN,
            event_id="SYNTHETIC-EVENT-002",
            suggestion=suggestion,
        ),
        target_version="target-v2",
    )
    with pytest.raises(ValueError, match="prior acceptance"):
        append_case_event((accepted_v1,), consent_v2)


def test_performed_step_requires_a_prior_execution_start():
    suggestion = _suggestion()
    accepted = _event(EventType.SUGGESTION_ACCEPTED, suggestion=suggestion)
    consent = _event(
        EventType.EXECUTION_CONSENT_GIVEN,
        event_id="SYNTHETIC-EVENT-002",
        suggestion=suggestion,
    )
    reviewed = _event(
        EventType.SPECIALIST_REVIEW_RECORDED,
        event_id="SYNTHETIC-EVENT-003",
        suggestion=suggestion,
        payload=(
            ("review_ref", "SYNTHETIC-REVIEW-001"),
            ("decision", "APPROVED"),
        ),
        actor_kind="SPECIALIST",
    )
    step = _event(
        EventType.PERFORMED_STEP_RECORDED,
        event_id="SYNTHETIC-EVENT-004",
        suggestion=suggestion,
        payload=(("step_ref", "SYNTHETIC-STEP-001"),),
        actor_kind="SPECIALIST",
    )
    with pytest.raises(ValueError, match="prior execution-start"):
        append_case_event((accepted, consent, reviewed), step)



def test_restart_rejects_a_fresh_evaluation_for_another_version_pair():
    stop = _event(EventType.CLIENT_STOP_REQUESTED)
    stopped = append_case_event((), stop)
    restart = _event(
        EventType.WORKFLOW_RESTART_AUTHORIZED,
        event_id="SYNTHETIC-EVENT-002",
        payload=(
            ("fresh_evaluation_ref", "SYNTHETIC-RUN-002"),
            ("authorization_ref", "SYNTHETIC-AUTH-001"),
        ),
        actor_kind="OPERATOR",
    )
    with pytest.raises(ValueError, match="exact current case/target versions"):
        append_case_event(
            stopped.events,
            restart,
            stopped.workflow_control,
            fresh_evaluation=_run(
                run_id="SYNTHETIC-RUN-002",
                target_version="target-v2",
            ),
        )
