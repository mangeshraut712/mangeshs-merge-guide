#!/usr/bin/env python3
"""Check whether someone else already has, or has offered to take, an issue before you start on it. Read-only gh REST calls."""
import argparse
import re
import sys

from collect_pr_evidence import CollectionError, api

MAINTAINERS = {"OWNER", "MEMBER", "COLLABORATOR"}
OFFER = re.compile(
    r"\b(?:(?:can|could|may) i (?:take|work on|pick up|open a pr|submit a pr|send a pr|fix)"
    r"|i(?:'d| would) like to (?:work on|take|fix|pick up|submit|open)"
    r"|i(?:'m| am) (?:working on|on) (?:this|it)"
    r"|i(?:'ll| will) (?:take|open a pr|submit a pr|send a pr|work on)"
    r"|(?:assign|assigning) (?:this|it) to me"
    r"|happy to (?:work on|take|submit|open|send)"
    r"|let me (?:take|work on))",
    re.I,
)
TRIAGE = re.compile(r"triage|needs[- ]?(?:info|discussion|design|decision)|blocked|wontfix|duplicate", re.I)


def _is_bot(account):
    account = account or {}
    return account.get("type") == "Bot" or str(account.get("login", "")).endswith("[bot]")


def linked_prs(timeline):
    prs = []
    for event in timeline:
        issue = (event.get("source") or {}).get("issue") or {}
        if event.get("event") == "cross-referenced" and "pull_request" in issue:
            prs.append({"number": issue.get("number"), "user": (issue.get("user") or {}).get("login"),
                        "state": issue.get("state"), "repository": (issue.get("repository") or {}).get("full_name")})
    return prs


def assess(issue, comments, prs, me):
    notes = [f"Label `{label['name']}` suggests the issue is not ready for a fix yet."
             for label in issue.get("labels") or [] if TRIAGE.search(label.get("name", ""))]
    if issue.get("milestone"):
        notes.append(f"Milestone `{issue['milestone'].get('title')}` is set; some projects want you to ask first.")
    if issue.get("state") != "open":
        return {"verdict": "closed", "assignees": [], "open_prs": [], "offers": [], "notes": notes}

    assignees = [a["login"] for a in issue.get("assignees") or [] if a.get("login") != me]
    open_prs = [p for p in prs if p["state"] == "open" and p["user"] != me]
    humans = [c for c in comments if not _is_bot(c.get("user"))]
    offers = []
    for i, c in enumerate(humans):
        login = (c.get("user") or {}).get("login")
        if login == me or not OFFER.search(c.get("body") or ""):
            continue
        replied = any((later.get("user") or {}).get("login") not in (login, me)
                      and later.get("author_association") in MAINTAINERS for later in humans[i + 1:])
        offers.append({"login": login, "at": c.get("created_at"), "maintainer_replied": replied})

    verdict = "taken" if assignees or open_prs else "ask_first" if offers else "clear"
    return {"verdict": verdict, "assignees": assignees, "open_prs": open_prs, "offers": offers, "notes": notes}


def render(repo, number, result):
    lines = [f"{repo}#{number}"]
    if result["verdict"] == "closed":
        lines.append("  The issue is closed. Check whether it was fixed before working on it.")
    for login in result["assignees"]:
        lines.append(f"  Assigned to {login}.")
    for pr in result["open_prs"]:
        lines.append(f"  Open PR {pr['repository']}#{pr['number']} by {pr['user']} references it.")
    for offer in result["offers"]:
        reply = "a maintainer has replied since" if offer["maintainer_replied"] else "no maintainer reply yet"
        lines.append(f"  {offer['login']} offered to work on it on {offer['at'][:10]} ({reply}).")
    lines += [f"  {note}" for note in result["notes"]]
    if result["verdict"] == "taken":
        lines.append("  Someone else has this. Offer to help or review instead of opening a competing PR.")
    elif result["verdict"] == "ask_first":
        lines.append("  Read the offer and any reply. If it is still open, ask the person or the maintainers before starting.")
    elif result["verdict"] == "clear":
        lines.append("  No one else is assigned, has an open PR, or has offered to take it.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="GitHub OWNER/REPO")
    parser.add_argument("number", type=int, help="Issue number")
    parser.add_argument("--me", required=True, help="Your GitHub login, so your own comments and PRs are ignored")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9_.-]+", args.repository) or args.number < 1:
        parser.error("Provide OWNER/REPO and a positive issue number")
    route = f"repos/{args.repository}/issues/{args.number}"
    try:
        issue = api(route)
        comments = [c for page in api(route + "/comments?per_page=100", paginated=True) for c in page]
        timeline = [e for page in api(route + "/timeline?per_page=100", paginated=True) for e in page]
    except CollectionError as exc:
        print(f"Claim check failed: {exc}", file=sys.stderr)
        return 2
    result = assess(issue, comments, linked_prs(timeline), args.me)
    print(render(args.repository, args.number, result))
    return 0 if result["verdict"] == "clear" else 1


if __name__ == "__main__":
    sys.exit(main())
