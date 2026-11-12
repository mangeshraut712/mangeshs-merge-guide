# Contributing to Mangesh’s Merge Guide

Beginners and experienced contributors are welcome. Useful contributions include clearer examples, reproducible helper bugs, accessibility improvements, repository-policy edge cases and tested workflow improvements. This project is MIT licensed; preserve provenance and do not copy material you cannot contribute under compatible terms.

## Start small

Search existing issues and PRs before starting. For substantial behavior changes, open an issue explaining the problem and proposed scope first. A label or comment is not a promise of acceptance. Do not open duplicate proposals or repeatedly ping reviewers.

Fork this repository, create a focused branch, and preserve any existing work. The installable skill lives in `skills/oss-contribution-insights`; the repository URL and invocation are retained for compatibility. README and these contributor files serve people and are outside the installable skill.

## Validate your change

Run from the repository root with Python 3.10+:

```bash
python3 -m unittest discover -s skills/oss-contribution-insights/scripts -p 'test_*.py' -v
```

For helper behavior changes, add synthetic regression tests that fail before the fix and pass afterward. Do not use real private ledgers, session histories or credentials as fixtures. Tests mock GitHub responses; report live-access tests separately. Check Markdown links and examples. For guidance changes, include a realistic scenario showing what decision changes and why, including a counterexample when appropriate. Do not claim a merge proves causation or correctness.

## Open a reviewable PR

Explain the problem, bounded change, exact validation and remaining limitations. Disclose material AI assistance and personally review what you submit. Never invent human testing or authorship. Keep commits free of secrets, private paths, raw contribution histories and unrelated generated files. Do not change permissions, credentials, workflows or automatic publication behavior as incidental cleanup.

Respond to feedback with evidence rather than repeated nudges. Only a maintainer can decide acceptance. A green test suite is necessary evidence where applicable, not guaranteed approval or a promise of response timing.

## Improving the guide

Prefer demonstrated problems and repeatable validation over new rules based on one anecdote. Scope repository-specific advice to that repository. Keep the contribution workflow first and analytics optional. New languages or tools should solve a concrete problem rather than add prestige or complexity. Avoid collecting personal data or adding telemetry by default.

## Security and privacy

Do not post secrets, private logs or exploitable vulnerability details in public issues. Use a private reporting method explicitly published by the maintainer if one is available; this repository does not currently document a verified private reporting channel or response SLA. If none is available, withhold sensitive details and ask how to share them privately without including the exploit or data. A public issue template is not a private channel.
