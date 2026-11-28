"""Offline tests for the PR noise check; synthetic snapshots, no network calls."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("noise", Path(__file__).with_name("noise_check.py"))
noise = importlib.util.module_from_spec(spec)
spec.loader.exec_module(noise)


def user(login, kind="User"):
    return {"login": login, "type": kind}


def commit(message, parents=1):
    return {"commit": {"message": message}, "parents": [{"sha": str(i)} for i in range(parents)]}


def comment(login, when, body="Thanks", kind="User"):
    return {"user": user(login, kind), "created_at": when, "body": body}


def snapshot(commits=(), issue_comments=(), reviews=(), review_comments=()):
    return {
        "schema_version": 1, "repository": "owner/repo", "number": 7,
        "pr": {"user": user("me"), "base": {"ref": "main"}, "html_url": "https://github.com/owner/repo/pull/7"},
        "sections": {"commits": list(commits), "issue_comments": list(issue_comments),
                     "reviews": list(reviews), "review_comments": list(review_comments)},
        "errors": {},
    }


class MergeCommitTests(unittest.TestCase):
    def test_counts_base_merges_by_parents_and_message(self):
        result = noise.assess(snapshot(commits=[
            commit("fix: thing"),
            commit("Merge branch 'main' into fix", parents=2),
            commit("Merge remote-tracking branch 'origin/main' into fix", parents=2),
            commit("Merge branch 'main' into fix"),  # squashed-looking message, still a base merge
        ]))
        self.assertEqual(result["base_merges"], 3)
        self.assertIn("base_merges", result["flags"])

    def test_one_merge_is_not_noise(self):
        result = noise.assess(snapshot(commits=[commit("fix"), commit("Merge branch 'main' into fix", parents=2)]))
        self.assertEqual(result["base_merges"], 1)
        self.assertNotIn("base_merges", result["flags"])

    def test_merging_a_feature_branch_is_not_a_base_merge(self):
        result = noise.assess(snapshot(commits=[commit("Merge branch 'helper' into fix", parents=2)] * 3))
        self.assertEqual(result["base_merges"], 0)


class PingTests(unittest.TestCase):
    def test_trailing_author_comments_without_a_reply_are_flagged(self):
        result = noise.assess(snapshot(issue_comments=[
            comment("maint", "2026-11-01T00:00:00Z", "Please add a test"),
            comment("me", "2026-11-02T00:00:00Z", "Added the test"),
            comment("me", "2026-11-10T00:00:00Z", "Gentle ping @maint"),
        ]))
        self.assertEqual(result["unanswered_author_comments"], 2)
        self.assertEqual(result["nudges"], 1)
        self.assertIn("unanswered_comments", result["flags"])

    def test_a_maintainer_review_counts_as_a_reply(self):
        result = noise.assess(snapshot(
            issue_comments=[comment("me", "2026-11-02T00:00:00Z"), comment("me", "2026-11-03T00:00:00Z")],
            reviews=[{"user": user("maint"), "submitted_at": "2026-11-04T00:00:00Z", "state": "COMMENTED"}],
        ))
        self.assertEqual(result["unanswered_author_comments"], 0)
        self.assertEqual(result["flags"], [])

    def test_bot_replies_do_not_count(self):
        result = noise.assess(snapshot(issue_comments=[
            comment("me", "2026-11-02T00:00:00Z"),
            comment("vercel[bot]", "2026-11-02T01:00:00Z", "Deployment ready", kind="Bot"),
            comment("me", "2026-11-09T00:00:00Z", "Any update on this?"),
        ]))
        self.assertEqual(result["unanswered_author_comments"], 2)
        self.assertEqual(result["nudges"], 1)

    def test_a_single_status_update_is_fine(self):
        result = noise.assess(snapshot(issue_comments=[comment("me", "2026-11-02T00:00:00Z", "Rebased and green")]))
        self.assertEqual(result["flags"], [])

    def test_missing_sections_are_reported_not_guessed(self):
        snap = snapshot()
        del snap["sections"]["issue_comments"]
        snap["errors"]["issue_comments"] = "HTTP 502"
        result = noise.assess(snap)
        self.assertIn("issue_comments", result["incomplete"])


class CliTests(unittest.TestCase):
    def write(self, folder, name, data):
        path = Path(folder) / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return str(path)

    def test_reports_flags_with_advice_and_exit_code(self):
        noisy = snapshot(commits=[commit("Merge branch 'main' into x", parents=2)] * 2)
        with tempfile.TemporaryDirectory() as folder:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = noise.main([self.write(folder, "a.json", noisy), self.write(folder, "b.json", snapshot())])
        self.assertEqual(code, 1)
        text = out.getvalue()
        self.assertIn("owner/repo#7", text)
        self.assertIn("2 merge commits from main", text)
        self.assertIn("No noise found", text)

    def test_rejects_a_file_that_is_not_a_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = noise.main([self.write(folder, "x.json", {"hello": 1})])
        self.assertEqual(code, 2)
        self.assertIn("not a collect_pr_evidence snapshot", err.getvalue())


if __name__ == "__main__":
    unittest.main()
