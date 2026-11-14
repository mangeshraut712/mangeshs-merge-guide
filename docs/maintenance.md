# Maintaining the project

Keep the execution workflow useful and reviewable; avoid adding rules simply because a count increased.

1. Start from a reproducible helper problem, a scoped contributor difficulty, or an evidenced policy change. Link permissible public sources or use synthetic examples. Never commit private retrospective ledgers or session logs.
2. Propose a bounded change and its counterexample. Single-project lessons remain scoped to that project. Distinguish observations from interpretations and avoid acceptance guarantees.
3. For code, run the documented tests and add regression coverage. For instruction changes, use a fresh scenario without giving the evaluator the intended conclusion. Evaluate whether the output is actionable and respects evidence/authorization.
4. Review the diff independently where practical. Check links, installable-folder integrity, license parity, interface compatibility, truthful result claims and supported runtimes.
5. Verify published content after release. Record tested versions and limitations in the results documentation rather than silently broadening claims.

The repository and personal ChatGPT skill are separate copies. Neither updates the other automatically. This project does not itself schedule monitoring, install a daemon, send maintainer messages or grant GitHub access. Maintaining a real contribution ledger needs a separately authorized private location and complete checkpoints; see the skill's [incremental evidence guidance](../skills/oss-contribution-insights/references/maintenance.md).

Contributions are welcome through [CONTRIBUTING.md](../CONTRIBUTING.md). Do not change accounts, credentials, permissions or auto-publication behavior as incidental maintenance.

## Publishing with provenance

Release 0.1.3 introduces the manually dispatched `release.yml` workflow. Ordinary pushes do not publish. After the exact main commit passes all nine release checks, dispatch **Publish npm with provenance** on main. The workflow repeats installer, packed-package and Python validation before publishing from a GitHub-hosted runner with `id-token: write`. Configure `NPM_TOKEN` as a repository secret with publishing access to this package and the npm permissions required for unattended publication; never commit the token.

The package enables `publishConfig.provenance`. Release publication must use the hosted workflow, not a local terminal. Confirm registry availability, download the public tarball, verify the provenance attestation and run fresh-cache npx installation checks before announcing success. Release 0.1.2 remains available without provenance; its artifact is unchanged.
