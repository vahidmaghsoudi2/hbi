"""Pre-decision client questions are informational; they do not change case decisions."""
from __future__ import annotations
from dataclasses import dataclass

EXPLICIT_DECISION_EVENTS=("accept_suggestion","reject_suggestion","execution_consent","stop_request")

@dataclass(frozen=True)
class QuestionHandling:
    question_id: str
    answer_status: str
    decision_event: str | None
    case_state_unchanged: bool
    suggestion_id_unchanged: bool
    case_version_unchanged: bool
    evidence_refs: tuple[str,...]
    message: str

def handle_predecision_question(question_id: object, question_text: object,
                               case_state: object, suggestion_id: object,
                               case_version: object, evidence_refs: object = (),
                               explicit_decision_event: object = None) -> QuestionHandling:
    if not all(isinstance(x,str) and x.strip() for x in (question_id,question_text,case_state,suggestion_id,case_version)):
        return QuestionHandling("", "invalid_input", None, False, False, False, (),
            "Question/case identifiers invalid; fail closed and do not change decisions.")
    refs=tuple(x.strip() for x in evidence_refs if isinstance(x,str) and x.strip()) if isinstance(evidence_refs,(tuple,list)) else ()
    if explicit_decision_event not in (None,*EXPLICIT_DECISION_EVENTS):
        return QuestionHandling(question_id.strip(),"invalid_decision_event",None,True,True,True,refs,
            "Decision event is invalid; question remains informational and no state change occurs.")
    status="answer_from_recorded_evidence" if refs else "evidence_gap"
    if refs:
        message="Answer only from the referenced evidence; question itself does not accept/reject or authorize execution."
    else:
        message="No evidence reference supplied; state that reliable answer is unavailable rather than guess. Question itself changes no decision."
    return QuestionHandling(question_id.strip(),status,explicit_decision_event,True,True,True,refs,message)
