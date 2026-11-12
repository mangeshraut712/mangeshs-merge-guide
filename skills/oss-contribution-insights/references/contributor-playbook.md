# Contributor playbook: first issue to ongoing maintenance

Use this guide to adapt assistance to the contributor's experience. Explain unfamiliar terms, ask what they can reproduce, and offer the next small step rather than a wall of commands. Do not assume paid tools, maintainer access or a particular operating system. Let experienced contributors skip setup explanations while preserving verification and policy gates.

## First contribution

1. Identify the actual user problem, a supported release, and an accessible development environment. A “good first issue” label is a lead, not proof that it is current or unclaimed.
2. Read the contribution guide, code of conduct, issue/PR templates and AI policy. Check whether assignment, a design proposal, CLA or human sign-off is required. Explain legal attestations; never sign them for someone.
3. Search existing issues, merged and open PRs, and recent release notes. If someone owns the work, do not duplicate it. Prefer a wanted, bounded fix with an observable test, including documentation or accessibility defects when useful.
4. Follow the project's environment instructions. Explain fork (your copy), branch (isolated changes), commit (saved revision), and PR (request to incorporate changes) as needed. Preserve uncommitted user work; do not prescribe destructive resets.
5. Run the smallest baseline reproduction before changing code. Save the exact command, environment, revision and observed result. Distinguish environment failures from product defects.

## Issue triage and proposals

Read the entire changed discussion and linked evidence before interpreting a maintainer request. Separate expected behavior, observed behavior and hypothesis. A useful issue draft contains version/platform, minimal reproducer, expected/actual result, relevant sanitized output and duplicate search. Do not publish security-sensitive reports through a normal public issue; follow SECURITY.md and disclosure policy.

For a larger change, propose scope and compatibility before implementation when the project requires it. Explain alternatives and trade-offs, not just the favored design. Do not equate issue activity or an emoji with permission or assignment.

## Implement and open a PR

Follow the main skill's red/green and final-head verification steps. Start with a narrowly scoped behavior change, add repository-appropriate tests, and update relevant docs/changelog. For public interfaces consider backward compatibility, accessibility, platform support, performance/resource cost and security. A refactor needs its own justification.

Before publication, review the full diff and commit content for generated noise, secrets, private paths and unrelated edits. Check licensing and provenance of copied code. Prepare the repository's PR template truthfully. State unrun checks explicitly. Only publish when the user authorized it; draft-first does not remove that requirement.

## Comments and communication

Draft first unless sending is explicitly authorized. Match repository tone and terminology, stay concise, and avoid mass pings or synthetic progress updates. Do not claim personal understanding, manual testing or human authorship that has not occurred. Mark AI assistance when required; a policy requiring substantial human input cannot be satisfied by approving an AI-only message.

Use these as structures, not automatically posted text:

- **Clarify scope:** “I can reproduce [observed behavior] on [version]. Before changing [interface], is [bounded behavior] the intended contract?” Only state reproduction if verified.
- **Respond to a review:** “Changed [specific point] in [commit]. [Exact test] now covers [behavior]. [Remaining limitation].” Link evidence; do not resolve a thread merely because a reply was posted.
- **Disagree constructively:** “I see the concern about [trade-off]. [Evidence] suggests [constraint]. Would [alternative] address it without [documented regression]?” Acknowledge what is unknown.
- **Blocked:** “[Check] cannot run because [observed error]. [Other checks] passed on [head]. The missing verification is [specific step].” Avoid presenting a workaround as permission to bypass a gate.
- **Declined or superseded:** Thank the maintainer briefly if a response is warranted and authorized, record the outcome, and stop the declined line of work. Do not debate for credit or reopen automatically.

For every review point, track requested change → code or explanation → evidence → unresolved/resolved status. Distinguish blocking review, suggestion, question and automated finding. Re-read materially edited comments. Do not pressure maintainers or use arbitrary follow-up quotas; respect explicit cadence and stop requests.

## Experienced contributors and maintainers

For architecture or multi-package changes, document invariants, migration/rollback strategy, consumer wiring and release implications. Keep security, compatibility and resource budgets explicit. Prefer staged changes only when each is independently useful, not to manufacture activity. Review others' PRs only with authorization and within project policy; evaluate actual diffs and tests rather than issuing approval from summaries. Never approve as another person or bypass branch protections.

After an authorized rebase or conflict resolution, rerun affected checks on the new head. A clean merge or green CI does not establish semantic correctness. Distinguish author-fixable work from maintainer-only workflow/review gates.

## After acceptance or closure

Verify native merge metadata or credited destination code separately. Preserve final accepted scope and collaborator credit. Monitor post-merge issues only within an agreed arrangement. A revert or correction is learning evidence, not something to hide. Record rejected, withdrawn and unexplained closures without inventing reasons. Finish the contribution with accurate evidence, not a promise of acceptance.
