"""Offline tests for merge_stats; synthetic search pages, no network calls."""
import contextlib
import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("stats", Path(__file__).with_name("merge_stats.py"))
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


def item(repo, number, created, merged, comments=0):
    return {"repository_url": f"https://api.github.com/repos/{repo}", "number": number, "comments": comments,
            "created_at": created, "pull_request": {"merged_at": merged}}


ITEMS = [
    item("a/x", 1, "2026-11-01T00:00:00Z", "2026-11-01T12:00:00Z", 1),
    item("a/x", 2, "2026-11-02T00:00:00Z", "2026-11-05T00:00:00Z", 2),
    item("b/y", 3, "2026-11-01T00:00:00Z", "2026-11-11T00:00:00Z", 6),
    item("skip/z", 4, "2026-11-01T00:00:00Z", "2026-11-02T00:00:00Z"),
]


class SummaryTests(unittest.TestCase):
    def test_summarizes_merge_times_repos_and_discussion(self):
        s = stats.summarize(ITEMS, exclude_owners={"skip"})
        self.assertEqual(s["merged"], 3)
        self.assertEqual(s["repositories"], 2)
        self.assertEqual(s["days_to_merge"]["median"], 3.0)
        self.assertEqual(s["days_to_merge"]["max"], 10.0)
        self.assertEqual(s["merged_within"], {"1": 1, "7": 2, "30": 3})
        self.assertEqual(s["repositories_with_one_merge"], 1)
        self.assertEqual(s["by_comment_count"]["0-2"]["count"], 2)
        self.assertEqual(s["by_comment_count"]["3+"]["median_days"], 10.0)

    def test_open_prs_older_than_every_merge_are_counted(self):
        s = stats.summarize(ITEMS, exclude_owners=set(), open_items=[
            {"created_at": "2026-10-01T00:00:00Z"}, {"created_at": "2026-11-27T00:00:00Z"}], now="2026-11-28T00:00:00Z")
        self.assertEqual(s["open"], 2)
        self.assertEqual(s["open_older_than_slowest_merge"], 1)


class SearchTests(unittest.TestCase):
    def test_pages_through_read_only_search(self):
        calls = []

        def fake(command, **kwargs):
            calls.append(command)
            body = {"total_count": 3, "items": ITEMS[:2] if len(calls) == 1 else ITEMS[2:3]}
            return subprocess.CompletedProcess(command, 0, json.dumps(body), "")

        with patch.object(stats.subprocess, "run", side_effect=fake):
            found = stats.search("is:pr is:merged author:me")
        self.assertEqual(len(found), 3)
        self.assertEqual(calls[0][:6], ["gh", "api", "--hostname", "github.com", "--method", "GET"])
        self.assertIn("page=2", calls[1])

    def test_search_cap_is_reported(self):
        body = json.dumps({"total_count": 1500, "items": []})
        with patch.object(stats.subprocess, "run", return_value=subprocess.CompletedProcess(["gh"], 0, body, "")):
            with self.assertRaisesRegex(stats.StatsError, "1000"):
                stats.search("q")


class CliTests(unittest.TestCase):
    def test_prints_summary(self):
        out = io.StringIO()
        with patch.object(stats, "search", side_effect=[ITEMS, []]), contextlib.redirect_stdout(out):
            self.assertEqual(stats.main(["--author", "me", "--exclude-owner", "skip"]), 0)
        self.assertIn("3 merged PRs in 2 repositories", out.getvalue())


if __name__ == "__main__":
    unittest.main()
