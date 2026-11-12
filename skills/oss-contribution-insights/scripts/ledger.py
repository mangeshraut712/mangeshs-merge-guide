#!/usr/bin/env python3
"""Inspect and compare local contribution ledgers. No network or mutation of inputs."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys


class LedgerError(ValueError):
    pass


def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get("metadata"), dict) or not isinstance(data.get("records"), list):
        raise LedgerError("Expected an object with metadata and records")
    ids, aliases = set(), set()
    for index, row in enumerate(data["records"]):
        if not isinstance(row, dict):
            raise LedgerError(f"Record {index} is not an object")
        identity, repo, number = row.get("pull_request_node_id"), row.get("repository"), row.get("number")
        if not isinstance(identity, str) or not identity.strip():
            raise LedgerError(f"Record {index} lacks an immutable pull_request_node_id")
        if not isinstance(repo, str) or repo.count("/") != 1 or not all(repo.split("/")):
            raise LedgerError(f"Record {index} has an invalid repository")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise LedgerError(f"Record {index} has an invalid PR number")
        alias = (repo.casefold(), number)
        if identity in ids or alias in aliases:
            raise LedgerError(f"Duplicate PR identity or repository/number at record {index}")
        ids.add(identity)
        aliases.add(alias)
        if row.get("github_lifecycle") not in {"github_merged", "open", "closed_without_github_merge"}:
            raise LedgerError(f"Record {index} has an unknown lifecycle; reconcile schema before counting")
        if not isinstance(row.get("disposition"), str) or not row["disposition"]:
            raise LedgerError(f"Record {index} lacks a disposition")
        native = row["github_lifecycle"] == "github_merged"
        if native != (row["disposition"] == "github_merged"):
            raise LedgerError(f"Record {index} has inconsistent native merge lifecycle/disposition")
    return data


def load(path):
    try:
        return validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerError(f"Cannot read ledger: {exc}") from exc


def summary(data):
    validate(data)
    rows = data["records"]
    lifecycle = Counter(row["github_lifecycle"] for row in rows)
    dispositions = Counter(row["disposition"] for row in rows)
    return {
        "as_of": data["metadata"].get("as_of"),
        "author": data["metadata"].get("author"),
        "scope": data["metadata"].get("scope"),
        "pr_records": len(rows),
        "repositories": len({row["repository"].casefold() for row in rows}),
        "owner_namespaces": len({row["repository"].split("/")[0].casefold() for row in rows}),
        "github_lifecycle": dict(sorted(lifecycle.items())),
        "dispositions": dict(sorted(dispositions.items())),
        "discussion_coverage": dict(sorted(Counter(row.get("discussion_coverage", "unknown") for row in rows).items())),
        "disposition_confidence": dict(sorted(Counter(row.get("disposition_confidence", "unknown") for row in rows).items())),
        "native_or_full_landed_pr_records": lifecycle["github_merged"] + dispositions["verified_full_landed_elsewhere"],
        "partial_credit_pr_records": dispositions["verified_partial_landed_elsewhere"],
        "caution": "Recorded claims, not independent verification. PR records are not unique fixes. Scope excludes any uncollected contribution types; no causal or acceptance-rate claim.",
    }


def brief(row):
    return {key: row.get(key) for key in ("pull_request_node_id", "url", "repository", "number", "github_lifecycle", "disposition", "discussion_coverage")}


def compare(old, new):
    validate(old)
    validate(new)
    if old["metadata"].get("author") != new["metadata"].get("author") or old["metadata"].get("scope") != new["metadata"].get("scope"):
        raise LedgerError("Author or declared scope changed; reconcile comparable scope before diffing")
    before = {row["pull_request_node_id"]: row for row in old["records"]}
    after = {row["pull_request_node_id"]: row for row in new["records"]}
    changed = []
    for identity in sorted(before.keys() & after.keys()):
        fields = sorted(key for key in before[identity].keys() | after[identity].keys() if before[identity].get(key) != after[identity].get(key))
        if fields:
            changed.append({**brief(after[identity]), "changes": {field: {"before": before[identity].get(field), "after": after[identity].get(field)} for field in fields}})
    return {
        "old_summary": summary(old),
        "new_summary": summary(new),
        "added": [brief(after[key]) for key in sorted(after.keys() - before.keys())],
        "changed": changed,
        "absent_from_new": [brief(before[key]) for key in sorted(before.keys() - after.keys())],
        "reconciliation_note": "Absent rows remain unresolved; do not delete history or infer rejection. Changed evidence must be checked before updating claims. No inputs were modified.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    summarize = sub.add_parser("summary")
    summarize.add_argument("path", type=Path)
    show = sub.add_parser("show")
    show.add_argument("path", type=Path)
    show.add_argument("--repository", required=True)
    show.add_argument("--number", type=int, required=True)
    diff = sub.add_parser("diff")
    diff.add_argument("old", type=Path)
    diff.add_argument("new", type=Path)
    diff.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "summary":
            output = summary(load(args.path))
        elif args.operation == "show":
            matches = [row for row in load(args.path)["records"] if row["repository"].casefold() == args.repository.casefold() and row["number"] == args.number]
            if len(matches) != 1:
                raise LedgerError("No matching PR record")
            output = matches[0]
        else:
            if args.output.exists():
                raise LedgerError("Output exists; choose a new file")
            output = compare(load(args.old), load(args.new))
            with os.fdopen(os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as destination:
                json.dump(output, destination, ensure_ascii=False, indent=2)
                destination.write("\n")
            print(f"Saved local comparison: {args.output}")
            return 0
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (LedgerError, OSError) as exc:
        print(f"Ledger operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
