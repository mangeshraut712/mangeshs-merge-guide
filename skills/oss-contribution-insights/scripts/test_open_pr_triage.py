"""Offline contract tests for open-PR triage; synthetic data, no network calls."""
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

spec = importlib.util.spec_from_file_location("triage", Path(__file__).with_name("open_pr_triage.py"))
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)

NOW = "2026-11-28T00:00:00Z"


def node(**overrides):
    base = {
        "url": "https://github.com/owner/repo/pull/7",
        "number": 7,
        "title": "fix: example",
        "isDraft": False,
        "createdAt": "2026-11-01T00:00:00Z",
        "updatedAt": "2026-11-27T00:00:00Z",
        "repository": {"nameWithOwner": "owner/repo"},
        "author": {"login": "me"},
        "reviewDecision": "REVIEW_REQUIRED",
        "mergeable": "MERGEABLE",
        "latestReviews": {"nodes": []},
        "commits": {"nodes": [{"commit": {"committedDate": "2026-11-20T00:00:00Z", "statusCheckRollup": {
            "state": "SUCCESS", "contexts": {"nodes": [{"__typename": "CheckRun", "name": "unit", "conclusion": "SUCCESS", "status": "COMPLETED"}]}}}}]},
        "comments": {"nodes": []},
    }
    base.update(overrides)
    return base


def bucket(**overrides):
    return triage.classify(triage.normalize(node(**overrides)), now=NOW, stale_days=30)["bucket"]


class ClassifyTests(unittest.TestCase):
    def test_unreviewed_green_pr_waits_for_review(self):
        self.assertEqual(bucket(), "awaiting_review")

    def test_approved_pr_is_ready_to_merge(self):
        self.assertEqual(bucket(reviewDecision="APPROVED"), "approved")

    def test_unanswered_change_request_needs_the_author(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-25T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestReviews=reviews), "address_review")

    def test_change_request_answered_by_a_later_commit_waits_for_rereview(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-10T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestReviews=reviews), "awaiting_rereview")

    def test_change_request_answered_by_an_author_comment_waits_for_rereview(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-25T00:00:00Z", "author": {"login": "maint"}}]}
        comments = {"nodes": [{"author": {"login": "me"}, "createdAt": "2026-11-26T00:00:00Z"}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestReviews=reviews, comments=comments), "awaiting_rereview")

    def test_conflict_needs_the_author_before_anything_else(self):
        self.assertEqual(bucket(mergeable="CONFLICTING", reviewDecision="APPROVED"), "resolve_conflict")

    def test_failing_checks_list_the_failing_names(self):
        rollup = {"state": "FAILURE", "contexts": {"nodes": [
            {"__typename": "StatusContext", "context": "Vercel", "state": "FAILURE"},
            {"__typename": "CheckRun", "name": "unit", "conclusion": "SUCCESS", "status": "COMPLETED"},
        ]}}
        pr = triage.normalize(node(commits={"nodes": [{"commit": {"committedDate": "2026-11-20T00:00:00Z", "statusCheckRollup": rollup}}]}))
        result = triage.classify(pr, now=NOW, stale_days=30)
        self.assertEqual(result["bucket"], "checks_failing")
        self.assertEqual(result["failing_checks"], ["Vercel"])

    def test_missing_rollup_is_not_reported_as_failing(self):
        pr = triage.normalize(node(commits={"nodes": [{"commit": {"committedDate": "2026-11-20T00:00:00Z", "statusCheckRollup": None}}]}))
        self.assertEqual(triage.classify(pr, now=NOW, stale_days=30)["bucket"], "awaiting_review")

    def test_draft_is_kept_separate(self):
        self.assertEqual(bucket(isDraft=True, reviewDecision="APPROVED"), "draft")

    def test_stale_flag_uses_last_update(self):
        pr = triage.normalize(node(updatedAt="2026-10-01T00:00:00Z"))
        self.assertTrue(triage.classify(pr, now=NOW, stale_days=30)["stale"])
        self.assertFalse(triage.classify(triage.normalize(node()), now=NOW, stale_days=30)["stale"])


class CollectionTests(unittest.TestCase):
    def page(self, nodes, has_next, cursor):
        return {"data": {"search": {"pageInfo": {"hasNextPage": has_next, "endCursor": cursor}, "nodes": nodes}}}

    def test_paginates_with_read_only_graphql(self):
        pages = [self.page([node(number=1)], True, "c1"), self.page([node(number=2), {}], False, None)]
        calls = []

        def fake_run(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, json.dumps(pages[len(calls) - 1]), "")

        with patch.object(triage.subprocess, "run", side_effect=fake_run):
            nodes = triage.fetch_open_prs("me", include_own=False)
        self.assertEqual([n["number"] for n in nodes], [1, 2])
        self.assertEqual(calls[0][:4], ["gh", "api", "graphql", "--hostname"])
        joined = " ".join(calls[0])
        self.assertIn("is:pr is:open author:me -user:me", joined)
        self.assertNotIn("mutation", joined)
        self.assertIn("after=c1", " ".join(calls[1]))

    def test_gh_failure_is_reported(self):
        failed = subprocess.CompletedProcess(["gh"], 1, "", "HTTP 401: Bad credentials")
        with patch.object(triage.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(triage.TriageError, "Bad credentials"):
                triage.fetch_open_prs("me", include_own=False)

    def test_graphql_errors_are_reported(self):
        body = json.dumps({"errors": [{"message": "rate limited"}]})
        with patch.object(triage.subprocess, "run", return_value=subprocess.CompletedProcess(["gh"], 0, body, "")):
            with self.assertRaisesRegex(triage.TriageError, "rate limited"):
                triage.fetch_open_prs("me", include_own=False)


class CliTests(unittest.TestCase):
    def run_cli(self, argv, nodes):
        stdout = io.StringIO()
        with patch.object(triage, "fetch_open_prs", return_value=nodes), contextlib.redirect_stdout(stdout):
            code = triage.main(argv)
        return code, stdout.getvalue()

    def test_prints_report_grouped_by_next_owner(self):
        code, out = self.run_cli(["--author", "me", "--now", NOW], [node(), node(number=8, reviewDecision="APPROVED")])
        self.assertEqual(code, 0)
        self.assertIn("Approved, waiting for a maintainer to merge (1)", out)
        self.assertIn("Waiting for a first review (1)", out)
        self.assertLess(out.index("Approved"), out.index("Waiting for a first review"))

    def test_writes_private_json_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "triage.json"
            code, _ = self.run_cli(["--author", "me", "--now", NOW, "--output", str(path)], [node()])
            self.assertEqual(code, 0)
            report = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(report["counts"]["awaiting_review"], 1)
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(SystemExit):
                self.run_cli(["--author", "me", "--output", str(path)], [node()])

    def test_rejects_an_invalid_login(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            triage.main(["--author", "bad login; rm -rf"])


if __name__ == "__main__":
    unittest.main()
