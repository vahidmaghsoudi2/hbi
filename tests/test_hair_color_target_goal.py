from app.domain.hair_color_target_goal import PRIORITIES, TARGET_DIMENSIONS, assess_target

def test_target_dimensions_and_priorities_are_stable():
    assert "depth" in TARGET_DIMENSIONS and "tone_direction" in TARGET_DIMENSIONS
    assert "avoid_damage" in PRIORITIES

def test_missing_goal_or_priority_requests_clarification():
    a=assess_target("",None,None)
    assert a.status=="needs_clarification"
    assert "target_description" in a.missing
    assert "priorities" in a.missing

def test_partial_target_does_not_invent_unspecified_dimensions():
    a=assess_target("Warm light brown",{"depth":"light","color_family":"brown"},("goal_match",))
    assert a.status=="partial_target"
    assert "tone_direction" in a.unknown_dimensions

def test_complete_preference_is_not_feasibility_assessment():
    dims={k:"client preference" for k in TARGET_DIMENSIONS}
    a=assess_target("Target color",dims,("goal_match","hair_condition"),("too_dark",),"Photo reference","Low maintenance")
    assert a.status=="target_recorded_for_review"
    assert "unevaluated" in a.message

def test_invalid_priority_fails_closed():
    a=assess_target("Goal",{k:"x" for k in TARGET_DIMENSIONS},("magic",))
    assert a.status=="needs_clarification"
    assert a.invalid_priorities==("magic",)
