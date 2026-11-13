---
name: oss-contribution-insights
description: Tackle useful open-source issues from selection and reproduction through implementation, regression tests, PR preparation, review comments, and maintainer follow-through. Use for first contributions, complex fixes, current PR feedback, and merge-readiness. Learn from verified accepted work and setbacks without promising acceptance; contribution analytics are optional supporting evidence.
---

# Mangesh’s Merge Guide

Help the contributor complete a useful change that a maintainer can confidently evaluate. Default to the current issue or PR, not a history report. Optimize for maintainer value and reviewability, not PR volume or a promised merge rate.

For C or C++ repositories, use [the C/C++ contribution track](references/c-cpp-contributions.md) for build identity, memory/concurrency safety, portability, ABI and sanitizer verification. Follow the target project’s language rather than rewriting unrelated tooling.

## Run a contribution work session

1. Establish the requested outcome and exact authorization. Resume existing owned work before starting another fix. Read current local/remote state and any outstanding review.
2. Select a wanted, reproducible issue using the criteria below. If no target is given, produce a short ranked shortlist with maintainer need, duplicate risk, verification feasibility and the smallest next step; do not auto-claim issues.
3. Reproduce on the supported base, identify the contract and real execution path, then implement the smallest sufficient fix within authorized local scope. Follow the validation steps below.
4. Review the actual final diff and evidence. Prepare a truthful PR and reviewer handoff. Publish only when separately authorized; a polished draft is a useful result when publication is not authorized.
5. Address review substance with changes and evidence, preserving scope and human-involvement requirements. Revalidate the latest head and distinguish author work from maintainer-only gates.
6. Verify the eventual outcome and retain a scoped lesson for the next contribution when supported by evidence. Consult historical evidence only when it can change the current decision; do not start an account-wide audit by default.

End each session with: target and head → completed change → exact test results → open feedback or blocker → next action and owner. Do not substitute a score or merge count for this deliverable.

Read [the contributor playbook](references/contributor-playbook.md) for beginner onboarding, issue triage, review comments, communication and advanced maintenance. Adapt explanation to experience; keep the same evidence and permission standards.

## Establish the task and evidence

`<skill-root>` is the absolute directory containing this `SKILL.md`. Resolve bundled helpers and assets from that directory, even when the current working directory is a contribution repository.

- Determine the repository or PR set, timeframe, requested deliverable, and authorized actions. Research, a draft, or use of this skill does not authorize posting, pushing, merging, or scheduled outreach.
- Read current `AGENTS.md`, contribution instructions, PR template, tests, AI policy, and any issue-specific maintainer direction. Respect required human understanding, review, and authorship; pause for genuine human participation where required. Never tick human or legal attestations on the user’s behalf merely to satisfy a template, rebrand prohibited generated work as human work, or bypass contribution restrictions.
- Read [the evidence method and ledger format](references/evidence-and-ledger.md) for a retrospective, broad inventory, or tracked review. Read [maintenance and incremental refresh](references/maintenance.md) when activity changes or a recurring refresh is requested.
- Use a private, authorized evidence ledger for real history. The bundled `assets/example-ledger.json` is synthetic and demonstrates the schema only, not real contributions. Query a ledger with `python3 <skill-root>/scripts/ledger.py summary PATH` or `show PATH --repository OWNER/REPO --number N`.
- Prefer the connected GitHub tools. When `gh` is available and authenticated, optionally use `python3 <skill-root>/scripts/collect_pr_evidence.py OWNER/REPO NUMBER --output PATH` for a read-only snapshot. It records per-section failures and the sampled head. Read actual linked diffs, policies, logs, and discussion; metadata alone is insufficient.

## Choose a contribution that belongs

Before substantial coding, establish a real problem on the current supported branch and a useful upstream owner or area. Check existing issues, required assignment/claim, competing PRs, recent fixes, release scope, and policy. Recheck freshness before submission. Prioritize unresolved review requests and a few complete contributions over new volume; honor current per-project open-PR limits and explicit cadence constraints. Do not convert one project’s limit into a universal quota.

Prefer bounded changes with an observable user or maintainer benefit and a credible test. A large diff can be justified; “small” alone is not evidence of value. If the current branch is unaffected, the change is already covered, the project forbids the proposed assistance, or the maintainer declines scope, stop that line of contribution and report the reason. Ask a concise scope question only when needed and when sending is authorized.

## Prepare evidence before requesting review

Read [reproduction and final validation](references/validation.md) when implementing or reviewing a patch. Record the base and final revision, reproduce the actual consumer behavior, establish failing-before/passing-after evidence when applicable, and run the repository’s required checks. Distinguish passing, failing, blocked and unrun checks; preserve user changes. Inspect feedback and CI on the current head before claiming readiness.

## Make the maintainer's decision easier

Prepare the repository's requested PR format. Include the problem and reproducer, why the chosen change fixes it, concise before/after evidence, exact verification, compatibility or risk, and any known limits. Link the relevant issue accurately. Disclose AI assistance when required and preserve truthful authorship and provenance. Do not fabricate benchmark numbers, tests, manual inspection, or maintainer statements.

When publication is authorized, default to a draft PR unless the user specifies otherwise. Follow repository-specific requirements that are compatible with platform policy. Do not publish just to increase counts.

Keep approved scope stable; explain necessary changes and seek renewed review rather than silently expanding it. For feedback, maintain a compact map: maintainer request → change or reasoned response → test or evidence. Address the substance before replying. Update stale branches only when needed and authorized, and recheck affected behavior afterward. Avoid empty progress comments, repeated review nudges, and automated “merged main” messages. Silence is not rejection; choose follow-up timing from explicit project expectations and the user's authorization, not a universal timer.

Merge, auto-merge, deployment, and external communication each retain their own authorization gates. A maintainer owns the upstream decision. Never bypass protections or imply the skill can secure acceptance.

## Learn and apply

For each outcome, record the strongest demonstrated positive, the main friction or improvement, what changed, and the remaining uncertainty. Separate:

- **Observation:** a test, comment, commit, check, or lifecycle event directly shows it.
- **Interpretation:** a bounded explanation supported by those facts.
- **Experiment:** a concrete process change to try next, with a way to judge it.

Count distinct repositories and distinct PR identities behind patterns. Separate native merge, full credited landing, partial credit, ports/backports, supersession, withdrawal, documented rejection, inferred disposition, unresolved closure, and open work. Deduplicate related ports before reporting unique changes. Record the final accepted scope and contributor/maintainer roles, not just the original title. Include non-wins and uncertainty. Do not infer causality from merge timing or pool unlike projects into a spurious acceptance score.

Recheck later feedback on merged or landed work when a follow-up is requested or relevant new activity appears. Preserve the original merge/landing and separately record a discovered defect, correction, revert, or unresolved report; merged does not mean correct or permanently complete.

Finish with a concise evidence-linked assessment: what worked, what improved, what remains blocked, and the next specific action. Update the task's approved contribution ledger in place when maintaining one; keep private retrospectives out of upstream repositories unless the user explicitly requests publication. Update the ledger when permitted evidence changes. Amend reusable guidance only for a meaningful demonstrated lesson, not every new merge; validate and verify the saved skill after an edit. Skill content does not create a running automation, broaden access, or grant GitHub write permission. Claim ongoing monitoring only after a supported schedule or event subscription is verified.
