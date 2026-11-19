from app.domain.hair_color_owner_rules import (
    OWNER_DEFINED_RULES,
    get_owner_defined_rule,
    list_owner_defined_rule_ids,
)


def test_registry_has_stable_unique_rule_ids():
    ids = list_owner_defined_rule_ids()
    assert ids == ("OR-01", "OR-02", "OR-03", "OR-04", "OR-05", "OR-06")
    assert len(ids) == len(set(ids))


def test_natural_extra_rule_has_explicit_nonchemical_limit():
    rule = get_owner_defined_rule("OR-01")
    assert rule is not None
    assert "stronger" in rule.statement
    assert "lift" in rule.limitation
    assert "oxidative strength" in rule.limitation


def test_numbering_exceptions_are_exactly_scoped():
    rule = get_owner_defined_rule("OR-02")
    assert rule is not None
    for code in ("6.7", "8.56", "6.53", "6.54"):
        assert code in rule.statement
    assert "exact raw shade-code strings" in rule.scope


def test_raw_code_preservation_and_alias_boundaries():
    raw = get_owner_defined_rule("OR-03")
    aliases = get_owner_defined_rule("OR-04")
    assert raw is not None and "exactly" in raw.statement
    assert aliases is not None
    assert "+05" in aliases.statement and "+09" in aliases.statement
    assert "Do not extend" in aliases.limitation


def test_rules_are_scope_limited_and_nonchemical():
    scope = get_owner_defined_rule("OR-05")
    nonchemical = get_owner_defined_rule("OR-06")
    assert scope is not None and "only within its stated scope" in scope.statement
    assert nonchemical is not None
    for rule in OWNER_DEFINED_RULES:
        assert rule.status == "owner_approved"
        assert rule.limitation


def test_unknown_or_wrong_type_rule_id_fails_closed():
    assert get_owner_defined_rule("OR-99") is None
    assert get_owner_defined_rule("or-01") is None
    assert get_owner_defined_rule(None) is None
    assert get_owner_defined_rule(11) is None
