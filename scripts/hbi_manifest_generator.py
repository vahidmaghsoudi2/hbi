"""
HBI Manifest Generator v0.3.1
READ-ONLY | No Network | No Side Effects on Code/DB/Architecture
Generates a Derived Read-Only Snapshot (NOT a Source of Truth).
"""
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT = Path("E:/HBI")
MANIFEST_PATH = PROJECT / "HBI_MANIFEST.md"
OVERRIDES_PATH = "docs/01_project_state/ARCHITECTURE_OVERRIDES.md"
GENERATED_AT = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

READABLE_DOCS = [
    "README.md",
    "docs/01_project_state/HBI_PROJECT_STATE.md",
    "docs/01_project_state/HBI_Handover.txt",
    "docs/02_architecture/HBI_ARCHITECTURE.md",
    "docs/03_decision_log/DECISION_LOG_INDEX.md",
    "docs/09_gate_reports/GATE_STATUS_INDEX.md",
    "docs/07_evidence/EVIDENCE_INDEX.md",
    "docs/06_artifacts_index/ARTIFACTS_INDEX.md",
]

LIST_DIRS = ["app", "tests", "scripts", "docs"]

FORBIDDEN_PATHS = ["data/hbi.db", "data", "__pycache__", ".pytest_cache"]

KNOWN_GATES = [
    ("GATE 5", "Schema Lock v1.1"),
    ("GATE 6-1", "Models"),
    ("GATE 6-2", "Repositories"),
    ("GATE 6-3", "Services"),
    ("GATE 6-4A", "Interface Contract"),
    ("GATE 6-4B", "Interface Implementation"),
]


def read_file_safe(rel_path):
    p = PROJECT / rel_path
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def extract_gate_status_from_text(text, gate_id):
    """NOT_APPROVED MUST be checked BEFORE APPROVED."""
    if text is None:
        return "NOT_VERIFIED"
    escaped = re.escape(gate_id)
    pattern = re.compile(escaped + r"[^\n]*(?:\n[^\n]*){0,3}", re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return "NOT_VERIFIED"
    block = match.group(0).upper()
    if "NOT APPROVED" in block or "NOT_APPROVED" in block:
        return "NOT_APPROVED"
    if "LOCKED" in block and "APPROVED" in block:
        return "LOCKED_APPROVED"
    if "CONDITIONALLY APPROVED" in block:
        return "CONDITIONALLY_APPROVED"
    if "READY FOR REVIEW" in block or "READY_FOR_REVIEW" in block:
        return "READY_FOR_REVIEW"
    if "APPROVED" in block:
        return "APPROVED"
    if "PENDING" in block:
        return "PENDING"
    return "NOT_VERIFIED"


def load_overrides():
    """Load Architecture Overrides from ARCHITECTURE_OVERRIDES.md."""
    content = read_file_safe(OVERRIDES_PATH)
    if content is None:
        return {}
    overrides = {}
    in_gate_section = False
    for line in content.split("\n"):
        if "## GATE_OVERRIDES" in line:
            in_gate_section = True
            continue
        if in_gate_section and line.startswith("## ") and "GATE_OVERRIDES" not in line:
            in_gate_section = False
            continue
        if in_gate_section and line.startswith("|"):
            if "Gate" in line or "---" in line or "Override_Status" in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                gate_id = parts[0].strip()
                status = parts[1].strip()
                if gate_id and status and gate_id != "(none)":
                    overrides[gate_id] = status
    return overrides


def collect_gate_statuses():
    sources = {}
    for rel in READABLE_DOCS:
        content = read_file_safe(rel)
        if content is not None:
            sources[rel] = content

    results = {}
    for gate_id, layer in KNOWN_GATES:
        statuses = []
        for rel, content in sources.items():
            s = extract_gate_status_from_text(content, gate_id)
            if s != "NOT_VERIFIED":
                statuses.append((rel, s))
        if not statuses:
            results[gate_id] = {"status": "NOT_VERIFIED", "sources": [], "conflict": False, "overridden": False}
            continue
        unique = set(s for _, s in statuses)
        if len(unique) > 1:
            results[gate_id] = {"status": "CONFLICT", "sources": statuses, "conflict": True, "overridden": False}
        else:
            results[gate_id] = {"status": statuses[0][1], "sources": statuses, "conflict": False, "overridden": False}

    overrides = load_overrides()
    for gate_id, override_status in overrides.items():
        if gate_id in results:
            results[gate_id]["status"] = override_status
            results[gate_id]["overridden"] = True
            results[gate_id]["override_source"] = "ARCHITECTURE_OVERRIDES.md"
            results[gate_id]["conflict"] = False
    return results


def list_files_in_dir(rel_dir):
    d = PROJECT / rel_dir
    if not d.exists():
        return []
    files = []
    for root, dirs, filenames in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".pytest_cache", ".git")]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), PROJECT).replace("\\", "/")
            skip = any(rel.startswith(fb) or fb in rel for fb in FORBIDDEN_PATHS)
            if not skip:
                files.append(rel)
    return sorted(files)


def detect_missions():
    """Evidence-Based Mission Discovery. No invention."""
    missions = []
    missions_dir = PROJECT / "docs" / "00_missions"
    if missions_dir.exists():
        for f in sorted(missions_dir.glob("*.md")):
            if f.name.upper() != "MISSION_INDEX.MD":
                missions.append({"id": f.stem, "status": "ARTIFACT_FOUND",
                                 "reason": str(f.relative_to(PROJECT)).replace("\\", "/")})
    docs_dir = PROJECT / "docs"
    if docs_dir.exists():
        for f in sorted(docs_dir.rglob("*MISSION*.md")):
            rel = str(f.relative_to(PROJECT)).replace("\\", "/")
            if "00_missions" not in rel:
                already = any(m.get("reason") == rel for m in missions)
                if not already:
                    missions.append({"id": f.stem, "status": "ARTIFACT_FOUND", "reason": rel})
    if not missions:
        missions.append({"id": "NONE", "status": "NOT_VERIFIED",
                         "reason": "No Mission Artifact files found in Repository"})
    return missions


def detect_blocking_issues():
    """Extract from real Artifact. No invention when Artifact missing."""
    issues = []
    handover = read_file_safe("docs/01_project_state/HBI_Handover.txt")
    if handover is None:
        return issues

    if re.search(r"Products\s+C\s*(?:&|and)\s*D.*?UNIDENTIFIED", handover, re.IGNORECASE | re.DOTALL):
        issues.append({"id": "BI-003",
                       "desc": "Products C & D UNIDENTIFIED - awaiting PO physical info",
                       "severity": "HIGH", "source": "HBI_Handover.txt"})

    if re.search(r"(?:Products\s+A\s*(?:&|and)\s*B|ISDIN).*?(?:awaiting\s+Evidence|AWAITING_EVIDENCE|Awaiting\s+collection)", handover, re.IGNORECASE | re.DOTALL):
        issues.append({"id": "BI-004",
                       "desc": "Products A & B (ISDIN) VERIFIED but awaiting Evidence",
                       "severity": "HIGH", "source": "HBI_Handover.txt"})

    if re.search(r"GATE\s+6-1.*?NOT\s+APPROVED", handover, re.IGNORECASE | re.DOTALL):
        issues.append({"id": "BI-006",
                       "desc": "GATE 6-1 NOT APPROVED in Handover - Override applied: NOT_VERIFIED",
                       "severity": "HIGH", "source": "HBI_Handover.txt"})
    return issues


def extract_evidence_status():
    """Extract Evidence Status from real Handover text."""
    handover = read_file_safe("docs/01_project_state/HBI_Handover.txt")
    results = []
    if handover is None:
        return [{"product": "ALL", "identity": "NOT_VERIFIED", "evidence": "NOT_VERIFIED", "source": "Handover missing"}]

    ab_identity = "NOT_VERIFIED"
    ab_match = re.search(r"Products\s+A\s*(?:&|and)\s*B\s*(?:\(ISDIN\))?\s*[:\-]?\s*(\w+)", handover, re.IGNORECASE)
    if ab_match:
        c = ab_match.group(1).upper()
        if c in ("VERIFIED", "UNIDENTIFIED", "IDENTIFIED", "PARTIALLY_IDENTIFIED"):
            ab_identity = c
    if ab_identity == "NOT_VERIFIED":
        ab_section = re.search(r"Products\s+A\s*(?:&|and)\s*B.*?Identity\s+Status:\s*(\w+)", handover, re.IGNORECASE | re.DOTALL)
        if ab_section:
            c = ab_section.group(1).upper()
            if c in ("VERIFIED", "UNIDENTIFIED", "IDENTIFIED", "PARTIALLY_IDENTIFIED"):
                ab_identity = c

    ab_evidence = "NOT_VERIFIED"
    if re.search(r"(?:Products\s+A\s*(?:&|and)\s*B|ISDIN).*?(?:awaiting|AWAITING)", handover, re.IGNORECASE | re.DOTALL):
        ab_evidence = "AWAITING_EVIDENCE"

    results.append({"product": "Products A & B (ISDIN)", "identity": ab_identity, "evidence": ab_evidence, "source": "Parsed from Handover"})

    cd_identity = "NOT_VERIFIED"
    cd_match = re.search(r"Products\s+C\s*(?:&|and)\s*D\s*[:\-]?\s*(\w+)", handover, re.IGNORECASE)
    if cd_match:
        c = cd_match.group(1).upper()
        if c in ("VERIFIED", "UNIDENTIFIED", "IDENTIFIED", "PARTIALLY_IDENTIFIED"):
            cd_identity = c
    if cd_identity == "NOT_VERIFIED":
        cd_section = re.search(r"Products\s+C\s*(?:&|and)\s*D.*?Identity\s+Status:\s*(\w+)", handover, re.IGNORECASE | re.DOTALL)
        if cd_section:
            c = cd_section.group(1).upper()
            if c in ("VERIFIED", "UNIDENTIFIED", "IDENTIFIED", "PARTIALLY_IDENTIFIED"):
                cd_identity = c

    cd_evidence = "NOT_VERIFIED"
    if cd_identity == "UNIDENTIFIED":
        cd_evidence = "BLOCKED"

    results.append({"product": "Products C & D", "identity": cd_identity, "evidence": cd_evidence, "source": "Parsed from Handover"})
    return results


def build_manifest():
    lines = []
    lines.append("# HBI MANIFEST")
    lines.append("> Derived Read-Only Snapshot - NOT a Source of Truth")
    lines.append("> Source of Truth: E:/HBI repository and its real artifacts")
    lines.append("> Architecture Override > Derived Status")
    lines.append("")
    lines.append("## META")
    lines.append("| Key | Value |")
    lines.append("|---|---|")
    lines.append("| manifest_version | v0.3.1 |")
    lines.append("| generated_at | " + GENERATED_AT + " |")
    lines.append("| generated_by | hbi_manifest_generator.py (AUTO) |")
    lines.append("| source_root | E:/HBI |")
    lines.append("| schema_lock | v1.1 |")
    lines.append("| manifest_type | DERIVED_READONLY_SNAPSHOT |")
    override_exists = (PROJECT / OVERRIDES_PATH).exists()
    lines.append("| overrides_file_exists | " + str(override_exists) + " |")
    lines.append("")

    lines.append("## PROJECT_STATUS")
    state = read_file_safe("docs/01_project_state/HBI_PROJECT_STATE.md")
    if state is None:
        lines.append("current_phase: NOT_VERIFIED")
        lines.append("overall_status: NOT_VERIFIED")
    else:
        m = re.search(r"Current Phase:\s*(.+)", state)
        lines.append("current_phase: " + (m.group(1).strip() if m else "NOT_VERIFIED"))
        m2 = re.search(r"overall_status:\s*(.+)", state)
        lines.append("overall_status: " + (m2.group(1).strip() if m2 else "NOT_VERIFIED"))
    lines.append("")

    lines.append("## MISSIONS")
    lines.append("> Evidence-Based only. No invention from Memory.")
    lines.append("")
    missions = detect_missions()
    lines.append("| Mission ID | Status | Evidence/Reason |")
    lines.append("|---|---|---|")
    for mi in missions:
        lines.append("| " + mi["id"] + " | " + mi["status"] + " | " + mi["reason"] + " |")
    lines.append("")

    lines.append("## ARCHITECTURE_GATES")
    lines.append("> Architecture Override > Derived Status")
    lines.append("")
    gate_statuses = collect_gate_statuses()
    lines.append("| Gate | Layer | Status | Overridden | Conflict | Source |")
    lines.append("|---|---|---|---|---|---|")
    for gate_id, layer in KNOWN_GATES:
        info = gate_statuses[gate_id]
        if info.get("overridden"):
            src = info.get("override_source", "OVERRIDE")
        elif info["sources"]:
            src = "; ".join(sorted(set(r for r, _ in info["sources"])))
        else:
            src = "NONE"
        ov = "YES" if info.get("overridden") else "NO"
        cf = "YES" if info["conflict"] else "NO"
        lines.append("| " + gate_id + " | " + layer + " | " + info["status"] + " | " + ov + " | " + cf + " | " + src + " |")
    lines.append("")

    lines.append("## BLOCKING_ISSUES")
    lines.append("> Extracted from real Artifact text. No invention.")
    lines.append("")
    issues = detect_blocking_issues()
    if issues:
        lines.append("| ID | Description | Severity | Source |")
        lines.append("|---|---|---|---|")
        for iss in issues:
            lines.append("| " + iss["id"] + " | " + iss["desc"] + " | " + iss["severity"] + " | " + iss["source"] + " |")
    else:
        lines.append("No blocking issues detected in available artifacts.")
    lines.append("")

    lines.append("## ARTIFACTS_INVENTORY")
    lines.append("| Directory | File Count | Sample |")
    lines.append("|---|---|---|")
    for d in LIST_DIRS:
        files = list_files_in_dir(d)
        sample = ", ".join(files[:3]) if files else "NONE"
        lines.append("| " + d + "/ | " + str(len(files)) + " | " + sample + " |")
    lines.append("")

    lines.append("## EVIDENCE_STATUS")
    lines.append("> Extracted from real Artifact text.")
    lines.append("")
    evidence = extract_evidence_status()
    lines.append("| Product | Identity | Evidence | Source |")
    lines.append("|---|---|---|---|")
    for ev in evidence:
        lines.append("| " + ev["product"] + " | " + ev["identity"] + " | " + ev["evidence"] + " | " + ev["source"] + " |")
    lines.append("")

    lines.append("## UNKNOWN_REGISTRY")
    lines.append("| Item | Status | Reason |")
    lines.append("|---|---|---|")
    has_unknown = False
    for gate_id, layer in KNOWN_GATES:
        info = gate_statuses[gate_id]
        if info["status"] in ("NOT_VERIFIED", "CONFLICT"):
            reason = "Architecture Override applied" if info.get("overridden") else "Insufficient/contradictory evidence"
            lines.append("| " + gate_id + " (" + layer + ") | " + info["status"] + " | " + reason + " |")
            has_unknown = True
    if not has_unknown:
        lines.append("| (none) | - | All gates verified |")
    lines.append("")

    lines.append("## END OF MANIFEST")
    lines.append("> DERIVED snapshot. Do NOT edit manually.")
    lines.append("> Source of Truth = actual repository files.")
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("HBI MANIFEST GENERATOR v0.3.1 (READ-ONLY)")
    print("=" * 60)
    manifest = build_manifest()
    MANIFEST_PATH.write_text(manifest, encoding="utf-8")
    print("[OK] Manifest written to: " + str(MANIFEST_PATH))
    print("[OK] No project file modified except HBI_MANIFEST.md")
    print("[OK] No network access used")
    print("=" * 60)
    print(manifest)
    print("=" * 60)


if __name__ == "__main__":
    main()