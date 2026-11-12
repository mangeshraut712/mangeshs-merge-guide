# Maintain contribution learning as work evolves

## Keep data, guidance, and automation separate

- **Ledger:** dated observations for individual immutable contribution identities. Refresh new comments, review changes, heads, checks, lifecycle, landing evidence, and post-merge corrections.
- **Skill:** reusable decision guidance. Change it when an evidenced lesson changes a future decision, preserving source and uncertainty. Do not add a universal rule for every anecdote.
- **Automation:** a separately configured, verified schedule or event source. The existence of this skill does not schedule anything. A user request for skill updates does not grant posting, code changes, pushes, PR creation, or merges in upstream repositories.

The bundled example ledger is synthetic, not a research baseline or maintained database. For ongoing work, use an authorized private location or an existing user-approved ledger. Keep any separately established research baseline intact and save dated working snapshots there. Read current permissions and source restrictions before each refresh; a historical held-source marker is neither new permission nor a substitute for current instructions.

## Incremental refresh

1. Read the last successful checkpoint and its coverage. If none exists, establish a baseline for the agreed scope, including contribution types and account. Confirm the source is accessible before promising monitoring.
2. Search for **updated**, not only created or merged, contributions since the last successful checkpoint, with a modest overlap for indexing delays. Include all lifecycle states so a comment on an old merged PR is not missed. Recheck outstanding open items relevant to current work. Deduplicate with immutable PR node IDs.
3. Page each result and each required discussion stream fully. Record totals, retrieval errors, inaccessible/held records, and `incomplete_results`. If a search approaches GitHub's 1,000-result limit, partition into disjoint creation-date ranges and subdivide any saturated range; validate boundary coverage and deduplicate identities. If one partition still cannot be enumerated, report the coverage gap or use a supported repository/listing endpoint. Never call a capped query complete.
4. Refresh only changed permitted items and the evidence needed to understand them. Respect rate limits and bounded retries; do not retry access denials through another identity or tool. Preserve the last known record if a source becomes unavailable. Do not erase a record because it disappeared from one query.
5. Reconcile lifecycle separately from code disposition and post-landing quality. Verify equivalent landed code and credit, not only a closure comment. Keep partial incorporation distinct from full landing. Preserve links between a source PR, destination PR/commit, ports, and backports so a single change is not counted twice.
6. Compare snapshots using `python3 scripts/ledger.py diff OLD NEW --output NEW_FILE`. This helper reports changes; it never rewrites the ledger or resolves conflicting evidence. Investigate unexpected count decreases, changed immutable identities, duplicate records, and inconsistent lifecycle/disposition before publishing totals.
7. Advance the **complete checkpoint** only through an interval whose permitted retrieval finished. A partial attempt can retain successful rows and a retry list, but must not silently skip its failed interval later. Record the snapshot's observation time separately from GitHub event times.
8. Periodically reconcile the full agreed inventory in addition to incremental queries, at a cadence justified by activity and API cost. Revalidate a live PR before taking action; a scheduled snapshot is not action-time verification.

## Useful triggers and bounded responses

- **New substantive review:** map each required point to the relevant change/evidence; report blockers requiring the user. Do not automatically reply.
- **Head changed:** invalidate prior readiness conclusions for changed code; check final-head verification and review requirements.
- **Merged or credited landing:** verify destination, final scope, credit, and deduplication. Update status, not a quality guarantee.
- **Post-merge correction, revert, or vulnerability report:** retain historical acceptance and record current quality/repair status separately. Verify severity before an urgent message; do not automatically publish a vulnerability or modify upstream code.
- **Repeated failure or new policy constraint:** update the reusable lesson with evidence and proper scope, then rerun skill validation and relevant behavioral tests before saving.
- **No substantive change:** save coverage/checkpoint if appropriate; no empty user update or maintainer nudge.

For an ongoing arrangement, prefer a modest agreed cadence and event-driven refresh where supported. A weekly read-only check is a reasonable option to propose for this history; it is not a schedule already running. More frequent checks should be justified by active review or a deadline. Batch nonurgent user findings, honor explicit reviewer limits, and avoid mass submissions or automated green-CI messages.

## Refresh the skill safely

Use the supported personal-skill workflow, resolve the skill by its frontmatter name, preserve UI policy/dependencies, and update only this skill. Keep raw history in the approved ledger, with focused sourced examples in references. Run structure validation, helper tests, and independent task scenarios for meaningful behavior changes. Verify the saved remote content before claiming the update is available. Do not infer that saving a cloud/personal skill installs it into a desktop-local skills folder.
