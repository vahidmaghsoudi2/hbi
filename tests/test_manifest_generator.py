"""
Tests for hbi_manifest_generator.py v0.3.1
Covers: Test A, B, C, D, E per FINAL FIX ORDER.
READ-ONLY. No network. No modification of project files.
"""
import sys
import re
from pathlib import Path

PROJECT = Path("E:/HBI")
SCRIPTS_DIR = PROJECT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import hbi_manifest_generator as gen


# === STRUCTURAL TESTS ===

def test_project_root_exists():
    assert PROJECT.exists()


def test_generator_no_network_imports():
    import inspect
    src = inspect.getsource(gen)
    for mod in ["requests", "urllib", "http.client", "socket"]:
        assert mod not in src


def test_known_gates_fixed():
    ids = [g[0] for g in gen.KNOWN_GATES]
    assert ids == ["GATE 5", "GATE 6-1", "GATE 6-2", "GATE 6-3", "GATE 6-4A", "GATE 6-4B"]


def test_forbidden_paths_defined():
    assert "data/hbi.db" in gen.FORBIDDEN_PATHS
    assert "__pycache__" in gen.FORBIDDEN_PATHS


def test_list_files_excludes_forbidden():
    files = gen.list_files_in_dir("app")
    for f in files:
        assert "__pycache__" not in f
        assert not f.endswith(".pyc")


def test_manifest_type_is_derived():
    manifest = gen.build_manifest()
    assert "DERIVED_READONLY_SNAPSHOT" in manifest
    assert "NOT a Source of Truth" in manifest


# === TEST A: NOT APPROVED must NOT be interpreted as APPROVED ===

def test_A_not_approved_not_interpreted_as_approved():
    text = "GATE 6-1 (Models): NOT APPROVED (DeepSeek fixing)"
    result = gen.extract_gate_status_from_text(text, "GATE 6-1")
    assert result == "NOT_APPROVED", f"Expected NOT_APPROVED, got {result}"


def test_A_not_approved_variant_underscore():
    text = "GATE 6-1: NOT_APPROVED"
    result = gen.extract_gate_status_from_text(text, "GATE 6-1")
    assert result == "NOT_APPROVED"


def test_A_approved_still_works():
    text = "GATE 6-2 (Repositories): APPROVED"
    result = gen.extract_gate_status_from_text(text, "GATE 6-2")
    assert result == "APPROVED"


# === TEST B: Architecture Override takes precedence ===

def test_B_override_takes_precedence():
    gate_statuses = gen.collect_gate_statuses()
    # Compatible with both OVERRIDES_PATH and OVERRIDES_REL_PATH naming
    overrides_path_attr = getattr(gen, "OVERRIDES_PATH", None) or getattr(gen, "OVERRIDES_REL_PATH", None)
    assert overrides_path_attr is not None, "Generator must define an overrides path"
    override_path = PROJECT / overrides_path_attr
    if override_path.exists():
        overrides = gen.load_overrides()
        if "GATE 6-1" in overrides:
            assert gate_statuses["GATE 6-1"]["status"] == overrides["GATE 6-1"]
            assert gate_statuses["GATE 6-1"]["overridden"] is True


def test_B_gate61_is_not_verified():
    gate_statuses = gen.collect_gate_statuses()
    assert gate_statuses["GATE 6-1"]["status"] == "NOT_VERIFIED", \
        f"GATE 6-1 must be NOT_VERIFIED, got {gate_statuses['GATE 6-1']['status']}"


# === TEST C: Real Blocking Issue appears in Manifest ===

def test_C_blocking_issues_from_handover():
    issues = gen.detect_blocking_issues()
    handover = gen.read_file_safe("docs/01_project_state/HBI_Handover.txt")
    if handover is not None:
        has_cd = re.search(r"Products\s+C\s*(?:&|and)\s*D.*?UNIDENTIFIED", handover, re.IGNORECASE | re.DOTALL)
        if has_cd:
            ids = [i["id"] for i in issues]
            assert "BI-003" in ids, "BI-003 must appear when Handover has Products C&D UNIDENTIFIED"


def test_C_manifest_contains_blocking_section():
    manifest = gen.build_manifest()
    assert "## BLOCKING_ISSUES" in manifest


# === TEST D: No invention when Artifact is missing ===

def test_D_no_invention_without_artifact():
    original = gen.read_file_safe
    gen.read_file_safe = lambda x: None
    try:
        issues = gen.detect_blocking_issues()
        assert len(issues) == 0, "No issues should be invented when Artifact is missing"
    finally:
        gen.read_file_safe = original


def test_D_empty_handover_no_issues():
    original = gen.read_file_safe
    def fake_read(x):
        if "Handover" in x:
            return ""
        return original(x)
    gen.read_file_safe = fake_read
    try:
        issues = gen.detect_blocking_issues()
        assert len(issues) == 0
    finally:
        gen.read_file_safe = original


# === TEST E: Mission only identified with real Artifact ===

def test_E_mission_evidence_based():
    missions = gen.detect_missions()
    assert isinstance(missions, list)
    assert len(missions) > 0
    missions_dir = PROJECT / "docs" / "00_missions"
    if not missions_dir.exists():
        for m in missions:
            assert m["status"] in ("NOT_VERIFIED", "ARTIFACT_FOUND")


def test_E_no_mission_invention():
    missions = gen.detect_missions()
    for m in missions:
        if m["status"] == "ARTIFACT_FOUND":
            assert "reason" in m
            path = PROJECT / m["reason"]
            assert path.exists(), f"Mission artifact must exist: {m['reason']}"