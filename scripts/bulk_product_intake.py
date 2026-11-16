#!/usr/bin/env python3
"""Fail-closed, resumable Product identity intake over the existing HBI API.

Dry-run is the default. No database is opened by this utility. Every Product is
created through POST /api/v1/products/ as an independent API transaction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import math
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRODUCT_LINES = {"SKIN", "HAIR", "BEAUTY", "TOOLS", "OTHER"}
REQUIRED_COLUMNS = {"brand", "product_name", "product_line"}
OPTIONAL_COLUMNS = {
    "source_key", "variant", "size_value", "size_unit", "barcode_gtin",
    "market_region", "country_of_origin", "packaging_version",
}
DUPLICATE_IDENTITY_COLUMNS = (
    "brand", "product_name", "variant", "size_value", "size_unit",
    "barcode_gtin", "market_region", "packaging_version",
)
FINAL_STATES = {
    "CREATED", "EXISTING", "HUMAN_RESOLVED_SKIP", "PREFLIGHT_FAILED",
    "CREATE_REJECTED", "UNKNOWN_OUTCOME", "VALIDATION_ERROR",
}
IN_FLIGHT_STATES = {"PREFLIGHT_IN_FLIGHT", "DECISION_IN_FLIGHT", "CREATE_IN_FLIGHT"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _identity_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row.get(key) for key in DUPLICATE_IDENTITY_COLUMNS}


def _product_payload(row: dict[str, Any], duplicate_check_id: str | None = None) -> dict[str, Any]:
    allowed = REQUIRED_COLUMNS | (OPTIONAL_COLUMNS - {"source_key"})
    payload = {
        key: value for key, value in row.items()
        if key in allowed and value not in (None, "")
    }
    if duplicate_check_id:
        payload["duplicate_check_id"] = duplicate_check_id
    # A system-generated product_id is intentionally never accepted from CSV.
    payload.pop("product_id", None)
    return payload


def load_source(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if not reader.fieldnames:
        raise ValueError("CSV must contain a header row")
    normalized_headers = [str(h or "").strip() for h in reader.fieldnames]
    if len(normalized_headers) != len(set(normalized_headers)):
        raise ValueError("CSV contains duplicate column names")
    reader.fieldnames = normalized_headers
    headers = set(normalized_headers)
    missing = REQUIRED_COLUMNS - headers
    unknown = headers - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
    if missing:
        raise ValueError(f"Missing required CSV columns: {sorted(missing)}")
    if unknown:
        raise ValueError(f"Unsupported CSV columns: {sorted(unknown)}")

    rows: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_identities: dict[str, int] = {}
    for line_number, raw_row in enumerate(reader, start=2):
        if None in raw_row and any(str(v or "").strip() for v in (raw_row[None] or [])):
            raise ValueError(f"CSV line {line_number}: more values than declared columns")
        if not any(str(v or "").strip() for v in raw_row.values()):
            continue
        row: dict[str, Any] = {}
        for key in REQUIRED_COLUMNS | OPTIONAL_COLUMNS:
            if key in raw_row:
                value = str(raw_row.get(key) or "").strip()
                if value:
                    row[key] = value
        for key in ("brand", "product_name"):
            if not row.get(key):
                raise ValueError(f"CSV line {line_number}: {key} is required")
        product_line = str(row.get("product_line", "")).strip().upper()
        if product_line not in PRODUCT_LINES:
            raise ValueError(
                f"CSV line {line_number}: product_line must be one of {sorted(PRODUCT_LINES)}; "
                "it is never inferred"
            )
        row["product_line"] = product_line
        if "size_value" in row:
            try:
                size_value = float(row["size_value"])
            except (TypeError, ValueError):
                raise ValueError(f"CSV line {line_number}: size_value must be numeric")
            if not math.isfinite(size_value) or size_value <= 0:
                raise ValueError(f"CSV line {line_number}: size_value must be finite and greater than zero")
            row["size_value"] = size_value

        source_key = row.get("source_key") or f"row-{line_number}"
        if source_key in seen_keys:
            raise ValueError(f"CSV line {line_number}: duplicate source_key {source_key!r}")
        seen_keys.add(source_key)
        row["source_key"] = source_key

        identity = {
            key: row.get(key) for key in DUPLICATE_IDENTITY_COLUMNS
        }
        identity["brand"] = _norm(identity.get("brand"))
        identity["product_name"] = _norm(identity.get("product_name"))
        identity["variant"] = _norm(identity.get("variant"))
        identity["size_unit"] = _norm(identity.get("size_unit"))
        identity["barcode_gtin"] = _norm(identity.get("barcode_gtin"))
        identity["market_region"] = _norm(identity.get("market_region"))
        identity["packaging_version"] = _norm(identity.get("packaging_version"))
        identity_hash = _canonical_hash(identity)
        if identity_hash in seen_identities:
            prior = seen_identities[identity_hash]
            raise ValueError(
                f"CSV line {line_number}: repeated product identity; first appeared on line {prior}"
            )
        seen_identities[identity_hash] = line_number
        row["_source_line"] = line_number
        row["_row_hash"] = _canonical_hash(row)
        rows.append(row)

    if not rows:
        raise ValueError("CSV contains no product rows")
    if len(rows) > 500:
        raise ValueError(f"Maximum batch size is 500 rows; received {len(rows)}")
    return rows, digest


class Checkpoint:
    def __init__(self, path: Path, data: dict[str, Any]):
        self.path = path
        self.data = data

    @classmethod
    def create(cls, path: Path, rows: list[dict[str, Any]], input_hash: str, base_url: str):
        if path.exists():
            raise FileExistsError(f"Checkpoint already exists: {path}; use --resume")
        data = {
            "schema_version": 1,
            "batch_id": str(uuid.uuid4()),
            "input_sha256": input_hash,
            "base_url": base_url.rstrip("/"),
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "rows": {
                row["source_key"]: {
                    "source_line": row["_source_line"],
                    "row_sha256": row["_row_hash"],
                    "state": "READY",
                    "updated_at": utc_now(),
                    "attempts": [],
                }
                for row in rows
            },
        }
        checkpoint = cls(path, data)
        checkpoint.save()
        return checkpoint

    @classmethod
    def resume(cls, path: Path, input_hash: str, base_url: str, rows: list[dict[str, Any]]):
        if not path.exists():
            raise FileNotFoundError(f"No checkpoint found at {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("Unsupported checkpoint schema_version")
        if data.get("input_sha256") != input_hash:
            raise ValueError("Input CSV changed since checkpoint creation; refusing resume")
        if data.get("base_url") != base_url.rstrip("/"):
            raise ValueError("API target differs from checkpoint; refusing resume")
        expected = {row["source_key"]: row["_row_hash"] for row in rows}
        actual = {key: item.get("row_sha256") for key, item in data.get("rows", {}).items()}
        if expected != actual:
            raise ValueError("CSV rows/source keys differ from checkpoint; refusing resume")
        checkpoint = cls(path, data)
        # An interrupted request may already have committed. Never replay it.
        for item in checkpoint.data["rows"].values():
            if item.get("state") in IN_FLIGHT_STATES:
                item["state"] = "UNKNOWN_OUTCOME"
                item["error"] = "Process ended while request was in flight; reconcile manually before any retry."
                item["updated_at"] = utc_now()
        checkpoint.save()
        return checkpoint

    def save(self):
        self.data["updated_at"] = utc_now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(self.data, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        except Exception:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise

    def set_row(self, source_key: str, state: str, **fields):
        item = self.data["rows"][source_key]
        item.update(fields)
        item["state"] = state
        item["updated_at"] = utc_now()
        self.save()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a bearer token to a redirected host or path."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class CheckpointLock:
    """Cross-platform exclusive lock; the OS releases it if the process exits."""

    def __init__(self, checkpoint_path: Path):
        self.path = checkpoint_path.with_suffix(checkpoint_path.suffix + ".lock")
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError):
            self.handle.close()
            self.handle = None
            raise RuntimeError(f"Another batch process holds checkpoint lock: {self.path}")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.handle is None:
            return
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None


class ApiClient:
    def __init__(self, base_url: str, token: str, timeout: float = 30.0, opener=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.opener = opener or urllib.request.build_opener(_NoRedirect()).open

    def request(self, method: str, path: str, body: dict[str, Any] | None = None):
        url = self.base_url + path
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )
        try:
            response = self.opener(request, timeout=self.timeout)
            status = getattr(response, "status", None) or response.getcode()
            raw = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read()
        if not 200 <= status < 300:
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except Exception:
                parsed = {"detail": raw.decode("utf-8", errors="replace")[:2000]}
            return status, parsed
        try:
            return status, json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            return status, {"_unparsed_response": raw.decode("utf-8", errors="replace")[:2000]}


class BatchRunner:
    def __init__(self, rows: list[dict[str, Any]], checkpoint: Checkpoint, api: ApiClient,
                 decisions: dict[str, dict[str, Any]] | None = None):
        self.rows = rows
        self.checkpoint = checkpoint
        self.api = api
        self.decisions = decisions or {}

    def run(self):
        for row in self.rows:
            key = row["source_key"]
            item = self.checkpoint.data["rows"][key]
            state = item.get("state")
            if state in FINAL_STATES or state in IN_FLIGHT_STATES:
                continue
            if state == "POSSIBLE_MATCH_REVIEW":
                self._apply_decision(row, item)
                continue
            if state in {"DECISION_RECORDED", "DUPLICATE_CHECKED_NEW"}:
                self._create(row, item)
                continue
            if state != "READY":
                continue
            self._duplicate_check(row)

    def _duplicate_check(self, row: dict[str, Any]):
        key = row["source_key"]
        self.checkpoint.set_row(key, "PREFLIGHT_IN_FLIGHT", preflight_started_at=utc_now())
        try:
            status, body = self.api.request(
                "POST", "/api/v1/products/duplicate-check/", _identity_payload(row)
            )
        except Exception as exc:
            self.checkpoint.set_row(key, "UNKNOWN_OUTCOME", error=f"DuplicateCheck transport outcome unknown: {exc}")
            return
        if status != 200:
            state = "UNKNOWN_OUTCOME" if status >= 500 else "PREFLIGHT_FAILED"
            self.checkpoint.set_row(key, state, http_status=status, response=body)
            return
        result = str(body.get("result", "")).upper()
        check_id = body.get("check_id")
        response_summary = {
            "result": result,
            "reason": body.get("reason"),
            "candidates": body.get("candidates", []),
            "naming_reference_count": len(body.get("naming_reference") or []),
            "operator_decision_required": body.get("operator_decision_required"),
        }
        if not check_id or result not in {"NEW", "EXISTING", "POSSIBLE_MATCH"}:
            self.checkpoint.set_row(key, "UNKNOWN_OUTCOME", error="DuplicateCheck returned an incomplete or unknown response", response=response_summary)
            return
        if result == "EXISTING":
            self.checkpoint.set_row(key, "EXISTING", duplicate_check_id=check_id, candidates=body.get("candidates", []), response=response_summary)
        elif result == "POSSIBLE_MATCH":
            self.checkpoint.set_row(key, "POSSIBLE_MATCH_REVIEW", duplicate_check_id=check_id, candidates=body.get("candidates", []), response=response_summary)
            self._apply_decision(row, self.checkpoint.data["rows"][key])
        else:
            self.checkpoint.set_row(key, "DUPLICATE_CHECKED_NEW", duplicate_check_id=check_id, response=response_summary)
            self._create(row, self.checkpoint.data["rows"][key])

    def _apply_decision(self, row: dict[str, Any], item: dict[str, Any]):
        key = row["source_key"]
        decision = self.decisions.get(key)
        if not decision:
            return
        choice = str(decision.get("decision", "")).strip().upper()
        if choice not in {"NEW", "EXISTING", "RENAME"}:
            self.checkpoint.set_row(key, "POSSIBLE_MATCH_REVIEW", decision_error="Decision must be NEW, EXISTING, or RENAME")
            return
        payload = {
            "decision": choice,
            "selected_product_id": decision.get("selected_product_id"),
            "final_product_name": decision.get("final_product_name"),
            "reason": str(decision.get("reason") or "").strip(),
        }
        if not payload["reason"]:
            self.checkpoint.set_row(key, "POSSIBLE_MATCH_REVIEW", decision_error="Every operator decision requires an explicit reason")
            return
        elif choice == "EXISTING" and not payload["selected_product_id"]:
            self.checkpoint.set_row(key, "POSSIBLE_MATCH_REVIEW", decision_error="EXISTING decision requires selected_product_id")
            return
        elif choice == "RENAME" and not payload["final_product_name"]:
            self.checkpoint.set_row(key, "POSSIBLE_MATCH_REVIEW", decision_error="RENAME decision requires final_product_name")
            return

        self.checkpoint.set_row(key, "DECISION_IN_FLIGHT", pending_decision=payload)
        try:
            status, body = self.api.request(
                "POST",
                f"/api/v1/products/duplicate-check/audit/{item['duplicate_check_id']}/decision",
                payload,
            )
        except Exception as exc:
            self.checkpoint.set_row(key, "UNKNOWN_OUTCOME", error=f"Operator decision transport outcome unknown: {exc}")
            return
        if status != 200:
            state = "UNKNOWN_OUTCOME" if status >= 500 else "POSSIBLE_MATCH_REVIEW"
            self.checkpoint.set_row(key, state, decision_http_status=status, decision_response=body)
            return
        if choice == "NEW":
            self.checkpoint.set_row(key, "DECISION_RECORDED", operator_decision=body.get("operator_decision", payload))
            self._create(row, self.checkpoint.data["rows"][key])
        else:
            self.checkpoint.set_row(key, "HUMAN_RESOLVED_SKIP", operator_decision=body.get("operator_decision", payload))

    def _create(self, row: dict[str, Any], item: dict[str, Any]):
        key = row["source_key"]
        check_id = item.get("duplicate_check_id")
        self.checkpoint.set_row(key, "CREATE_IN_FLIGHT", create_started_at=utc_now())
        try:
            status, body = self.api.request(
                "POST",
                "/api/v1/products/",
                _product_payload(row, duplicate_check_id=check_id),
            )
        except Exception as exc:
            self.checkpoint.set_row(key, "UNKNOWN_OUTCOME", error=f"Product Create transport outcome unknown: {exc}")
            return
        if status == 201 and body.get("product_id"):
            self.checkpoint.set_row(
                key, "CREATED", product_id=body["product_id"], product_status=body.get("status"),
                qa_verdict=body.get("qa_verdict"), identity_status=body.get("identity_status"),
                http_status=status,
            )
        elif status >= 500:
            self.checkpoint.set_row(key, "UNKNOWN_OUTCOME", http_status=status, response=body)
        else:
            self.checkpoint.set_row(key, "CREATE_REJECTED", http_status=status, response=body)


def load_decisions(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Decision file must be a JSON object keyed by source_key")
    allowed_fields = {"decision", "selected_product_id", "final_product_name", "reason"}
    for source_key, decision in data.items():
        if not isinstance(decision, dict):
            raise ValueError(f"Decision for {source_key!r} must be an object")
        unknown = set(decision) - allowed_fields
        if unknown:
            raise ValueError(f"Decision for {source_key!r} has unsupported fields: {sorted(unknown)}")
        if str(decision.get("decision", "")).strip().upper() not in {"NEW", "EXISTING", "RENAME"}:
            raise ValueError(f"Decision for {source_key!r} must be NEW, EXISTING, or RENAME")
        if not str(decision.get("reason") or "").strip():
            raise ValueError(f"Decision for {source_key!r} requires an explicit reason")
    return data


def build_parser():
    parser = argparse.ArgumentParser(
        description="Resumable HBI Product intake. Dry-run by default; no blind retries."
    )
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 CSV source file")
    parser.add_argument("--base-url", required=True, help="Exact HBI API origin, e.g. https://hbi.example")
    parser.add_argument("--checkpoint", type=Path, default=Path("bulk-product-intake.checkpoint.json"))
    parser.add_argument("--decision-file", type=Path, help="JSON mapping source_key to explicit operator decisions")
    parser.add_argument("--apply", action="store_true", help="Send API requests; without this flag only validate/plan")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing matching checkpoint")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows, input_hash = load_source(args.input)
        base_url = args.base_url.rstrip("/")
        parts = urlsplit(base_url)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            raise ValueError("--base-url must be an explicit http:// or https:// origin")
        if parts.username or parts.password or parts.query or parts.fragment or parts.path not in {"", "/"}:
            raise ValueError("--base-url must be an origin only; do not include credentials, path, query, or fragment")
        if parts.scheme != "https" and parts.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("HTTPS is required for non-local API targets")
        print(f"Validated {len(rows)} product rows; input_sha256={input_hash}")
        if not args.apply:
            print("DRY RUN: no token read, no checkpoint written, no API request sent.")
            return 0
        token = os.getenv("HBI_ACCESS_TOKEN", "").strip()
        if not token:
            raise ValueError("Set HBI_ACCESS_TOKEN in the process environment; it is never stored in the checkpoint")
        with CheckpointLock(args.checkpoint):
            if args.resume:
                checkpoint = Checkpoint.resume(args.checkpoint, input_hash, base_url, rows)
            else:
                checkpoint = Checkpoint.create(args.checkpoint, rows, input_hash, base_url)
            decisions = load_decisions(args.decision_file)
            BatchRunner(rows, checkpoint, ApiClient(base_url, token), decisions).run()
            counts: dict[str, int] = {}
            for item in checkpoint.data["rows"].values():
                state = item.get("state", "UNKNOWN")
                counts[state] = counts.get(state, 0) + 1
            print(json.dumps({"batch_id": checkpoint.data["batch_id"], "states": counts, "checkpoint": str(args.checkpoint)}, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
