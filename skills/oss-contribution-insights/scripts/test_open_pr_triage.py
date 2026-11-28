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
        "latestOpinionatedReviews": {"nodes": []},
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
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestOpinionatedReviews=reviews), "address_review")

    def test_change_request_answered_by_a_later_commit_waits_for_rereview(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-10T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestOpinionatedReviews=reviews), "awaiting_rereview")

    def test_change_request_answered_by_an_author_comment_waits_for_rereview(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-25T00:00:00Z", "author": {"login": "maint"}}]}
        comments = {"nodes": [{"author": {"login": "me"}, "createdAt": "2026-11-26T00:00:00Z"}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestOpinionatedReviews=reviews, comments=comments), "awaiting_rereview")

    def test_answered_change_request_with_failing_checks_needs_the_author(self):
        reviews = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-10T00:00:00Z", "author": {"login": "maint"}}]}
        rollup = {"state": "FAILURE", "contexts": {"nodes": [{"__typename": "CheckRun", "name": "unit", "conclusion": "FAILURE", "status": "COMPLETED"}]}}
        commits = {"nodes": [{"commit": {"committedDate": "2026-11-20T00:00:00Z", "statusCheckRollup": rollup}}]}
        self.assertEqual(bucket(reviewDecision="CHANGES_REQUESTED", latestOpinionatedReviews=reviews, commits=commits), "checks_failing")

    def test_reviews_count_when_the_branch_requires_none(self):
        approved = {"nodes": [{"state": "APPROVED", "submittedAt": "2026-11-25T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(bucket(reviewDecision=None, latestOpinionatedReviews=approved), "approved")
        changes = {"nodes": [{"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-25T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(bucket(reviewDecision=None, latestOpinionatedReviews=changes), "address_review")

    def test_query_ignores_comment_only_reviews(self):
        self.assertIn("latestOpinionatedReviews", triage.QUERY)
        self.assertNotIn("latestReviews(", triage.QUERY)

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


class NoiseSignalTests(unittest.TestCase):
    def signals(self, **overrides):
        return triage.classify(triage.normalize(node(**overrides)), now=NOW, stale_days=30)["noise"]

    def test_repeated_base_merges_are_flagged(self):
        recent = {"nodes": [{"commit": {"messageHeadline": "Merge branch 'main' into fix"}}] * 3 + [{"commit": {"messageHeadline": "fix"}}]}
        self.assertEqual(self.signals(baseRefName="main", recent=recent), ["3 merges from main"])

    def test_unanswered_author_comments_are_flagged_and_bots_ignored(self):
        comments = {"nodes": [
            {"author": {"login": "maint", "__typename": "User"}, "createdAt": "2026-11-01T00:00:00Z"},
            {"author": {"login": "me", "__typename": "User"}, "createdAt": "2026-11-02T00:00:00Z"},
            {"author": {"login": "vercel", "__typename": "Bot"}, "createdAt": "2026-11-02T01:00:00Z"},
            {"author": {"login": "me", "__typename": "User"}, "createdAt": "2026-11-09T00:00:00Z"},
        ]}
        self.assertEqual(self.signals(comments=comments), ["2 comments with no reply"])

    def test_a_maintainer_review_after_the_comments_counts_as_a_reply(self):
        comments = {"nodes": [{"author": {"login": "me", "__typename": "User"}, "createdAt": t} for t in ("2026-11-02T00:00:00Z", "2026-11-03T00:00:00Z")]}
        reviews = {"nodes": [{"state": "APPROVED", "submittedAt": "2026-11-04T00:00:00Z", "author": {"login": "maint"}}]}
        self.assertEqual(self.signals(comments=comments, latestOpinionatedReviews=reviews), [])

    def test_a_comment_only_review_counts_as_a_reply(self):
        comments = {"nodes": [{"author": {"login": "me", "__typename": "User"}, "createdAt": t} for t in ("2026-11-02T00:00:00Z", "2026-11-03T00:00:00Z")]}
        all_reviews = {"nodes": [{"submittedAt": "2026-11-04T00:00:00Z", "author": {"login": "maint", "__typename": "User"}}]}
        self.assertEqual(self.signals(comments=comments, allReviews=all_reviews), [])

    def test_quiet_pr_has_no_noise(self):
        self.assertEqual(self.signals(), [])

    def test_report_shows_noise_next_to_the_pr(self):
        recent = {"nodes": [{"commit": {"messageHeadline": "Merge branch 'main' into fix"}}] * 2}
        out = triage.render(triage.build_report([node(baseRefName="main", recent=recent)], NOW, 30))
        self.assertIn("[noise: 2 merges from main]", out)


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

    def test_output_is_decoded_as_utf8(self):
        page = self.page([node(title="fix: emoji \U0001F60D")], False, None)
        with patch.object(triage.subprocess, "run", return_value=subprocess.CompletedProcess(["gh"], 0, json.dumps(page), "")) as run:
            nodes = triage.fetch_open_prs("me", include_own=False)
        self.assertEqual(run.call_args.kwargs.get("encoding"), "utf-8")
        self.assertEqual(nodes[0]["title"], "fix: emoji \U0001F60D")

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

    def test_missing_output_folder_is_explained(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
            triage.main(["--author", "me", "--output", "/no/such/folder/t.json"])
        self.assertIn("does not exist", err.getvalue())

    def test_missing_gh_is_explained(self):
        with patch.object(triage.subprocess, "run", side_effect=FileNotFoundError("gh")):
            with self.assertRaisesRegex(triage.TriageError, "cli.github.com"):
                triage.fetch_open_prs("me", include_own=False)

    def test_rejects_an_invalid_login(self):
        for login in ("bad login; rm -rf", "trailing-", "-leading"):
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                triage.main(["--author", login])


if __name__ == "__main__":
    unittest.main()
