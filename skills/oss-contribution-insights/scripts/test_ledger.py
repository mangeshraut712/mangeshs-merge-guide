"""Offline tests for identity, lifecycle accounting, and non-destructive comparison."""
import contextlib
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("ledger", Path(__file__).with_name("ledger.py"))
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


def record(number, lifecycle="open", disposition="open"):
    return {"pull_request_node_id": f"PR_{number}", "repository": "example/project", "number": number, "url": f"https://github.com/example/project/pull/{number}", "github_lifecycle": lifecycle, "disposition": disposition, "discussion_coverage": "complete_available_api_entries"}


def data(*rows):
    return {"metadata": {"author": "example", "scope": "authored upstream PRs", "as_of": "2026-11-12"}, "records": list(rows)}


class LedgerTests(unittest.TestCase):
    def test_synthetic_example_integrity(self):
        example = Path(__file__).resolve().parents[1] / "assets/example-ledger.json"
        result = ledger.summary(ledger.load(example))
        self.assertEqual(result["pr_records"], 3)
        self.assertEqual(result["github_lifecycle"], {"github_merged": 1, "open": 1, "closed_without_github_merge": 1})

    def test_partial_credit_and_supersession_are_not_full_landings(self):
        result = ledger.summary(data(record(1, "github_merged", "github_merged"), record(2, "closed_without_github_merge", "verified_full_landed_elsewhere"), record(3, "closed_without_github_merge", "verified_partial_landed_elsewhere"), record(4, "closed_without_github_merge", "superseded")))
        self.assertEqual(result["native_or_full_landed_pr_records"], 2)
        self.assertEqual(result["partial_credit_pr_records"], 1)

    def test_open_pr_can_have_verified_external_landing(self):
        result = ledger.summary(data(record(1, "open", "verified_full_landed_elsewhere")))
        self.assertEqual(result["github_lifecycle"]["open"], 1)
        self.assertEqual(result["native_or_full_landed_pr_records"], 1)

    def test_duplicate_node_id_rejected(self):
        first, second = record(1), record(2)
        second["pull_request_node_id"] = first["pull_request_node_id"]
        with self.assertRaises(ledger.LedgerError):
            ledger.validate(data(first, second))

    def test_duplicate_alias_rejected_case_insensitively(self):
        first, second = record(1), record(2)
        second["repository"], second["number"] = "EXAMPLE/PROJECT", 1
        with self.assertRaises(ledger.LedgerError):
            ledger.validate(data(first, second))

    def test_missing_immutable_id_rejected(self):
        row = record(1)
        del row["pull_request_node_id"]
        with self.assertRaises(ledger.LedgerError):
            ledger.validate(data(row))

    def test_inconsistent_merge_rejected(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.validate(data(record(1, "github_merged", "superseded")))

    def test_absent_records_are_reported_not_deleted(self):
        old, new = data(record(1), record(2)), data(record(1))
        original = deepcopy(old)
        result = ledger.compare(old, new)
        self.assertEqual(result["absent_from_new"][0]["number"], 2)
        self.assertEqual(old, original)

    def test_post_merge_correction_preserves_merge(self):
        old = data(record(1, "github_merged", "github_merged"))
        new = deepcopy(old)
        new["records"][0]["post_landing"] = {"status": "correction_reported"}
        result = ledger.compare(old, new)
        self.assertIn("post_landing", result["changed"][0]["changes"])
        self.assertEqual(result["new_summary"]["native_or_full_landed_pr_records"], 1)

    def test_scope_change_is_not_silent(self):
        old, new = data(record(1)), data(record(1))
        new["metadata"]["scope"] = "all contributions"
        with self.assertRaises(ledger.LedgerError):
            ledger.compare(old, new)

    def test_unknown_annotations_and_renames_preserved(self):
        old = data(record(1))
        new = deepcopy(old)
        new["records"][0].update(repository="new-owner/project", custom_note="uncertain")
        result = ledger.compare(old, new)
        self.assertEqual(len(result["changed"]), 1)
        self.assertEqual(result["added"], [])
        self.assertEqual(result["changed"][0]["changes"]["custom_note"]["after"], "uncertain")

    def test_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "existing.json"
            path.write_text("original", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ledger.main(["diff", "missing1", "missing2", "--output", str(path)]), 1)
            self.assertEqual(path.read_text(), "original")

    def test_comparison_is_created_without_input_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            old, new, out = (Path(temp) / name for name in ("old.json", "new.json", "diff.json"))
            old.write_text(json.dumps(data(record(1))), encoding="utf-8")
            new.write_text(json.dumps(data(record(1), record(2))), encoding="utf-8")
            before = (old.read_bytes(), new.read_bytes())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ledger.main(["diff", str(old), str(new), "--output", str(out)]), 0)
            self.assertEqual(json.loads(out.read_text())["added"][0]["number"], 2)
            self.assertEqual(out.stat().st_mode & 0o777, 0o600)
            self.assertEqual((old.read_bytes(), new.read_bytes()), before)


if __name__ == "__main__":
    unittest.main()
