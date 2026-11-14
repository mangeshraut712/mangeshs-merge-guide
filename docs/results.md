# Validation results and limits

## November 14 upgrade regression

Release 0.1.1 passes 16 installer tests, including a failing-before/passing-after regression for managed upgrades after Python helpers generate bytecode. Packed Codex, Claude and Cursor installs preserve the complete backup and still refuse edited source or additional notes. Independent review found no blockers. npm accepted version 0.1.1 and the registry confirms it is available. All nine hosted checks passed on Linux, macOS and Windows with Node 22, 24 and 26.

## November 13 registry and installed-skill verification

Fresh-cache `npx @mangeshraut712/merge-guide@0.1.0` checks passed on macOS with Node 26.13.0: Codex, Claude Code and Cursor project installs, write-free dry runs, refusal to overwrite, managed upgrades, and refusal to upgrade edited files without changing them. This verifies the published registry release, superseding the earlier pending-publication note below.

The current source also passes 15 installer tests, 28 helper/packaging tests, 3 adoption tests, and expanded packed-package checks that verify upgrade backups and preservation of local edits for all three targets. A first-reader scenario check found that helper paths depended on the working directory; commands now resolve from the installed skill root. The anchored ledger command was executed successfully outside the skill repository against synthetic data. These checks do not certify native agent task invocation or maintainer acceptance.

## November 12 maintenance refresh

Local macOS / Node 26.13.0: 15 installer tests, 28 evidence-helper tests, and 3 analytics tests passed. Packed installs into isolated Codex, Claude Code and Cursor targets verified complete file parity, dry runs and refusal to overwrite existing files. The skill metadata validator passed. The detailed validation workflow moved into a linked reference; it remains part of the installed package. This does not measure model quality or contribution acceptance.

The current CI matrix targets Node 22, 24 and 26 on Linux, macOS and Windows. Check the latest [release-check run](https://github.com/mangeshraut712/mangeshs-merge-guide/actions/workflows/ci.yml) for the exact revision and outcomes. Earlier results below remain dated historical evidence.

## Earlier audit

Observed 12 November 2026 against public commit [1fc6cf2](https://github.com/mangeshraut712/mangeshs-merge-guide/commit/1fc6cf2730c1f0aa9a1ec325534e10be7ddecb36). This is a reproducibility report, not a merge-rate or adoption claim.

| Check | Observed result | Boundary |
| --- | --- | --- |
| Public package | 20 files matched published Git blob hashes | Source export, not a fresh unauthenticated clone |
| Folder-only installation | Complete skill and MIT notice copied into isolated home | Existing Linux host, not a fresh operating system |
| No-overwrite instructions | Empty target succeeded; existing directory, file and dangling symlink refused unchanged | POSIX shell; not concurrent installer protection |
| Codex discovery | Enabled user skill, exact Mangesh’s Merge Guide title/default prompt, zero errors | Codex 0.167.0-alpha.4 only |
| Repository helpers | 28 tests passed | Offline tests with synthetic or mocked data |
| Installed-folder tests | 27 passed, one expected repository-parity skip | No repository root in standalone installation |
| Native task invocation | Blocked before thread start by host sandbox setup | No successful model execution or authentication established |

The invocation error was `app-server socket directory must be a user-owned directory with mode 0700`. No credential copying, security bypass or permission workaround was performed. This host failure is not evidence of a failed package installation; discovery and execution are separate checks. Do not treat these results as Windows, macOS, all-runtime or live GitHub collector certification.

## Fixes driven by first-reader testing

- [Preserved the MIT notice in standalone installations](https://github.com/mangeshraut712/mangeshs-merge-guide/commit/99975c7f728f813b750caf1907ee6fe5779e5161), with packaging regression tests.
- [Clarified first-time installation](https://github.com/mangeshraut712/mangeshs-merge-guide/commit/9e7261db02b2d9f726f7c5d988e49fefd1d3dddc), prerequisites and distinct verification stages.
- [Fixed public CLI interface metadata](https://github.com/mangeshraut712/mangeshs-merge-guide/commit/1fc6cf2730c1f0aa9a1ec325534e10be7ddecb36) after a controlled comparison. This does not alter separately managed personal-skill requirements.

The broader guide has also been applied manually to an existing issue as a separate read-only exercise. That does not establish native invocation, an independently tested upstream fix or maintainer acceptance. No merge improvement percentage is supported.

## Native macOS release check

On 12 November 2026, Node 24.22.0/npm 11.19.1 ran all 15 installer tests and 28 Python tests successfully. The initial installer tests failed because macOS temporary paths used a `/var` symlink; canonicalizing the freshly created test fixture directory fixed the harness without relaxing product symlink refusal. Deliberate symlink-rejection tests still passed. This does not establish native Windows support or successful agent-task invocation. The npm release was still pending at that stage.


## Version 0.1.0 release validation

The renamed repository was freshly cloned from `mangeshraut712/mangeshs-merge-guide`. On 12 November 2026, local macOS validation with Node 26.13.0/npm 11.20.0 passed 15 installer tests, 28 Python tests, and packed CLI installation checks for all three explicit target destinations. All 27 local Markdown file links resolved; no GitHub links to the old repository name remained. The installed skill identifier intentionally remains `oss-contribution-insights`.

[Native CI on commit 09d4106](https://github.com/mangeshraut712/mangeshs-merge-guide/actions/runs/43182990902) passed all six Linux/macOS/Windows × Node 20/24 jobs. Every job ran:

- All 15 installer tests, including refusal of symlinks, edited installations and existing destinations.
- `npm pack` and execution through the packaged CLI for Codex, Claude Code and Cursor project destinations: dry run without writes, full byte-for-byte source parity, marker version/hash checks, and refusal to overwrite.
- All 28 offline Python helper and packaging tests.

The first matrix run exposed a Windows/Node 20 shell-glob difference in the test command. Naming the installer test file explicitly fixed the harness; no tests were removed or skipped. Native installer checks do not certify agent discovery, model invocation, every ACL configuration or every IDE version. The earlier host startup limitation remains relevant to task invocation.

The prepared release package is [`@mangeshraut712/merge-guide@0.1.0`](https://www.npmjs.com/package/@mangeshraut712/merge-guide). The tarball allowlist contains 24 public files, no runtime dependencies and no install hooks. Public registry installation is a separate final release check from the local tarball smoke tests above. npm publication was attempted and rejected with E403 because the account requires 2FA. At that earlier checkpoint, the registry release and post-publication npx check were pending. The November 13 verification above confirms the subsequent publication.
