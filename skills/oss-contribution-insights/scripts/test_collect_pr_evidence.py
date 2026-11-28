"""Offline contract tests; no account access or network calls."""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("collector", Path(__file__).with_name("collect_pr_evidence.py"))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
SHA = "a" * 40


def good_response(command, **kwargs):
    assert command[:6] == ["gh", "api", "--hostname", "github.com", "--method", "GET"]
    endpoint = command[6]
    if endpoint.endswith("/pulls/7"):
        content = {"head": {"sha": SHA}, "state": "open", "merged": False, "commits": 2}
    elif "/actions/runs?" in endpoint:
        assert f"head_sha={SHA}&per_page=100" in endpoint
        content = [{"workflow_runs": [{"head_sha": SHA, "conclusion": "action_required"}]}]
    elif "/check-runs?" in endpoint:
        content = [{"check_runs": [{"name": "unit", "conclusion": "success"}]}]
    else:
        content = [[{"id": 1}], [{"id": 2}]]
    output = "\n".join(json.dumps(page) for page in content) if "--paginate" in command else json.dumps(content)
    return subprocess.CompletedProcess(command, 0, output, "")


class FriendlyErrorTests(unittest.TestCase):
    def test_output_is_decoded_as_utf8(self):
        ok = subprocess.CompletedProcess(["gh"], 0, json.dumps({"title": "\u2b50"}), "")
        with patch.object(collector.subprocess, "run", return_value=ok) as run:
            collector.api("repos/o/r/issues/1")
        self.assertEqual(run.call_args.kwargs.get("encoding"), "utf-8")

    def test_missing_gh_is_explained(self):
        with patch.object(collector.subprocess, "run", side_effect=FileNotFoundError("gh")):
            with self.assertRaisesRegex(collector.CollectionError, "cli.github.com"):
                collector.api("repos/o/r/pulls/1")

    def test_missing_output_folder_is_explained(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
            collector.main(["owner/repo", "7", "--output", "/no/such/folder/s.json"])
        self.assertIn("does not exist", err.getvalue())


class CollectorTests(unittest.TestCase):
    def test_all_reads_and_pagination(self):
        with patch.object(collector.subprocess, "run", side_effect=good_response) as run:
            result = collector.collect("owner/repo", 7)
        self.assertEqual(run.call_count, 9)
        self.assertTrue(result["collection_complete"])
        self.assertEqual(len(result["sections"]["reviews"]), 2)
        self.assertEqual(result["sections"]["check_runs"][0]["name"], "unit")
        self.assertEqual(result["sampled_head_sha"], SHA)
        self.assertEqual(result["sections"]["workflow_runs"][0]["conclusion"], "action_required")

    def test_commit_endpoint_cap_is_partial(self):
        def capped_response(command, **kwargs):
            response = good_response(command, **kwargs)
            if command[6].endswith("/pulls/7"):
                response.stdout = json.dumps({"head": {"sha": SHA}, "state": "open", "commits": 300})
            elif "/commits?" in command[6]:
                response.stdout = json.dumps([{"sha": str(index)} for index in range(250)])
            return response
        with patch.object(collector.subprocess, "run", side_effect=capped_response):
            result = collector.collect("owner/repo", 7)
        self.assertFalse(result["collection_complete"])
        self.assertIn("250 of 300", result["errors"]["commits_coverage"])

    def test_missing_commit_count_does_not_claim_complete_history(self):
        def missing_count(command, **kwargs):
            response = good_response(command, **kwargs)
            if command[6].endswith("/pulls/7"):
                response.stdout = json.dumps({"head": {"sha": SHA}, "state": "open"})
            return response
        with patch.object(collector.subprocess, "run", side_effect=missing_count):
            result = collector.collect("owner/repo", 7)
        self.assertFalse(result["collection_complete"])
        self.assertIn("commits_coverage", result["errors"])

    def test_pagination_works_without_newer_slurp_flag(self):
        with patch.object(collector.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '[{"id": 1}]\n[{"id": 2}]\n', "")) as run:
            self.assertEqual(collector.pages("repos/owner/repo/pulls/7/reviews"), [{"id": 1}, {"id": 2}])
        self.assertNotIn("--slurp", run.call_args.args[0])

    def test_empty_pagination_is_not_complete(self):
        with patch.object(collector.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
            with self.assertRaises(collector.CollectionError):
                collector.pages("repos/owner/repo/pulls/7/reviews")

    def test_partial_error_does_not_hide_other_sections(self):
        def fail_reviews(command, **kwargs):
            if "/reviews?" in command[6]:
                return subprocess.CompletedProcess(command, 1, "", "API access forbidden")
            return good_response(command, **kwargs)
        with patch.object(collector.subprocess, "run", side_effect=fail_reviews):
            result = collector.collect("owner/repo", 7)
        self.assertFalse(result["collection_complete"])
        self.assertIn("reviews", result["errors"])
        self.assertIn("check_runs", result["sections"])

    def test_racing_head_is_flagged(self):
        calls = 0
        def change_head(command, **kwargs):
            nonlocal calls
            response = good_response(command, **kwargs)
            if command[6].endswith("/pulls/7"):
                calls += 1
                if calls == 2:
                    response.stdout = json.dumps({"head": {"sha": "b" * 40}, "state": "open"})
            return response
        with patch.object(collector.subprocess, "run", side_effect=change_head):
            result = collector.collect("owner/repo", 7)
        self.assertTrue(result["head_changed_during_collection"])
        self.assertFalse(result["collection_complete"])

    def test_invalid_api_json_is_reported(self):
        with patch.object(collector.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "bad", "")):
            with self.assertRaises(collector.CollectionError):
                collector.collect("owner/repo", 7)

    def test_timeout_is_reported(self):
        with patch.object(collector.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 120)):
            with self.assertRaises(collector.CollectionError):
                collector.collect("owner/repo", 7)

    def test_initial_failure_creates_no_file(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "snapshot.json"
            with patch.object(collector, "collect", side_effect=collector.CollectionError("No access")), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(collector.main(["owner/repo", "7", "--output", str(output)]), 1)
            self.assertFalse(output.exists())

    def test_existing_output_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "snapshot.json"
            output.write_text("original", encoding="utf-8")
            with patch.object(collector, "collect") as collect, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    collector.main(["owner/repo", "7", "--output", str(output)])
            self.assertEqual(output.read_text(), "original")
            collect.assert_not_called()

    def test_dot_segment_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "snapshot.json"
            for repository in ("owner/..", "owner/."):
                with patch.object(collector, "collect") as collect, contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        collector.main([repository, "7", "--output", str(output)])
                collect.assert_not_called()
            self.assertFalse(output.exists())

    def test_partial_file_has_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "snapshot.json"
            partial = {"collection_complete": False, "errors": {"reviews": "blocked"}}
            with patch.object(collector, "collect", return_value=partial), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(collector.main(["owner/repo", "7", "--output", str(output)]), 2)
            self.assertEqual(json.loads(output.read_text()), partial)
            if os.name == "posix":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
