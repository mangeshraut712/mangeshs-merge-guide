# Beginner walkthrough: from install to a weekly PR check

This walkthrough uses Claude Code and the plugin. The same skill works in the other runtimes listed in the [README](../README.md#terminal-installer); there, you invoke it by its folder name, `oss-contribution-insights`.

## 1. Install and confirm the skill loads

```text
/plugin install mangeshs-merge-guide --marketplace mangeshraut712/mangeshs-merge-guide
```

Run `/plugin` and check that `mangeshs-merge-guide` is listed and enabled. If it is missing, see [troubleshooting](troubleshooting.md).

## 2. Pick one issue

Ask for help choosing, and give Claude the repository you care about:

```text
/mangeshs-merge-guide:oss-contribution-insights
Find a beginner-sized open issue in OWNER/REPO that nobody is working on, and explain why it fits.
```

Before writing code, read the project's contributing guide. If the issue isn't clearly open to outside contributors, comment on it and ask whether a fix would be welcome.

## 3. Reproduce, fix and test

Ask Claude to reproduce the bug on the current default branch first. A fix is ready when there is:

- a test that fails before the change and passes after it
- a run of the project's own required checks

Claude reports which checks passed, failed or were not run. Read that list before you open the PR.

## 4. Open a PR that is easy to review

Keep the change small. Match the title and description style of recently merged PRs in the same repository. Say what was wrong, what changed and how you tested it. If AI helped, say so, following the project's policy.

## 5. Check your open PRs once a week

These helpers need Python 3.10 or later and an authenticated `gh` CLI (`gh auth status`). The easiest way is to ask Claude to run them, because it knows where the plugin installed the scripts. To run them yourself, use the `scripts/` folder inside a clone of this repository's `skills/oss-contribution-insights/`.

```bash
python3 scripts/open_pr_triage.py --author YOUR_LOGIN
```

Act on the groups at the top: conflicts and unanswered change requests need you. "Approved" and "Waiting for a first review" need a maintainer, so leave those alone.

Before you post on a PR that has waited a while, save a snapshot and check it for noise. The collector won't overwrite a file, so use a new file name each time:

```bash
mkdir -p ~/pr-notes
python3 scripts/collect_pr_evidence.py OWNER/REPO NUMBER --output ~/pr-notes/REPO-NUMBER.json
python3 scripts/noise_check.py ~/pr-notes/REPO-NUMBER.json
```

If it reports repeated merges from `main` or several unanswered comments in a row, don't add another one. Post again only when you have new information or a maintainer asks.

## 6. Learn from your own history

Once you have a few merges, see how they landed:

```bash
python3 scripts/merge_stats.py --author YOUR_LOGIN
```

Then compare the result with [lessons from 105 merged PRs](../skills/oss-contribution-insights/references/lessons-from-merges.md).

The skill never merges, approves or pings on your behalf. Every one of those actions is yours to take.
