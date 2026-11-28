#!/usr/bin/env python3
"""Summarize how an author's merged pull requests landed, using read-only gh REST search."""
import argparse
import datetime as dt
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter

LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
SEARCH_CAP = 1000


class StatsError(RuntimeError):
    pass


def _time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def search(query):
    found, page = [], 1
    while True:
        command = ["gh", "api", "--hostname", "github.com", "--method", "GET", "search/issues",
                   "-f", f"q={query}", "-f", "per_page=100", "-f", f"page={page}"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        except FileNotFoundError as exc:
            raise StatsError("GitHub CLI (gh) is not installed or not on PATH. Install it from https://cli.github.com, then run `gh auth login`.") from exc
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise StatsError(f"GitHub read failed: {type(exc).__name__}") from exc
        if result.returncode:
            raise StatsError((result.stderr.strip() or "gh api failed")[:600])
        try:
            body = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise StatsError("gh returned invalid JSON") from exc
        if body.get("total_count", 0) > SEARCH_CAP:
            raise StatsError(f"Search matched more than {SEARCH_CAP} results; GitHub only returns {SEARCH_CAP}. Narrow it with --since.")
        if body.get("incomplete_results"):
            raise StatsError("GitHub returned incomplete search results (its search timed out). Try again, or narrow it with --since.")
        total, items = body.get("total_count", 0), body.get("items") or []
        found += items
        if len(found) >= total:
            return found
        if not items:
            raise StatsError(f"Search stopped at {len(found)} of {total} results. Try again before trusting the totals.")
        page += 1


def summarize(items, exclude_owners, open_items=(), now=None):
    rows = []
    for i in items:
        repo = i["repository_url"].split("/repos/", 1)[1]
        merged = (i.get("pull_request") or {}).get("merged_at")
        if repo.split("/")[0] in exclude_owners or not merged:
            continue
        rows.append({"repo": repo, "days": (_time(merged) - _time(i["created_at"])).total_seconds() / 86400,
                     "comments": i.get("comments", 0)})
    days = sorted(r["days"] for r in rows)
    per_repo = Counter(r["repo"] for r in rows)

    def group(selected):
        values = [r["days"] for r in selected]
        return {"count": len(values), "median_days": round(statistics.median(values), 1) if values else None}

    summary = {
        "merged": len(rows),
        "repositories": len(per_repo),
        "repositories_with_one_merge": sum(v == 1 for v in per_repo.values()),
        "days_to_merge": {"median": round(statistics.median(days), 1), "max": round(days[-1], 1)} if days else {},
        "merged_within": {str(n): sum(d <= n for d in days) for n in (1, 7, 30)},
        "by_comment_count": {"0-2": group([r for r in rows if r["comments"] <= 2]),
                             "3+": group([r for r in rows if r["comments"] > 2])},
    }
    if open_items:
        now = _time(now) if isinstance(now, str) else (now or dt.datetime.now(dt.timezone.utc))
        ages = [(now - _time(o["created_at"])).total_seconds() / 86400 for o in open_items]
        summary["open"] = len(ages)
        summary["open_older_than_slowest_merge"] = sum(a > days[-1] for a in ages) if days else None
    return summary


def render(s):
    lines = [f"{s['merged']} merged PRs in {s['repositories']} repositories ({s['repositories_with_one_merge']} with exactly one)."]
    if s["days_to_merge"]:
        w = s["merged_within"]
        lines.append(f"Days from opening to merge: median {s['days_to_merge']['median']}, slowest {s['days_to_merge']['max']}.")
        lines.append(f"Merged within 1 day: {w['1']}, within 7 days: {w['7']}, within 30 days: {w['30']}.")
        low, high = s["by_comment_count"]["0-2"], s["by_comment_count"]["3+"]
        lines.append(f"0-2 comments: {low['count']} PRs, median {low['median_days']} days; 3+ comments: {high['count']} PRs, median {high['median_days']} days.")
    if "open" in s:
        lines.append(f"Open now: {s['open']}, of which {s['open_older_than_slowest_merge']} are older than the slowest merge.")
        if s["open_older_than_slowest_merge"] and s["days_to_merge"] and s.get("author"):
            days = max(1, math.ceil(s["days_to_merge"]["max"]))
            lines.append(f"Next: see which ones with `open_pr_triage.py --author {s['author']} --stale-days {days}`.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author", required=True, help="GitHub login")
    parser.add_argument("--exclude-owner", action="append", default=[], help="Skip repositories under this owner (repeatable)")
    parser.add_argument("--since", help="Only PRs created on or after YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Print the summary as JSON")
    args = parser.parse_args(argv)
    if not LOGIN.fullmatch(args.author) or not all(LOGIN.fullmatch(o) for o in args.exclude_owner):
        parser.error("Provide valid GitHub logins")
    if args.since and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.since):
        parser.error("--since must be YYYY-MM-DD")
    scope = f"is:pr author:{args.author} -user:{args.author}" + "".join(f" -user:{o}" for o in args.exclude_owner)
    scope += f" created:>={args.since}" if args.since else ""
    try:
        merged = search(scope + " is:merged")
        still_open = search(scope + " is:open")
    except StatsError as exc:
        print(f"Stats failed: {exc}", file=sys.stderr)
        return 1
    summary = summarize(merged, set(args.exclude_owner), still_open)
    summary["author"] = args.author
    print(json.dumps(summary, indent=2) if args.json else render(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
