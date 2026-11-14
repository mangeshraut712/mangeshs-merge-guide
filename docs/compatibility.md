# Compatibility and validation — November 2026

Requirements below reflect the package manifest and CI configuration verified on 14 November 2026.

## Mangesh’s Merge Guide

The dependency-free installer retains its Node 20 minimum for compatibility, but new installations should use Node 22, 24 or 26. CI covers these maintained versions across Linux, macOS and Windows. No model SDK or runtime dependency is needed to copy the skill files.

Codex uses `~/.agents/skills`, Claude Code uses `~/.claude/skills`, and Cursor uses `~/.cursor/skills`; use the explicit installer target. Destination/file-integrity tests are distinct from running a contribution inside each host. Agent installation and authentication remain prerequisites.

Follow the [Codex skill format](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills](https://code.claude.com/docs/en/skills/) and [Cursor skills](https://cursor.com/docs/skills). Keep the compatibility invocation `oss-contribution-insights` while the visible project name is Mangesh’s Merge Guide. Refresh discovery or start a new host session after installation.

Run `npm test`, `npm run test:package`, and `python3 -B -m unittest discover -s skills/oss-contribution-insights/scripts -p 'test_*.py'`. These verify installer and evidence-tool behavior. Historical accepted PRs illustrate techniques; they are not a controlled experiment showing the skill caused acceptance.

## Verified 14 November 2026

The current source passed 18 installer tests, 28 Python helper/packaging tests, and packed Codex/Claude/Cursor install-and-upgrade journeys. All nine hosted Linux/macOS/Windows × Node 22/24/26 jobs passed. These are installer checks, not proof of end-to-end task execution in every agent runtime.

Release **0.1.2** includes rejection of cache-named symlinks and non-bytecode additions inside cache directories. Confirm registry availability with `npm view @mangeshraut712/merge-guide@0.1.2 version`; the existing 0.1.1 artifact remains unchanged.
