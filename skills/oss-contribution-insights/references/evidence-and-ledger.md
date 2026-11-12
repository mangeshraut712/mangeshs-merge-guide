# Evidence method and contribution ledger

## Collect a defensible inventory

State the account, contribution types, repositories/namespaces included or excluded, date range, exact query, UTC snapshot time, pagination, and coverage limits. “Every contribution” can include authored PRs, issues, reviews, direct commits, and own-repository work: enumerate those separately when requested and permitted. An authored-upstream-PR query does not establish completeness for those other categories. Do not silently rename a PR-only inventory “all GitHub contributions.”

Use all accessible relevant outcomes in the agreed scope rather than only wins. If only a sample is practical, label its selection. Check search result ceilings, per-page totals, incomplete flags, unique IDs, and discussion pagination. See [incremental maintenance](maintenance.md) for growth beyond search caps. Keep held/inaccessible records and collection errors explicit, not zero-filled or omitted. Do not re-read a held source to fill a gap without current authorization.

For a specific PR, inspect its metadata, current head and base, diff, linked issue, reviews, inline comments, discussion, and checks. Read current repository policy before acting on a historical case. A complete inventory and discussion assessment is not a complete code audit or a rerun of every test suite.

Record evidence provenance: author claim, CI/check output, automated or AI-assisted review, verified maintainer statement, independently reproduced test, or verified landed commit. Preserve unknown identity and automation status. A different account, reviewer badge, or positive review alone does not prove a human maintainer ran the tests. Prefer exact comment permalinks for review claims. Treat any old ledger wording about “human feedback” as historical classification, not verified actor identity.

## Separate lifecycle, disposition, and quality

Keep three independent dimensions:

1. **Lifecycle:** `github_merged`, `open`, or `closed_without_github_merge`, based on native metadata.
2. **Disposition:** full credited landing elsewhere; partial incorporation; superseded/duplicate; explicit withdrawal; documented rejection/out-of-scope; inferred reason; explicit stale closure; or unresolved. Keep the evidence and confidence for each reason.
3. **Post-landing quality:** unknown, no known correction in checked sources, correction reported, correction verified, reverted, or repaired. Do not erase a genuine merge because a later defect is reported, or let a merge badge hide the defect. Absence of reports is not proof of correctness.

For an outside landing, verify equivalent code in the destination commit/PR and contributor credit. If only a comment claims landing, say “reported landing; destination not verified.” Distinguish full and partial incorporation, record the final scope, and credit maintainer follow-ups. Link ports/backports and destination PRs so the same change is not double-counted. PR-record totals are not necessarily unique fixes.

Do not infer rejection from closure, infer cause from timing, or spread a cohort-level statement to every PR in a repository. Explicitly distinguish direct evidence, bounded inference, and unresolved explanation. Keep native merges, additional full landings, partial credit, and a goal-specific company allowlist separate. Organization account type is not evidence of company eligibility.

## Preserve a usable per-PR ledger

The bundled `assets/example-ledger.json` contains synthetic `metadata` and `records` for a smoke test. Store real evidence in an authorized private location. Query ledgers with `scripts/ledger.py` rather than loading them wholesale.

Use one current record per immutable `pull_request_node_id`; retain canonical `url`, `repository`, and `number` for navigation. Keep `issue_id` (REST issue identity) distinct from `pull_request_id` (REST PR identity); unknown IDs stay null. Keep renamed/moved repository aliases associated with the immutable ID.

Preserve existing fields and annotations. Important baseline fields include:

- `author`, `title`, `created_at`, `updated_at`, `closed_at`, `merged_at`.
- `github_lifecycle`, `disposition`, `disposition_confidence`.
- `discussion_coverage`, `discussion_entry_count`.
- `merge_commit_sha`, `landing_commit_url`, `landing_commit_sha`, `verified_credit`.
- `research_note`, `evidence_urls`; optional owner/account and explicitly scoped goal fields.

Add structured observations when useful rather than replacing history with a single favorable summary:

```json
{
  "observed_at": "UTC snapshot timestamp",
  "sampled_head_sha": null,
  "positive": {
    "observation": "A directly supported strength",
    "evidence_urls": [],
    "source_kind": "verified_test | reported_test | comment | commit | check",
    "confidence": "direct | supported_inference | unverified"
  },
  "improvement": {
    "feedback": "Specific friction or review request",
    "evidence_urls": [],
    "change_made": null,
    "verification": null,
    "status": "proposed | implemented_unverified | verified | not_applicable"
  },
  "verification": {
    "base_sha": null,
    "tested_head_sha": null,
    "red": "not_run",
    "green": "not_run",
    "mutation": "not_run",
    "required_checks": "unknown",
    "commands_and_results": []
  },
  "post_landing": {
    "status": "unknown",
    "checked_at": null,
    "evidence_urls": [],
    "correction_or_revert_url": null
  },
  "related_contributions": [],
  "interpretation": null,
  "next_experiment": null,
  "next_action": null,
  "blocker": null
}
```

Store dynamic ledgers only in an authorized private task location. Do not publish account-wide retrospectives or private feedback upstream by default. Keep secrets and unnecessary personal data out. If maintaining a historical event log, keep it separate from the one-row-per-PR current view and deduplicate events by source identity/version.

## Analyze and report without overclaiming

For each pattern, identify distinct PRs and repositories, counterexamples, confounding context, and what is independently verified. Separate observation → interpretation → next experiment. Report the strongest demonstrated positive, the improvement made, remaining friction, and a concrete action. Do not convert a plausible test into proven regression detection or credit all final quality to the original patch.

Measure useful outcomes when available: substantive review response, requested versus unnecessary revision, verification gaps closed, and post-merge corrections. Do not reward comment counts, PR volume, or repeated pings. Acceptance rate is descriptive only with a justified complete denominator, observation window and clearly separated open work; this history supports no causal effect or acceptance probability.

## Read-only helpers

- `collect_pr_evidence.py OWNER/REPO NUMBER --output NEW_PATH` uses authenticated `gh api --method GET`. It collects PR metadata, paginated comments/reviews/commits, and check-runs/statuses for a sampled head. An initial failure creates no file; later failures save a marked partial result with nonzero status. A head change during collection is flagged. Commit-list length is checked against PR metadata because pagination can still cap the endpoint at 250 commits; incomplete or unknown coverage is marked partial. It does not fetch policy, diffs, check logs, or independently verify reported tests. Use an available connector when `gh` authentication is absent; do not change credentials just for the helper.
- `ledger.py summary PATH` validates record identities and computes descriptive totals. It reports recorded coverage, not independent verification of the underlying claims.
- `ledger.py show PATH --repository OWNER/REPO --number N` extracts one local row.
- `ledger.py diff OLD NEW --output NEW_PATH` compares local snapshots without altering either, preserving added, changed, and absent records. An absent record is a reconciliation warning, not permission to delete it. Output files must be new; none are overwritten.

New helper output files use exclusive creation and owner-only mode `0600` on POSIX. Windows uses different ACL semantics; verify the destination access controls there before storing private evidence. These helpers do not configure Windows ACLs.
