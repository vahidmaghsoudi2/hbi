"""Unit tests for the contract-only hair-color test runner."""
from __future__ import annotations

import pytest

from scripts.run_hair_color_contract import (
    DEFAULT_README,
    ContractError,
    build_report,
    extract_manifest,
    validate_manifest,
)


@pytest.fixture()
def manifest():
    return extract_manifest(DEFAULT_README.read_text(encoding="utf-8"))


def test_embedded_manifest_is_valid(manifest):
    assert validate_manifest(manifest) == []


def test_manifest_has_fifteen_unique_scenarios(manifest):
    fixtures = manifest["fixtures"]
    assert len(fixtures) == 15
    assert len({item["fixture_id"] for item in fixtures}) == 15
    assert {item["scenario_id"] for item in fixtures} == {f"S{i:02d}" for i in range(1, 16)}


def test_duplicate_fixture_id_is_rejected(manifest):
    manifest["fixtures"][1]["fixture_id"] = manifest["fixtures"][0]["fixture_id"]
    assert any("duplicate fixture_id" in error for error in validate_manifest(manifest))


def test_non_synthetic_fixture_is_rejected(manifest):
    manifest["fixtures"][0]["synthetic"] = False
    assert any("synthetic must be true" in error for error in validate_manifest(manifest))


def test_missing_safety_assertion_is_rejected(manifest):
    fixture = next(item for item in manifest["fixtures"] if item["scenario_id"] == "S07")
    fixture["assertions"].remove("safety_stop_blocks_options")
    assert any("S07 missing assertion" in error for error in validate_manifest(manifest))


def test_personal_data_field_names_are_rejected(manifest):
    manifest["fixtures"][0]["customer_phone"] = "synthetic-placeholder"
    assert any("personal-data field names" in error for error in validate_manifest(manifest))


def test_report_never_marks_product_behavior_as_pass(manifest):
    report = build_report(manifest, [], ["python", "scripts/run_hair_color_contract.py"])
    assert report["contract_validation"] == "PASS"
    assert report["product_behavior_suite"] == "BLOCKED"
    assert len(report["scenario_results"]) == 15
    assert {item["status"] for item in report["scenario_results"]} == {"BLOCKED"}


def test_malformed_json_block_is_rejected():
    with pytest.raises(ContractError):
        extract_manifest("### stage four\n\n" + chr(96) * 3 + "json\n{bad}\n" + chr(96) * 3)

def test_cli_writes_a_contract_pass_and_runtime_blocked_report(tmp_path, capsys):
    from scripts.run_hair_color_contract import main

    report_path = tmp_path / "runner-report.json"
    exit_code = main(["--output", str(report_path)])
    output = capsys.readouterr().out
    report = __import__("json").loads(report_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert "CONTRACT_VALIDATION=PASS" in output
    assert "PRODUCT_BEHAVIOR_SUITE=BLOCKED" in output
    assert report["contract_validation"] == "PASS"
    assert report["product_behavior_suite"] == "BLOCKED"
    assert len(report["scenario_results"]) == 15
