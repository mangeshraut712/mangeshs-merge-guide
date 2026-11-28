#!/usr/bin/env python3
"""Flag reviewer-facing noise in saved PR snapshots: repeated base merges and unanswered pings. Reads local files only."""
import argparse
import json
import re
import sys
from pathlib import Path

MERGE_THRESHOLD = 2
UNANSWERED_THRESHOLD = 2
NUDGE = re.compile(r"\b(ping|bump|any update|gentle reminder|friendly reminder|following up|could (someone|you) (take a look|review))\b", re.I)
ADVICE = {
    "base_merges": "Stop merging the base branch to keep the PR fresh. Update it only when there is a conflict, a failing check caused by the base, or a maintainer asks.",
    "unanswered_comments": "Several of your comments have no reply yet. Wait for a maintainer before posting again, and put new information in one edited comment.",
}


def _is_bot(account):
    account = account or {}
    return account.get("type") == "Bot" or str(account.get("login", "")).endswith("[bot]")


def is_base_merge(entry, base):
    message = (((entry.get("commit") or {}).get("message") or "").splitlines() or [""])[0]
    name = re.escape(base)
    # The whole branch name must match, so `main-fix` or `main/cleanup` is not `main`.
    patterns = (
        rf"Merge branch '{name}'",
        rf"Merge remote-tracking branch '[^'/]+/{name}'",
        rf"Merge (?:[^\s/]+/)?{name}(?: |$)",
    )
    return any(re.match(p, message) for p in patterns)


def assess(snap):
    pr = snap.get("pr") or {}
    author = (pr.get("user") or {}).get("login")
    base = ((pr.get("base") or {}).get("ref")) or "main"
    sections = snap.get("sections") or {}
    incomplete = sorted(set(snap.get("errors") or {}) | {s for s in ("commits", "issue_comments", "reviews", "review_comments") if s not in sections})

    base_merges = sum(is_base_merge(c, base) for c in sections.get("commits") or [])

    events = []
    for c in (sections.get("issue_comments") or []) + (sections.get("review_comments") or []):
        events.append((c.get("created_at") or "", c.get("user"), c.get("body") or ""))
    for r in sections.get("reviews") or []:
        # An inline comment arrives with an empty COMMENTED review around it; count the comment once.
        if r.get("state") == "COMMENTED" and not (r.get("body") or "").strip() and (r.get("user") or {}).get("login") == author:
            continue
        events.append((r.get("submitted_at") or "", r.get("user"), r.get("body") or ""))
    events = sorted((e for e in events if e[0] and not _is_bot(e[1])), key=lambda e: e[0])
    trailing = []
    for when, account, body in reversed(events):
        if (account or {}).get("login") != author:
            break
        trailing.append(body)

    flags = []
    if base_merges >= MERGE_THRESHOLD:
        flags.append("base_merges")
    if len(trailing) >= UNANSWERED_THRESHOLD:
        flags.append("unanswered_comments")
    return {
        "repository": snap.get("repository"), "number": snap.get("number"), "base": base,
        "base_merges": base_merges, "unanswered_author_comments": len(trailing),
        "nudges": sum(bool(NUDGE.search(b)) for b in trailing), "flags": flags, "incomplete": incomplete,
    }


def render(result):
    head = f"{result['repository']}#{result['number']}"
    lines = []
    if "base_merges" in result["flags"]:
        lines.append(f"  {result['base_merges']} merge commits from {result['base']}. {ADVICE['base_merges']}")
    if "unanswered_comments" in result["flags"]:
        nudges = f", {result['nudges']} of them nudges" if result["nudges"] else ""
        lines.append(f"  {result['unanswered_author_comments']} of your comments in a row with no human reply{nudges}. {ADVICE['unanswered_comments']}")
    if not lines:
        lines.append("  No noise found.")
    if result["incomplete"]:
        lines.append(f"  Snapshot incomplete ({', '.join(result['incomplete'])}); refresh it before trusting this result.")
    return "\n".join([head] + lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", nargs="+", type=Path, help="Files saved by collect_pr_evidence.py")
    args = parser.parse_args(argv)
    flagged = False
    for path in args.snapshots:
        try:
            snap = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"{path}: cannot read ({type(exc).__name__})", file=sys.stderr)
            return 2
        if not isinstance(snap, dict) or snap.get("schema_version") != 1 or not isinstance(snap.get("sections"), dict):
            print(f"{path}: not a collect_pr_evidence snapshot", file=sys.stderr)
            return 2
        result = assess(snap)
        flagged |= bool(result["flags"])
        print(render(result))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
