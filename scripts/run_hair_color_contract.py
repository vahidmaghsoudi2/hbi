"""Contract-only validator for synthetic HBI hair-color fixtures.

It validates the JSON manifest embedded in the hair-color README. It does not
import or execute product logic; all product-behavior scenarios remain BLOCKED
until a reviewed engine adapter exists. Standard library only; no network calls.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_README = ROOT / "docs/homepage/encyclopedia/hair-color/README.md"
DEFAULT_MANIFEST = ROOT / "tests/fixtures/hair-color-contract-v1.json"
DEFAULT_SCHEMA = ROOT / "tests/fixtures/hair-color-contract-v1.schema.json"
HEADING = "### بستهٔ ساخت‌یافتهٔ آزمون و اعتبارسنجی قرارداد — مرحلهٔ چهارم"
SCENARIOS = tuple(f"S{i:02d}" for i in range(1, 16))
REQUIRED = (
    "fixture_id", "scenario_id", "synthetic", "input_profile",
    "expected_status", "expected_action", "required_evidence",
    "forbidden", "assertions", "severity_on_violation",
)
KEY_ASSERTIONS = {
    "S01": ("all_required_case_fields_present", "no_unresolved_safety_stop", "suggestion_has_traceable_rationale", "acceptance_unchanged", "execution_consent_unchanged"),
    "S02": ("only_material_missing_field_requested", "dependent_output_withheld", "case_waits_for_information"),
    "S03": ("both_values_preserved", "both_sources_preserved", "dependent_decision_withheld"),
    "S04": ("image_scope_limited", "no_hidden_trait_inference", "no_executable_suggestion"),
    "S05": ("identity_gap_detected", "market_and_line_requested", "no_product_specific_output"),
    "S06": ("knowledge_gap_distinguished_from_data_gap", "mock_evidence_rejected", "dependent_output_withheld"),
    "S07": ("safety_stop_blocks_options", "no_execution_suggestion", "stop_reason_traceable"),
    "S08": ("constraint_has_applicable_support_or_is_marked_unverified", "no_unsupported_alternative", "limitation_explained"),
    "S09": ("exactly_two_options_shown", "hard_constraints_applied_first", "ranking_stable_under_input_permutation"),
    "S10": ("exactly_one_option_shown", "rejected_options_not_active"),
    "S11": ("acceptance_snapshot_unchanged", "execution_consent_snapshot_unchanged", "question_event_recorded"),
    "S12": ("rejection_traceable", "rejected_suggestion_absent_from_active_list", "replacement_requires_independent_validity"),
    "S13": ("new_version_created", "dependent_outputs_rechecked", "independent_data_preserved", "prior_acceptance_and_consent_not_carried"),
    "S14": ("stop_event_recorded", "completed_steps_accurate", "uncompleted_steps_remain_uncompleted", "resume_blocked"),
    "S15": ("engine_failure_classified", "stale_output_suppressed", "run_id_and_failure_stage_logged"),
}
PERSONAL_KEY = re.compile(
    r"(customer_name|client_name|phone_number|email_address|real_client_id|"
    r"customer_phone|customer_email|customer_address|personal_identifier)",
    re.IGNORECASE,
)


class ContractError(ValueError):
    pass


def extract_manifest(readme_text: str) -> dict[str, Any]:
    heading_at = readme_text.find(HEADING)
    if heading_at < 0:
        raise ContractError("stage-four manifest section not found")
    section = readme_text[heading_at:]
    fence = chr(96) * 3
    start_token = fence + "json\n"
    blocks = section.split(start_token)
    if len(blocks) != 2 or "\n" + fence not in blocks[1]:
        raise ContractError("expected exactly one JSON code block in stage-four section")
    raw = blocks[1].split("\n" + fence, 1)[0]
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid manifest JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("manifest root must be an object")
    return value


def _all_keys(value: Any):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _all_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _all_keys(nested)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("contract_version") != "HBI-HC-TEST-CONTRACT-1.0":
        errors.append("invalid contract_version")
    if manifest.get("data_classification") != "SYNTHETIC_ONLY":
        errors.append("data_classification must be SYNTHETIC_ONLY")
    if manifest.get("scientific_evidence") is not False:
        errors.append("scientific_evidence must be false")
    if manifest.get("runtime_execution") is not False:
        errors.append("runtime_execution must be false for this contract-only runner")

    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        return errors + ["fixtures must be an array"]
    if len(fixtures) != 15:
        errors.append(f"expected 15 fixtures; found {len(fixtures)}")

    ids: set[str] = set()
    scenario_ids: set[str] = set()
    by_scenario: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(fixtures):
        label = f"fixtures[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = [field for field in REQUIRED if field not in item]
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
            continue
        fixture_id, scenario_id = item["fixture_id"], item["scenario_id"]
        if not isinstance(fixture_id, str) or not re.fullmatch(r"FX-S(0[1-9]|1[0-5])-SYN-01", fixture_id):
            errors.append(f"{label} invalid fixture_id")
        elif fixture_id in ids:
            errors.append(f"duplicate fixture_id: {fixture_id}")
        else:
            ids.add(fixture_id)
        if not isinstance(scenario_id, str) or scenario_id not in SCENARIOS:
            errors.append(f"{label} invalid scenario_id")
        elif scenario_id in scenario_ids:
            errors.append(f"duplicate scenario_id: {scenario_id}")
        else:
            scenario_ids.add(scenario_id)
            by_scenario[scenario_id] = item
        if item.get("synthetic") is not True:
            errors.append(f"{label} synthetic must be true")
        for field in ("input_profile", "expected_status", "expected_action"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{label}.{field} must be a non-empty string")
        for field in ("required_evidence", "forbidden", "assertions"):
            value = item.get(field)
            if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
                errors.append(f"{label}.{field} must be a non-empty string array")
        assertions = item.get("assertions")
        if isinstance(assertions, list) and len(assertions) != len(set(assertions)):
            errors.append(f"{label}.assertions contains duplicate entries")
        if item.get("severity_on_violation") not in ("C0", "C1"):
            errors.append(f"{label}.severity_on_violation must be C0 or C1")

    missing_scenarios = sorted(set(SCENARIOS) - scenario_ids)
    if missing_scenarios:
        errors.append("missing scenarios: " + ", ".join(missing_scenarios))
    for scenario_id, required in KEY_ASSERTIONS.items():
        item = by_scenario.get(scenario_id, {})
        actual = item.get("assertions", [])
        for assertion in required:
            if assertion not in actual:
                errors.append(f"{scenario_id} missing assertion: {assertion}")
    personal_keys = sorted({key for key in _all_keys(manifest) if PERSONAL_KEY.search(key)})
    if personal_keys:
        errors.append("prohibited personal-data field names: " + ", ".join(personal_keys))
    return errors



def validate_json_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the small, explicit JSON Schema 2020-12 subset used by this bundle."""
    errors: list[str] = []
    expected_type = schema.get("type")
    type_ok = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "boolean": isinstance(instance, bool),
    }.get(expected_type, True)
    if not type_ok:
        return [f"{path} must be {expected_type}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']!r}")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key} is required")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(instance) - set(properties))
            if extras:
                errors.append(f"{path} has additional properties: {', '.join(extras)}")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_json_schema(value, properties[key], f"{path}.{key}"))
    elif isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path} has fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path} has more than {schema['maxItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(validate_json_schema(value, item_schema, f"{path}[{index}]"))
    elif isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path} is shorter than {schema['minLength']} characters")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, instance) is None:
            errors.append(f"{path} does not match required pattern")
    return errors


def _git_value(command: list[str]) -> str:
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return "UNAVAILABLE"
    return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"


def build_report(manifest: dict[str, Any], errors: list[str], command: list[str]) -> dict[str, Any]:
    fixtures = manifest.get("fixtures", []) if isinstance(manifest, dict) else []
    scenarios = [
        {
            "scenario_id": item.get("scenario_id", "UNKNOWN"),
            "fixture_id": item.get("fixture_id", "UNKNOWN"),
            "status": "BLOCKED",
            "reason": "PRODUCT_ENGINE_ADAPTER_NOT_AVAILABLE",
        }
        for item in fixtures if isinstance(item, dict)
    ]
    return {
        "report_schema": "hbi.hair_color.contract_validation.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "agent": {"name": "ChatGPT", "model": "GPT-6", "runtime": "Python standard library"},
        "code_sha": _git_value(["git", "rev-parse", "HEAD"]),
        "branch": _git_value(["git", "branch", "--show-current"]),
        "command": command,
        "manifest_contract_version": manifest.get("contract_version") if isinstance(manifest, dict) else None,
        "manifest_fixture_count": len(fixtures) if isinstance(fixtures, list) else 0,
        "contract_validation": "PASS" if not errors else "FAIL",
        "contract_errors": errors,
        "product_behavior_suite": "BLOCKED",
        "scenario_results": scenarios,
        "interpretation": (
            "PASS validates only manifest structure and assertions. Product behavior remains BLOCKED "
            "because no reviewed product-engine adapter is connected."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    passed_args = argv if argv is not None else sys.argv[1:]
    command = [sys.executable, str(Path(__file__).resolve()), *passed_args]
    try:
        embedded_manifest = extract_manifest(args.readme.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        errors = validate_json_schema(manifest, schema)
        if manifest != embedded_manifest:
            errors.append("external fixture bundle differs from embedded README manifest")
        errors.extend(validate_manifest(manifest))
    except (OSError, ContractError, json.JSONDecodeError) as exc:
        manifest, errors = {}, [str(exc)]
    report = build_report(manifest, errors, command)
    output = args.output
    if output is None:
        folder = Path(tempfile.gettempdir()) / "hbi-hair-color-contract-evidence"
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = folder / f"contract-report-{stamp}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CONTRACT_VALIDATION={report['contract_validation']}")
    print(f"FIXTURES={report['manifest_fixture_count']}")
    print(f"PRODUCT_BEHAVIOR_SUITE={report['product_behavior_suite']}")
    print(f"BLOCKED_SCENARIOS={len(report['scenario_results'])}")
    print(f"REPORT={output}")
    for error in errors:
        print(f"ERROR={error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
