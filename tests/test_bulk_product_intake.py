import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.bulk_product_intake import (
    ApiClient,
    BatchRunner,
    Checkpoint,
    load_source,
    _product_payload,
    load_decisions,
    _same_identity,
    _NoRedirect,
    CheckpointLock,
    validate_decision_keys,
)


class FakeApi:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def request(self, method, path, body=None):
        self.requests.append((method, path, body))
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class BulkProductIntakeTests(unittest.TestCase):
    def write_csv(self, path, rows, headers=None):
        headers = headers or ["source_key", "brand", "product_name", "product_line", "variant", "size_value", "size_unit"]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def make_row(self, n=1):
        return {
            "source_key": f"sku-{n}",
            "brand": f"Brand {n}",
            "product_name": f"Product {n}",
            "product_line": "SKIN",
            "variant": "Original",
            "size_value": "50",
            "size_unit": "ml",
        }

    def load_rows(self, directory, rows):
        path = directory / "products.csv"
        self.write_csv(path, rows)
        return path, load_source(path)

    def make_checkpoint(self, directory, rows, digest):
        return Checkpoint.create(directory / "checkpoint.json", rows, digest, "https://hbi.test")

    def test_loads_100_to_500_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [self.make_row(n) for n in range(1, 501)])
            rows, digest = load_source(path)
            self.assertEqual(len(rows), 500)
            self.assertEqual(len(digest), 64)

    def test_rejects_more_than_500_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [self.make_row(n) for n in range(1, 502)])
            with self.assertRaisesRegex(ValueError, "Maximum batch size"):
                load_source(path)

    def test_rejects_missing_product_line_before_any_api_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [{"brand": "A", "product_name": "B"}], headers=["brand", "product_name"])
            with self.assertRaisesRegex(ValueError, "Missing required"):
                load_source(path)

    def test_rejects_unknown_columns_and_invalid_product_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [{"brand": "A", "product_name": "B", "product_line": "SKIN", "status": "ACTIVE"}], headers=["brand", "product_name", "product_line", "status"])
            with self.assertRaisesRegex(ValueError, "Unsupported CSV columns"):
                load_source(path)
            self.write_csv(path, [{"brand": "A", "product_name": "B", "product_line": "INFERRED"}],
                           headers=["brand", "product_name", "product_line"])
            with self.assertRaisesRegex(ValueError, "never inferred"):
                load_source(path)

    def test_rejects_duplicate_identity_and_duplicate_source_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [self.make_row(1), {**self.make_row(2), "source_key": "sku-2", "brand": "Brand 1", "product_name": "Product 1"}])
            with self.assertRaisesRegex(ValueError, "repeated product identity"):
                load_source(path)
            self.write_csv(path, [self.make_row(1), {**self.make_row(2), "source_key": "sku-1"}])
            with self.assertRaisesRegex(ValueError, "duplicate source_key"):
                load_source(path)

    def test_new_row_preflights_then_creates(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            api = FakeApi([
                (200, {"check_id": "DCA-1", "result": "NEW", "candidates": []}),
                (201, {"product_id": "HBI-PROD-1", "status": "DRAFT", "qa_verdict": "PENDING", "identity_status": "NEEDS_REVIEW"}),
            ])
            BatchRunner(rows, checkpoint, api).run()
            item = checkpoint.data["rows"]["sku-1"]
            self.assertEqual(item["state"], "CREATED")
            self.assertEqual(item["product_id"], "HBI-PROD-1")
            self.assertEqual(len(api.requests), 2)
            self.assertEqual(api.requests[0][1], "/api/v1/products/duplicate-check/")
            self.assertEqual(api.requests[1][1], "/api/v1/products/")
            self.assertEqual(api.requests[1][2]["product_line"], "SKIN")
            self.assertEqual(api.requests[1][2]["duplicate_check_id"], "DCA-1")
            self.assertNotIn("source_key", api.requests[1][2])
            self.assertNotIn("_row_hash", api.requests[1][2])
            self.assertEqual(item["last_request"]["path"], "/api/v1/products/")
            self.assertEqual(item["last_response"]["status"], 201)

    def test_unexpected_success_response_without_product_id_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            api = FakeApi([
                (200, {"check_id": "DCA-11", "result": "NEW", "candidates": []}),
                (201, {"status": "DRAFT"}),
            ])
            BatchRunner(rows, checkpoint, api).run()
            item = checkpoint.data["rows"]["sku-1"]
            self.assertEqual(item["state"], "UNKNOWN_OUTCOME")
            self.assertIn("may have been committed", item["error"])

    def test_existing_match_never_creates(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            api = FakeApi([(200, {"check_id": "DCA-2", "result": "EXISTING", "candidates": [{"product_id": "P1"}]})])
            BatchRunner(rows, checkpoint, api).run()
            self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "EXISTING")
            self.assertEqual(len(api.requests), 1)

    def test_possible_match_stops_for_human_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            api = FakeApi([(200, {"check_id": "DCA-3", "result": "POSSIBLE_MATCH", "candidates": [{"product_id": "P1"}]})])
            BatchRunner(rows, checkpoint, api).run()
            item = checkpoint.data["rows"]["sku-1"]
            self.assertEqual(item["state"], "POSSIBLE_MATCH_REVIEW")
            self.assertEqual(item["duplicate_check_id"], "DCA-3")
            self.assertEqual(len(api.requests), 1)

    def test_possible_match_requires_and_binds_explicit_new_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            api = FakeApi([
                (200, {"check_id": "DCA-4", "result": "POSSIBLE_MATCH", "candidates": [{"product_id": "P1"}]}),
                (200, {"check_id": "DCA-4", "operator_decision": {"decision": "NEW"}}),
                (201, {"product_id": "HBI-PROD-4", "status": "DRAFT", "qa_verdict": "PENDING", "identity_status": "NEEDS_REVIEW"}),
            ])
            decisions = {"sku-1": {"decision": "NEW", "reason": "Operator confirmed distinct identity"}}
            BatchRunner(rows, checkpoint, api, decisions).run()
            item = checkpoint.data["rows"]["sku-1"]
            self.assertEqual(item["state"], "CREATED")
            self.assertEqual(api.requests[1][1], "/api/v1/products/duplicate-check/audit/DCA-4/decision")
            self.assertEqual(api.requests[2][2]["duplicate_check_id"], "DCA-4")

    def test_existing_or_rename_decision_never_creates(self):
        for decision in (
            {"decision": "EXISTING", "selected_product_id": "P1", "reason": "Operator selected existing Product P1"},
            {"decision": "RENAME", "final_product_name": "New name", "reason": "Operator requested identity rename"},
        ):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                path, (rows, digest) = self.load_rows(directory, [self.make_row()])
                checkpoint = self.make_checkpoint(directory, rows, digest)
                api = FakeApi([
                    (200, {"check_id": "DCA-5", "result": "POSSIBLE_MATCH", "candidates": []}),
                    (200, {"check_id": "DCA-5", "operator_decision": decision}),
                ])
                BatchRunner(rows, checkpoint, api, {"sku-1": decision}).run()
                self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "HUMAN_RESOLVED_SKIP")
                self.assertEqual(len(api.requests), 2)

    def test_transport_error_marks_unknown_and_resume_never_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint_path = directory / "checkpoint.json"
            checkpoint = Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            api = FakeApi([
                (200, {"check_id": "DCA-6", "result": "NEW", "candidates": []}),
                TimeoutError("simulated response loss"),
            ])
            BatchRunner(rows, checkpoint, api).run()
            self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")
            resumed = Checkpoint.resume(checkpoint_path, digest, "https://hbi.test", rows)
            no_replay = FakeApi([])
            with self.assertRaisesRegex(RuntimeError, "Blocked rows"):
                BatchRunner(rows, resumed, no_replay).run()
            self.assertEqual(no_replay.requests, [])
            self.assertEqual(resumed.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")

    def test_resume_converts_inflight_to_unknown_without_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint_path = directory / "checkpoint.json"
            checkpoint = Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            checkpoint.set_row("sku-1", "CREATE_IN_FLIGHT", create_started_at="2026-01-01T00:00:00Z")
            resumed = Checkpoint.resume(checkpoint_path, digest, "https://hbi.test", rows)
            self.assertEqual(resumed.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")
            api = FakeApi([])
            with self.assertRaisesRegex(RuntimeError, "Blocked rows"):
                BatchRunner(rows, resumed, api).run()
            self.assertEqual(api.requests, [])

    def test_resume_continues_after_duplicate_check_was_checkpointed(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint_path = directory / "checkpoint.json"
            checkpoint = Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            checkpoint.set_row("sku-1", "DUPLICATE_CHECKED_NEW", duplicate_check_id="DCA-7")
            resumed = Checkpoint.resume(checkpoint_path, digest, "https://hbi.test", rows)
            api = FakeApi([(201, {"product_id": "HBI-PROD-7", "status": "DRAFT", "qa_verdict": "PENDING", "identity_status": "NEEDS_REVIEW"})])
            BatchRunner(rows, resumed, api).run()
            self.assertEqual(resumed.data["rows"]["sku-1"]["state"], "CREATED")
            self.assertEqual(len(api.requests), 1)
            self.assertEqual(api.requests[0][2]["duplicate_check_id"], "DCA-7")

    def test_checkpoint_rejects_changed_input_and_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint_path = directory / "checkpoint.json"
            Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            with self.assertRaisesRegex(ValueError, "Input CSV changed"):
                Checkpoint.resume(checkpoint_path, "different", "https://hbi.test", rows)
            with self.assertRaisesRegex(ValueError, "API target differs"):
                Checkpoint.resume(checkpoint_path, digest, "https://other.test", rows)

    def test_product_payload_excludes_local_checkpoint_fields(self):
        row = {**self.make_row(), "_source_line": 2, "_row_hash": "abc"}
        payload = _product_payload(row, "DCA-8")
        self.assertEqual(payload["product_line"], "SKIN")
        self.assertNotIn("source_key", payload)
        self.assertNotIn("_source_line", payload)
        self.assertNotIn("_row_hash", payload)
        self.assertNotIn("product_id", payload)

    def test_decision_file_requires_explicit_reason_and_known_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.json"
            path.write_text(json.dumps({"sku-1": {"decision": "NEW"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires an explicit reason"):
                load_decisions(path)
            path.write_text(json.dumps({"sku-1": {"decision": "NEW", "reason": "reviewed", "status": "ACTIVE"}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported fields"):
                load_decisions(path)

    def test_duplicate_headers_and_extra_csv_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            path.write_text("brand,product_name,product_line,brand\\nA,B,SKIN,A\\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate column names"):
                load_source(path)
            path.write_text("brand,product_name,product_line\\nA,B,SKIN,EXTRA\\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "more values than declared columns"):
                load_source(path)

    def test_non_finite_size_value_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "products.csv"
            self.write_csv(path, [{**self.make_row(), "size_value": "NaN"}])
            with self.assertRaisesRegex(ValueError, "finite and greater than zero"):
                load_source(path)

    def test_read_only_reconciliation_records_candidates_without_resolving(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            checkpoint.set_row("sku-1", "UNKNOWN_OUTCOME", create_started_at="2026-11-16T00:00:00+00:00")
            identity = {
                "product_id": None,
                "brand": "Brand 1",
                "product_name": "Product 1",
                "variant": "Original",
                "size_value": 50.0,
                "size_unit": "ml",
                "barcode_gtin": None,
                "market_region": None,
                "packaging_version": None,
            }
            audit = {"check_id": "DCA-9", "input_snapshot": identity}
            product = {**identity, "product_id": "HBI-PROD-9"}
            api = FakeApi([(200, [audit]), (200, [product])])
            BatchRunner(rows, checkpoint, api).reconcile()
            item = checkpoint.data["rows"]["sku-1"]
            self.assertEqual(item["state"], "UNKNOWN_OUTCOME")
            self.assertEqual([x["check_id"] for x in item["reconciliation"]["duplicate_check_candidates"]], ["DCA-9"])
            self.assertEqual(item["reconciliation"]["product_candidate_ids"], ["HBI-PROD-9"])
            self.assertTrue(all(request[0] == "GET" for request in api.requests))

    def test_reconciliation_failure_does_not_change_unknown_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            checkpoint = self.make_checkpoint(directory, rows, digest)
            checkpoint.set_row("sku-1", "UNKNOWN_OUTCOME")
            api = FakeApi([(503, {"detail": "unavailable"}), (401, {"detail": "unauthorized"})])
            BatchRunner(rows, checkpoint, api).reconcile()
            self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")
            self.assertTrue(checkpoint.data["last_reconciliation"]["read_only"])
            self.assertEqual(len(api.requests), 2)
            self.assertTrue(all(request[0] == "GET" for request in api.requests))

    def test_identity_reconciliation_ignores_generated_product_id_when_not_supplied(self):
        left = {"product_id": None, "brand": "Brand", "product_name": "Name", "size_value": 30}
        right = {"product_id": "HBI-PROD-X", "brand": " brand ", "product_name": "NAME", "size_value": 30.0}
        self.assertTrue(_same_identity(left, right))

    def test_uncertain_row_stops_batch_until_read_only_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row(1), self.make_row(2)])
            checkpoint_path = directory / "checkpoint.json"
            checkpoint = Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            first_api = FakeApi([(503, {"detail": "server outcome uncertain"})])
            BatchRunner(rows, checkpoint, first_api).run()
            self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")
            self.assertEqual(checkpoint.data["rows"]["sku-2"]["state"], "READY")
            self.assertEqual(len(first_api.requests), 1)

            resumed = Checkpoint.resume(checkpoint_path, digest, "https://hbi.test", rows)
            blocked_api = FakeApi([])
            with self.assertRaisesRegex(RuntimeError, "Blocked rows"):
                BatchRunner(rows, resumed, blocked_api).run()
            self.assertEqual(blocked_api.requests, [])

            reconcile_api = FakeApi([(200, []), (200, [])])
            BatchRunner(rows, resumed, reconcile_api).reconcile()
            self.assertTrue(resumed.data["rows"]["sku-1"]["reconciliation"]["read_only"])
            self.assertEqual(resumed.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")

            continue_api = FakeApi([
                (200, {"check_id": "DCA-10", "result": "NEW", "candidates": []}),
                (201, {"product_id": "HBI-PROD-10", "status": "DRAFT", "qa_verdict": "PENDING", "identity_status": "NEEDS_REVIEW"}),
            ])
            BatchRunner(rows, resumed, continue_api).run()
            self.assertEqual(resumed.data["rows"]["sku-1"]["state"], "UNKNOWN_OUTCOME")
            self.assertEqual(resumed.data["rows"]["sku-2"]["state"], "CREATED")
            self.assertEqual(len(continue_api.requests), 2)

    def test_api_client_uses_bearer_header_and_redirects_are_rejected(self):
        captured = {}

        class Response:
            status = 200
            def read(self):
                return b'{"ok": true}'
            def getcode(self):
                return 200

        def opener(request, timeout):
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            return Response()

        status, body = ApiClient("https://hbi.test", "secret-token", opener=opener).request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, {"ok": True})
        self.assertEqual(captured["authorization"], "Bearer secret-token")
        self.assertEqual(captured["timeout"], 30.0)
        self.assertIsNone(_NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://other.test"))

    @unittest.skipIf(__import__("os").name == "nt", "POSIX flock behavior only")
    def test_checkpoint_lock_rejects_concurrent_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checkpoint.json"
            other_checkpoint = Path(tmp) / "other-checkpoint.json"
            with CheckpointLock(path, "https://hbi.test"):
                with self.assertRaisesRegex(RuntimeError, "Another batch process"):
                    with CheckpointLock(other_checkpoint, "https://hbi.test"):
                        pass

    def test_auth_failure_stops_batch_and_blocks_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row(1), self.make_row(2)])
            checkpoint_path = directory / "checkpoint.json"
            checkpoint = Checkpoint.create(checkpoint_path, rows, digest, "https://hbi.test")
            api = FakeApi([(401, {"detail": "unauthorized"})])
            BatchRunner(rows, checkpoint, api).run()
            self.assertEqual(checkpoint.data["rows"]["sku-1"]["state"], "PREFLIGHT_FAILED")
            self.assertEqual(checkpoint.data["rows"]["sku-2"]["state"], "READY")
            resumed = Checkpoint.resume(checkpoint_path, digest, "https://hbi.test", rows)
            with self.assertRaisesRegex(RuntimeError, "Blocked rows"):
                BatchRunner(rows, resumed, FakeApi([])).run()

    def test_decision_file_rejects_unknown_source_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, (rows, digest) = self.load_rows(directory, [self.make_row()])
            decisions_path = directory / "decisions.json"
            decisions_path.write_text(json.dumps({"not-a-row": {"decision": "NEW", "reason": "reviewed"}}), encoding="utf-8")
            decisions = load_decisions(decisions_path)
            with self.assertRaisesRegex(ValueError, "unknown source_key"):
                validate_decision_keys(decisions, rows)


if __name__ == "__main__":
    unittest.main()
