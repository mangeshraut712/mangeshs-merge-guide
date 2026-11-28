"""Run the workflow's actual decision predicate against synthetic GitHub responses."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/merge-reviewed.yml"


@unittest.skipUnless(shutil.which("jq"), "workflow runner uses jq")
class MergePolicyTests(unittest.TestCase):
    def accepts(self, **changes):
        pr = dict(state="OPEN", isDraft=False, baseRefName="main", baseRefOid="base",
                  headRefOid="head", author={"login": "author"}, labels=[{"name": "merge-after-checks"}],
                  mergeStateStatus="CLEAN", latestReviews=[self.review()])
        pr.update(changes)
        script = WORKFLOW.read_text().split('--arg base "$BASE_SHA" \'', 1)[1].split("' <<<", 1)[0]
        result = subprocess.run(["jq", "-e", "--argjson", "approvals", json.dumps({"review-head": "head", "review-old": "old"}), "--arg", "head", "head", "--arg", "base", "base", script],
                                input=json.dumps(pr), text=True, capture_output=True)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        return result.returncode == 0

    def review(self, author="maintainer", state="APPROVED", sha="head", association="MEMBER"):
        return {"author": {"login": author}, "state": state, "id": "review-" + sha,
                "authorAssociation": association}

    def test_queued_and_independently_approved(self):
        self.assertTrue(self.accepts())

    def test_ineligible_contributions(self):
        for change in ({"labels": []}, {"isDraft": True}, {"baseRefName": "release"},
                       {"headRefOid": "new"}, {"baseRefOid": "new"}, {"mergeStateStatus": "BLOCKED"},
                       {"latestReviews": []}, {"latestReviews": [self.review(author="author")]},
                       {"latestReviews": [self.review(sha="old")]},
                       {"latestReviews": [self.review(association="NONE")]},
                       {"latestReviews": [self.review(), self.review(state="CHANGES_REQUESTED")]}):
            with self.subTest(change=change):
                self.assertFalse(self.accepts(**change))
