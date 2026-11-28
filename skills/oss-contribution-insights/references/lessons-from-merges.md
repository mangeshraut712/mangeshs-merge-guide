# Lessons from 105 merged pull requests

These patterns come from the maintainer's own history: 105 pull requests merged into 47 repositories they do not own, between July and November 2026. Personal and test repositories (`Roojool`, `dayx61`) are excluded. The numbers describe one contributor's history and show correlation, not cause. Use them to decide where to spend effort, not as promises about any project.

Reproduce or update them for any author:

```bash
python3 <skill-root>/scripts/merge_stats.py --author LOGIN [--exclude-owner OWNER ...] [--json]
```

## 1. Merges come quickly or not at all

- The median time from opening to merge was 2.5 days.
- 34 PRs merged within a day, 74 within a week, and all 105 within 26 days.
- When this was measured, 64 of 108 open PRs were older than the slowest merge.

What to do: a PR with no maintainer activity after about four weeks is unlikely to merge as it stands. Don't respond with pings or merges from `main` (see `noise_check.py`). Choose one of these:

- If you have new information, post a single update that contains it.
- If the project says how to escalate, follow that.
- Otherwise, spend your time on a repository that is responding.

`open_pr_triage.py` marks PRs stale after 30 days by default for this reason.

## 2. Depth beats breadth

- 33 of the 47 repositories have exactly one merge.
- The 10 repositories with three or more merges account for 64 of the 105.

What to do: once a repository has merged your work, its maintainers know your style and you know theirs. Look for the next issue there before opening a first PR somewhere new.

## 3. Short threads go with fast merges

- PRs with 0–2 conversation comments merged in a median of 2.2 days (68 PRs).
- PRs with 3 or more comments took a median of 6.6 days (37 PRs).

Long threads usually mean more review rounds, so this is correlation. Still, it supports two habits:

- Settle the scope before you open the PR: link the issue, show the reproduction, and say what is out of scope.
- Answer a review in one consolidated update rather than a comment per point.

## 4. Issue links and test notes are expected, not an advantage

- 87 PRs link an issue and 78 describe how the change was tested. Both counts come from a heuristic match on the PR description.
- The PRs that left these out merged no slower.

What to do: treat them as the minimum. They don't make up for a change that is too large or a scope the maintainer didn't agree to.

## 5. Follow the repository's conventions, not a universal one

Conventional-commit titles (`fix(scope): ...`) merged more slowly than other titles (median 4.1 days against 1.3). The difference tracks which repositories use them, not the title style itself. Copy the title and description format of recently merged PRs in the same repository.

## What this does not measure

- Review rounds, requested changes and CI reruns. The sample came from GitHub search, which doesn't include them. For a single PR, use `collect_pr_evidence.py`.
- PRs that were closed without merging. Many were closed by the author within a day, for example as duplicates or to retarget a branch, so they say little about how maintainers respond.
- Anything outside these 47 repositories. Read each project's contributing guide and recent merged PRs before applying these patterns to it.
