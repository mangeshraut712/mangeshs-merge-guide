# Validation results and limits

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

On 12 November 2026, Node 24.22.0/npm 11.19.1 ran all 15 installer tests and 28 Python tests successfully. The initial installer tests failed because macOS temporary paths used a `/var` symlink; canonicalizing the freshly created test fixture directory fixed the harness without relaxing product symlink refusal. Deliberate symlink-rejection tests still passed. This does not establish native Windows support or successful agent-task invocation. The npm release remains pending.
