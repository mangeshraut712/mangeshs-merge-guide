# OSS Contribution Insights

An evidence-based skill for making useful, reviewable open-source contributions and learning from their outcomes. It helps separate what worked, what needs improvement, and what remains unverified. It does not promise merges or automate maintainer outreach.

## What it does

- Checks contribution policies, competing fixes, scope and current review ownership before coding.
- Requires behavioral regression evidence, actual runtime wiring and final-head validation.
- Distinguishes GitHub merges, credited landings, partial credit, ports and unresolved closures.
- Records post-merge corrections without erasing historical acceptance.
- Keeps observation, interpretation and the next experiment separate.

## Beginner to experienced contributor

The [contributor playbook](skills/oss-contribution-insights/references/contributor-playbook.md) covers first-issue setup, triage, fixes, PR preparation, review comments, respectful disagreement, blocked checks, complex changes and post-merge follow-through. Communication examples are private draft structures, never automatic messages. Expertise changes the depth of explanation, not the verification standard.

## Use the skill

The skill folder is [`skills/oss-contribution-insights`](skills/oss-contribution-insights). Copy that complete directory to a skills location supported by your agent. For Codex, review the files, then copy it into `~/.agents/skills/oss-contribution-insights` without overwriting an existing installation. Invoke `$oss-contribution-insights`, for example:

> Review these PRs, distinguish verified outcomes from uncertainty, and identify the smallest useful next contribution. Do not post or modify repositories.

This GitHub copy is separate from any personal skill installed in ChatGPT. Updating one does not automatically update the other. This repository does not install schedules or enable access to accounts.

## Helpers

Python 3.10+; the optional live collector also requires an already authenticated GitHub CLI (`gh`). No third-party Python packages are required by the helpers.

```bash
python3 skills/oss-contribution-insights/scripts/ledger.py summary skills/oss-contribution-insights/assets/example-ledger.json
python3 skills/oss-contribution-insights/scripts/collect_pr_evidence.py OWNER/REPO NUMBER --output /path/to/private/new-snapshot.json
python3 -m unittest discover -s skills/oss-contribution-insights/scripts -p 'test_*.py' -v
```

The collector performs GET requests only. It records partial failures and head changes; it does not fetch repository policy, diffs or logs, verify tests, or publish anything. Offline tests use mocked responses; a green test suite is not proof of live GitHub access.

## Privacy and scope

This public package contains generic guidance, code and synthetic examples only. No personal contribution ledger, private retrospective, session history, credentials or watcher checkpoints are included. Keep collected evidence outside this checkout and review it before sharing. A PR inventory is not an inventory of every kind of GitHub contribution.

Permissions remain separate: using the skill does not authorize external messages, pushes, PRs, merges, account changes or scheduling. Respect repository AI/human-authorship policies and access denials. Do not use another identity or route to bypass restrictions.

## Provenance and development

Adapted from the author's personal OSS Contribution Insights skill, with private research removed. This is an independent community project, not an official GitHub or OpenAI product. The earlier [Codex Insights](https://github.com/mangeshraut712/codex-insights) project inspired the repository-plus-skill packaging; no source code from that project is copied here.

Changes should include relevant offline tests and sourced, scoped reasoning. Do not turn a single merge into a universal success rule. Never commit real account-wide evidence as a test fixture.
