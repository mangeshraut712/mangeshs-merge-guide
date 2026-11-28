# November 2026 contribution skill review

On November 28 we checked the 105 distinct PRs in the public scoreboard’s external merge evidence against GitHub. All 105 had a merge timestamp. They span 47 repositories; 94 have at least one review record (including automated reviews) and 61 changed three files or fewer. We inspected titles, changed paths, review counts and merge status. These are observations from selected successes. They cannot estimate acceptance probability or the effect of AI. [Pinned scoreboard](https://github.com/mangeshraut712/mangeshraut712/blob/6b5ed6a37c6cbbc5a5328499c08e2984710f8143/data/oss-scoreboard.json)

| Priority | Evidence | Decision |
|---|---|---|
| 1. Identify the next person who can act | Local regression tests passed while the upstream workflow still required approval on [Claude Agent SDK #1536](https://github.com/anthropics/claude-agent-sdk-python/pull/1536#issuecomment-7234506497). | Collect workflow runs for the exact head alongside checks and statuses. Preserve partial results when access is limited. |
| 2. Give maintainers reproducible decisions | [Carbon #24019](https://github.com/carbon-design-system/carbon/pull/24019) identifies the keyboard sequence that resets the picker. [NVIDIA #3224](https://github.com/NVIDIA/cuda-python/pull/3224) distinguishes inherited filesystem permissions from a cache-mode regression. | Teach contributors to record the consumer action, expected outcome and runner details. Queue a reviewed revision for integration only while its checks and reviewed head still match. |
| 3. Make the same skill usable across hosts | The existing [Claude plugin proposal](https://github.com/mangeshraut712/mangeshs-merge-guide/pull/11) documents demand for native discovery. | Keep its proposal independent. Ship the same portable skill, examples and standard-library collector through the existing Codex, Claude and Cursor installer. |

The current Agent Skills specification supports progressive disclosure through Markdown, scripts and references. Claude Code supports skill discovery and plugin distribution, and Cursor documents skill discovery for its agent. These capabilities fit the existing installer. The evidence collector uses the GitHub workflow-runs REST endpoint and Python’s bounded thread pool; it needs no inference service or provider key. [Agent Skills specification](https://agentskills.io/specification) · [Claude Code skills](https://code.claude.com/docs/en/skills) · [Cursor skills](https://cursor.com/docs/skills) · [GitHub workflow runs](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository)

## Try it

Start with the [installer walkthrough](installer.md) and [worked examples](examples.md). Ask your agent: “Read this PR and tell me which step I can take locally and which needs a maintainer.” A useful response identifies the revision and a specific test or upstream decision. For a reproducible snapshot, run the installed helper from the directory containing SKILL.md:

```sh
python3 scripts/collect_pr_evidence.py OWNER/REPO NUMBER --output pr-evidence.json
```

Choose an unused filename. Exit 2 means some evidence was missing or changed during collection. Open the JSON, read the named error and retry only after the condition changes. A completed collection can still contain zero workflow runs. Use the [troubleshooting guide](troubleshooting.md) and include a redacted observation and expected outcome in the [feedback template](../.github/ISSUE_TEMPLATE/workflow_improvement.md).

## Maintainer acceptance and review cadence

For each release, exercise the installer and package smoke tests, the Python suites, and a beginner scenario using a PR whose CI needs authorization. Check that the operator can identify the next owner without sharing a raw snapshot. Ask a new contributor to try the walkthrough and record where they needed help. Review feedback monthly and revisit the linked host specifications before changing install paths or adding a dependency.
