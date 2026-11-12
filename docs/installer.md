# Terminal installer

The installer copies the bundled skill to an explicit agent destination. It does not install or authenticate the agent, run a model, upload evidence, add telemetry, start background jobs or change account settings.

## Current availability

Source implementation and a locally packed `npx` installation were tested on Linux with Node 24.22.1 and npm 11.9.0. The proposed registry package `@mangeshraut712/merge-guide` is **not published**. Registry checks returned E404 and the available environment has no authenticated npm publisher. Do not use `npx @mangeshraut712/merge-guide` as though it is already released.

After reviewing/downloading this repository, from its root:

```sh
node bin/merge-guide.js install --target codex --dry-run
node bin/merge-guide.js install --target codex
```

To test the real npm packaging locally (no registry publication):

```sh
npm pack
npx --package ./mangeshraut712-merge-guide-0.1.0.tgz merge-guide install --target codex --dry-run
npx --package ./mangeshraut712-merge-guide-0.1.0.tgz merge-guide install --target codex
```

These commands use Node/npm, not POSIX-specific copy syntax; npm may ask for execution consent. Node 20+ and npm are prerequisites. A verified registry release can later shorten the command; a package name is not ownership proof.

## Destinations and compatibility

| Target | User scope (default) | Project scope |
| --- | --- | --- |
| `--target codex` | home `.agents/skills/oss-contribution-insights` | current directory `.agents/skills/oss-contribution-insights` |
| `--target claude` | home `.claude/skills/oss-contribution-insights`, or `CLAUDE_CONFIG_DIR/skills/...` | current directory `.claude/skills/oss-contribution-insights` |
| `--target cursor` | home `.cursor/skills/oss-contribution-insights` | current directory `.cursor/skills/oss-contribution-insights` |

Use `--scope project` only from the intended repository root. `--dest PATH` selects the **exact skill folder**, is mutually exclusive with `--target`, and does not certify that another agent supports this format.

Official documentation: [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills/), [Claude configuration roots](https://code.claude.com/docs/en/claude-directory), [Cursor](https://cursor.com/docs/skills). Codex uses `$oss-contribution-insights`; Claude Code uses `/oss-contribution-insights`; Cursor exposes skills through its supported selector. Verify discovery in your installed version.

Native Windows/macOS execution and Claude/Cursor discovery have **not** been tested here. Native path handling plus Windows/POSIX path simulations are not full OS testing. This is not universal IDE support, cloud installation or synchronization. A working agent runtime remains required; the earlier Codex task invocation was host-blocked despite successful discovery.

## Existing installations and upgrades

By default existing directories, files and symlinks are refused. The installer also refuses symlink ancestors, so symlinked home/config paths need deliberate inspection and an explicit real destination, not a blind workaround.

`--upgrade` accepts only a previous installer-managed directory whose recorded files are unchanged and which has no additional files. Manual installations and edited copies are refused. A successful upgrade retains a complete sibling backup and prints its path; it does not delete the backup automatically. Keep private ledgers outside the skill folder. Running Python inside an installed copy can add `__pycache__` files that deliberately block a later upgrade; use `python3 -B` when running its tests to avoid new bytecode. Inspect and preserve existing additions manually rather than expecting automatic deletion. Generated Python caches are excluded from the source copy and npm package. A stale `.install-lock` needs inspection before any manual cleanup; do not remove a lock while another installation is active.

The lock coordinates instances of this installer, not hostile filesystem mutations or every third-party installer. Stop other writers first. `--dry-run` checks the plan but cannot guarantee that state will remain unchanged afterward.

## Maintainer validation and release

```sh
npm test
npm pack --dry-run
```

Review the allowlisted manifest: only installer, skill sources, synthetic example, public documentation/metadata and MIT notices belong in a package. No private data, bytecode, tokens or machine paths. There are no npm lifecycle scripts or dependencies.

Publishing is separate: verify the correct npm identity and scope ownership through supported authentication, comply with npm's required approval/2FA flow, and verify the resulting registry version and a fresh npx install before announcing release. Do not register accounts, create tokens or change credentials just to bypass an access failure. See [npm publishing requirements](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages).
