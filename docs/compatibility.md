# Compatibility and validation — November 2026

Use maintained LTS runtimes. [Node’s release table](https://nodejs.org/en/about/previous-releases) lists Node 22, 24 and 26 as LTS in November 2026; Node 18 and 20 are end-of-life. Repository constraints take precedence over upgrading an upstream contributor’s toolchain just because a newer version exists.

## Mangesh’s Merge Guide

The dependency-free installer retains its Node 20 minimum for compatibility, but new installations should use Node 22, 24 or 26. CI covers these maintained versions across Linux, macOS and Windows. No model SDK or runtime dependency is needed to copy the skill files.

Codex uses `~/.agents/skills`, Claude Code uses `~/.claude/skills`, and Cursor uses `~/.cursor/skills`; use the explicit installer target. Destination/file-integrity tests are distinct from running a contribution inside each host. Agent installation and authentication remain prerequisites.

Follow the [Codex skill format](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills](https://code.claude.com/docs/en/skills/) and [Cursor skills](https://cursor.com/docs/skills). Keep the compatibility invocation `oss-contribution-insights` while the visible project name is Mangesh’s Merge Guide. Refresh discovery or start a new host session after installation.

Run `npm test`, `npm run test:package`, and `python3 -B -m unittest discover -s skills/oss-contribution-insights/scripts -p 'test_*.py'`. These verify installer and evidence-tool behavior. Historical accepted PRs illustrate techniques; they are not a controlled experiment showing the skill caused acceptance.
