#!/usr/bin/env python3
"""Save a read-only GitHub PR evidence snapshot using authenticated gh."""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path


class CollectionError(RuntimeError):
    pass


def api(endpoint, paginated=False):
    command = ["gh", "api", "--hostname", "github.com", "--method", "GET", endpoint]
    if paginated:
        command.append("--paginate")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectionError(f"GitHub read failed: {type(exc).__name__}") from exc
    if result.returncode:
        # Preserve useful diagnostics without collecting credentials or environment.
        raise CollectionError((result.stderr.strip() or "gh api failed")[:600])
    try:
        if not paginated:
            return json.loads(result.stdout)
        # Older gh versions emit consecutive JSON values and have no --slurp.
        remainder = result.stdout.lstrip()
        if not remainder:
            raise CollectionError("gh returned no pagination data")
        decoder = json.JSONDecoder()
        result_pages = []
        while remainder:
            page, end = decoder.raw_decode(remainder)
            result_pages.append(page)
            remainder = remainder[end:].lstrip()
        return result_pages
    except json.JSONDecodeError as exc:
        raise CollectionError("gh returned invalid JSON") from exc


def pages(endpoint, key=None):
    data = api(endpoint + "?per_page=100", paginated=True)
    if not isinstance(data, list):
        raise CollectionError("Expected a paginated JSON array")
    flattened = []
    for page in data:
        rows = page.get(key) if key and isinstance(page, dict) else page
        if not isinstance(rows, list):
            raise CollectionError(f"Unexpected pagination shape for {endpoint}")
        flattened.extend(rows)
    return flattened


def collect(repo, number):
    route = f"repos/{repo}/pulls/{number}"
    pr = api(route)
    if not isinstance(pr, dict) or not isinstance(pr.get("head"), dict):
        raise CollectionError("Initial PR metadata is missing a head")
    sha = pr["head"].get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        raise CollectionError("Initial PR metadata has an invalid head SHA")
    snapshot = {
        "schema_version": 1,
        "repository": repo,
        "number": number,
        "sampled_head_sha": sha,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "pr": pr,
        "sections": {},
        "errors": {},
    }
    endpoints = {
        "issue_comments": (f"repos/{repo}/issues/{number}/comments", None),
        "reviews": (route + "/reviews", None),
        "review_comments": (route + "/comments", None),
        "commits": (route + "/commits", None),
        "check_runs": (f"repos/{repo}/commits/{sha}/check-runs", "check_runs"),
        "commit_statuses": (f"repos/{repo}/commits/{sha}/statuses", None),
    }
    for section, (endpoint, key) in endpoints.items():
        try:
            snapshot["sections"][section] = pages(endpoint, key)
        except CollectionError as exc:
            snapshot["errors"][section] = str(exc)
    if "commits" in snapshot["sections"]:
        expected_commits = pr.get("commits")
        collected_commits = len(snapshot["sections"]["commits"])
        if not isinstance(expected_commits, int) or isinstance(expected_commits, bool) or expected_commits < 0:
            snapshot["errors"]["commits_coverage"] = "PR metadata commit count is unavailable; full commit coverage is not established."
        elif collected_commits != expected_commits:
            snapshot["errors"]["commits_coverage"] = (
                f"Collected {collected_commits} of {expected_commits} reported commits. "
                "The PR commits endpoint can cap results at 250; history is not complete."
            )
    try:
        ending = api(route)
        if not isinstance(ending, dict) or not isinstance(ending.get("head"), dict):
            raise CollectionError("Final PR metadata is missing a head")
        snapshot["ending_pr"] = {
            field: ending.get(field)
            for field in ("state", "merged", "merged_at", "closed_at", "draft", "merge_commit_sha")
        }
        snapshot["ending_head_sha"] = ending["head"].get("sha")
        snapshot["head_changed_during_collection"] = sha != snapshot["ending_head_sha"]
        if snapshot["head_changed_during_collection"]:
            snapshot["errors"]["head"] = "Head changed during collection; refresh before assessing checks."
    except CollectionError as exc:
        snapshot["errors"]["ending_pr"] = str(exc)
    snapshot["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    snapshot["collection_complete"] = not snapshot["errors"]
    return snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="GitHub OWNER/REPO")
    parser.add_argument("number", type=int, help="Positive PR number")
    parser.add_argument("--output", required=True, type=Path, help="New private snapshot file; never overwritten")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9_.-]+", args.repository) or args.number < 1:
        parser.error("Provide OWNER/REPO and a positive PR number")
    if args.output.exists():
        parser.error("Output already exists; choose a new file")
    try:
        result = collect(args.repository, args.number)
        with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
    except (CollectionError, OSError) as exc:
        print(f"Snapshot failed: {exc}", file=sys.stderr)
        return 1
    print(f"Saved {'complete' if result['collection_complete'] else 'partial'} snapshot: {args.output}")
    if result["errors"]:
        print("Incomplete sections: " + ", ".join(result["errors"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
