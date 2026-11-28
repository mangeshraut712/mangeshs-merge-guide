#!/usr/bin/env python3
"""Sort your open pull requests by who has to act next, using read-only gh GraphQL queries."""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from noise_check import is_base_merge

QUERY = """
query($q: String!, $after: String) {
  search(query: $q, type: ISSUE, first: 50, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        url number title isDraft createdAt updatedAt baseRefName
        repository { nameWithOwner }
        author { login }
        reviewDecision mergeable
        latestOpinionatedReviews(first: 50) { nodes { state submittedAt author { login } } }
        commits(last: 1) { nodes { commit { committedDate statusCheckRollup { state
          contexts(first: 50) { nodes { __typename
            ... on CheckRun { name conclusion status }
            ... on StatusContext { context state } } } } } } }
        recent: commits(last: 30) { nodes { commit { messageHeadline } } }
        comments(last: 30) { nodes { author { login __typename } createdAt } }
      }
    }
  }
}
"""

# Ordered by who acts next: the author first, then maintainers.
BUCKETS = {
    "resolve_conflict": "Merge conflict: you need to act",
    "address_review": "Changes requested and not yet answered: you need to act",
    "checks_failing": "Checks failing: check whether the failure is yours",
    "approved": "Approved, waiting for a maintainer to merge",
    "awaiting_rereview": "Review answered, waiting for re-review",
    "awaiting_review": "Waiting for a first review",
    "draft": "Drafts",
}
FAILED = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")


class TriageError(RuntimeError):
    pass


def graphql(variables):
    command = ["gh", "api", "graphql", "--hostname", "github.com", "-f", f"query={QUERY}"]
    for key, value in variables.items():
        command += ["-f", f"{key}={value}"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    except FileNotFoundError as exc:
        raise TriageError("GitHub CLI (gh) is not installed or not on PATH. Install it from https://cli.github.com, then run `gh auth login`.") from exc
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TriageError(f"GitHub read failed: {type(exc).__name__}") from exc
    if result.returncode:
        raise TriageError((result.stderr.strip() or "gh api graphql failed")[:600])
    try:
        body = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TriageError("gh returned invalid JSON") from exc
    if body.get("errors"):
        raise TriageError("; ".join(str(e.get("message", e)) for e in body["errors"])[:600])
    return body["data"]["search"]


def fetch_open_prs(author, include_own):
    query = f"is:pr is:open author:{author}" + ("" if include_own else f" -user:{author}") + " archived:false"
    nodes, after = [], None
    while True:
        variables = {"q": query}
        if after:
            variables["after"] = after
        page = graphql(variables)
        nodes += [n for n in page["nodes"] if n.get("number")]
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


def _time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def normalize(n):
    commit = ((n.get("commits") or {}).get("nodes") or [{}])[-1].get("commit") or {}
    rollup = commit.get("statusCheckRollup")
    contexts = ((rollup or {}).get("contexts") or {}).get("nodes") or []
    failing = []
    for c in contexts:
        state = c.get("conclusion") or c.get("state")
        if state in FAILED:
            failing.append(c.get("name") or c.get("context") or "unnamed check")
    author = (n.get("author") or {}).get("login")
    # Comment-only reviews are excluded, so a later comment cannot hide an active change request.
    reviews = (n.get("latestOpinionatedReviews") or {}).get("nodes") or []
    states = {r.get("state") for r in reviews}
    change_requests = [_time(r["submittedAt"]) for r in reviews if r.get("state") == "CHANGES_REQUESTED" and r.get("submittedAt")]
    # reviewDecision is null when the branch requires no reviews; fall back to the reviews themselves.
    decision = n.get("reviewDecision") or ("CHANGES_REQUESTED" if "CHANGES_REQUESTED" in states else "APPROVED" if "APPROVED" in states else None)
    comments = [c for c in (n.get("comments") or {}).get("nodes") or []
                if c.get("createdAt") and (c.get("author") or {}).get("__typename") != "Bot"]
    author_comments = [_time(c["createdAt"]) for c in comments if (c.get("author") or {}).get("login") == author]
    # Human activity by anyone else: comments plus reviews. Author comments after the last of it went unanswered.
    replies = [_time(c["createdAt"]) for c in comments if (c.get("author") or {}).get("login") != author]
    replies += [_time(r["submittedAt"]) for r in reviews if r.get("submittedAt") and (r.get("author") or {}).get("login") != author]
    last_reply = max(replies) if replies else None
    unanswered = sum(1 for t in author_comments if last_reply is None or t > last_reply)
    base = n.get("baseRefName") or "main"
    merges = sum(is_base_merge({"commit": {"message": c["commit"].get("messageHeadline", "")}}, base)
                 for c in (n.get("recent") or {}).get("nodes") or [] if c.get("commit"))
    return {
        "repository": n["repository"]["nameWithOwner"],
        "number": n["number"],
        "title": n.get("title", ""),
        "url": n.get("url", ""),
        "draft": bool(n.get("isDraft")),
        "review_decision": decision,
        "mergeable": n.get("mergeable"),
        "checks_state": (rollup or {}).get("state"),
        "failing_checks": failing,
        "updated_at": _time(n.get("updatedAt")),
        "last_commit_at": _time(commit.get("committedDate")),
        "last_change_request_at": max(change_requests) if change_requests else None,
        "last_author_comment_at": max(author_comments) if author_comments else None,
        "base": base,
        "base_merges": merges,
        "unanswered_comments": unanswered,
    }


def _answered(pr):
    asked = pr["last_change_request_at"]
    # A commit date is set by the author's machine, so treat it as a hint, not proof.
    answers = [t for t in (pr["last_commit_at"], pr["last_author_comment_at"]) if t]
    return bool(asked and answers and max(answers) > asked)


def classify(pr, now, stale_days):
    now = _time(now) if isinstance(now, str) else now
    if pr["draft"]:
        bucket = "draft"
    elif pr["mergeable"] == "CONFLICTING":
        bucket = "resolve_conflict"
    elif pr["review_decision"] == "CHANGES_REQUESTED" and not _answered(pr):
        bucket = "address_review"
    elif pr["failing_checks"] or pr["checks_state"] in FAILED:
        bucket = "checks_failing"
    elif pr["review_decision"] == "CHANGES_REQUESTED":
        bucket = "awaiting_rereview"
    elif pr["review_decision"] == "APPROVED":
        bucket = "approved"
    else:
        bucket = "awaiting_review"
    updated = pr["updated_at"]
    stale = bool(updated and (now - updated).days >= stale_days)
    noise = []
    if pr.get("base_merges", 0) >= 2:
        noise.append(f"{pr['base_merges']} merges from {pr['base']}")
    if pr.get("unanswered_comments", 0) >= 2:
        noise.append(f"{pr['unanswered_comments']} comments with no reply")
    return {"bucket": bucket, "stale": stale, "failing_checks": pr["failing_checks"], "noise": noise}


def build_report(nodes, now, stale_days):
    rows = []
    for n in nodes:
        pr = normalize(n)
        verdict = classify(pr, now, stale_days)
        rows.append({"repository": pr["repository"], "number": pr["number"], "title": pr["title"], "url": pr["url"],
                     "updated_at": pr["updated_at"].isoformat() if pr["updated_at"] else None, **verdict})
    counts = {key: sum(r["bucket"] == key for r in rows) for key in BUCKETS}
    return {"schema_version": 1, "generated_at": now, "stale_days": stale_days, "counts": counts, "pull_requests": rows}


def render(report):
    lines = [f"Open pull requests: {len(report['pull_requests'])} (stale = no update in {report['stale_days']}+ days)"]
    for key, label in BUCKETS.items():
        rows = [r for r in report["pull_requests"] if r["bucket"] == key]
        if not rows:
            continue
        lines += ["", f"{label} ({len(rows)})"]
        for r in sorted(rows, key=lambda r: r["updated_at"] or ""):
            extra = f" [failing: {', '.join(r['failing_checks'])}]" if r["failing_checks"] else ""
            stale = " [stale]" if r["stale"] else ""
            noise = f" [noise: {'; '.join(r['noise'])}]" if r["noise"] else ""
            lines.append(f"  {r['repository']}#{r['number']} {r['title'][:70]}{extra}{stale}{noise}")
    if any(r["noise"] for r in report["pull_requests"]):
        lines += ["", "[noise] means repeated merges from the base branch or comments nobody has answered yet. "
                  "Don't add another until a maintainer replies, unless there is a conflict or new information."]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author", required=True, help="GitHub login whose open PRs to sort")
    parser.add_argument("--include-own", action="store_true", help="Also include PRs to repositories the author owns")
    parser.add_argument("--stale-days", type=int, default=30, help="Mark PRs with no update for this many days")
    parser.add_argument("--output", type=Path, help="Also save the report as a new private JSON file")
    parser.add_argument("--now", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not LOGIN.fullmatch(args.author):
        parser.error("Provide a valid GitHub login")
    if args.stale_days < 1:
        parser.error("--stale-days must be positive")
    if args.output and not args.output.parent.is_dir():
        parser.error(f"Folder {args.output.parent} does not exist; create it first (mkdir -p {args.output.parent})")
    if args.output and args.output.exists():
        parser.error("Output already exists; choose a new file")
    now = args.now or dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        report = build_report(fetch_open_prs(args.author, args.include_own), now, args.stale_days)
        if args.output:
            with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as out:
                json.dump(report, out, ensure_ascii=False, indent=2)
                out.write("\n")
    except (TriageError, OSError) as exc:
        print(f"Triage failed: {exc}", file=sys.stderr)
        return 1
    print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
