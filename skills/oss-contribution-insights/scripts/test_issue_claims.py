"""Offline tests for issue_claims; synthetic GitHub responses, no network calls."""
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location("claims", Path(__file__).with_name("issue_claims.py"))
claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims)


def user(login, kind="User"):
    return {"login": login, "type": kind}


def comment(login, when, body, association="NONE", kind="User"):
    return {"user": user(login, kind), "created_at": when, "body": body, "author_association": association}


ISSUE = {"state": "open", "assignees": [], "user": user("reporter"), "labels": [{"name": "bug"}], "milestone": None}


class AssessTests(unittest.TestCase):
    def test_unanswered_offer_to_work_is_a_soft_claim(self):
        comments = [comment("helper", "2026-11-28T02:48:01Z", "Could I open a PR with a regression test for this?")]
        result = claims.assess(ISSUE, comments, [], me="me")
        self.assertEqual(result["verdict"], "ask_first")
        self.assertEqual(result["offers"][0]["login"], "helper")
        self.assertFalse(result["offers"][0]["maintainer_replied"])

    def test_offer_answered_by_a_maintainer_is_still_reported_with_the_reply(self):
        comments = [comment("helper", "2026-11-01T00:00:00Z", "I'd like to work on this."),
                    comment("maint", "2026-11-02T00:00:00Z", "Go ahead!", association="MEMBER")]
        result = claims.assess(ISSUE, comments, [], me="me")
        self.assertEqual(result["verdict"], "ask_first")
        self.assertTrue(result["offers"][0]["maintainer_replied"])

    def test_assignee_or_open_linked_pr_means_taken(self):
        self.assertEqual(claims.assess(dict(ISSUE, assignees=[user("other")]), [], [], me="me")["verdict"], "taken")
        linked = [{"number": 9, "user": "other", "state": "open", "repository": "o/r"}]
        self.assertEqual(claims.assess(ISSUE, [], linked, me="me")["verdict"], "taken")

    def test_own_assignment_comments_and_prs_and_bots_are_ignored(self):
        comments = [comment("me", "2026-11-01T00:00:00Z", "I'm working on this."),
                    comment("dependabot[bot]", "2026-11-01T00:00:00Z", "I will open a PR", kind="Bot"),
                    comment("someone", "2026-11-01T00:00:00Z", "Same problem here, any workaround?")]
        linked = [{"number": 9, "user": "me", "state": "open", "repository": "o/r"},
                  {"number": 8, "user": "other", "state": "closed", "repository": "o/r"}]
        result = claims.assess(dict(ISSUE, assignees=[user("me")]), comments, linked, me="me")
        self.assertEqual(result["verdict"], "clear")

    def test_closed_issue_or_triage_label_is_reported(self):
        self.assertEqual(claims.assess(dict(ISSUE, state="closed"), [], [], me="me")["verdict"], "closed")
        result = claims.assess(dict(ISSUE, labels=[{"name": "needs-triage"}]), [], [], me="me")
        self.assertIn("needs-triage", result["notes"][0])

    def test_linked_prs_come_from_cross_reference_events(self):
        timeline = [{"event": "cross-referenced", "source": {"issue": {"number": 9, "state": "open", "user": user("other"),
                     "pull_request": {}, "repository": {"full_name": "o/r"}}}},
                    {"event": "cross-referenced", "source": {"issue": {"number": 3, "state": "open", "user": user("x")}}},
                    {"event": "labeled"}]
        self.assertEqual(claims.linked_prs(timeline), [{"number": 9, "user": "other", "state": "open", "repository": "o/r"}])


class CliTests(unittest.TestCase):
    def run_cli(self, argv, issue, comments, timeline):
        def fake(endpoint, paginated=False):
            if "/comments" in endpoint:
                return [comments]
            if "/timeline" in endpoint:
                return [timeline]
            return issue
        out = io.StringIO()
        with patch.object(claims, "api", side_effect=fake), contextlib.redirect_stdout(out):
            code = claims.main(argv)
        return code, out.getvalue()

    def test_reports_offer_and_exits_1(self):
        comments = [comment("helper", "2026-11-28T02:48:01Z", "Can I take this one?")]
        code, out = self.run_cli(["o/r", "656", "--me", "me"], ISSUE, comments, [])
        self.assertEqual(code, 1)
        self.assertIn("helper offered to work on it", out)
        self.assertIn("no maintainer reply", out)

    def test_clear_issue_exits_0(self):
        code, out = self.run_cli(["o/r", "656", "--me", "me"], ISSUE, [], [])
        self.assertEqual(code, 0)
        self.assertIn("No one else", out)

    def test_rejects_bad_arguments(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            claims.main(["not-a-repo", "1", "--me", "me"])


if __name__ == "__main__":
    unittest.main()
