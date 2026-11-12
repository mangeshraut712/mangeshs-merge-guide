# C and C++ contribution track

Use when the target project is C or C++. A contribution skill is primarily instructions; rewriting a small network/JSON evidence helper in C++ does not inherently improve contributions. Choose implementation language from the target repository and measurable needs, not prestige. Introduce native tooling only with a concrete benefit, an agreed interface and relevant tests.

## Establish the build and failing behavior

- Read the supported compiler, language standard, build system and platform matrix. Record actual compiler executable/version, generator and dependency versions. Use the repository's presets or documented CMake, Meson, Bazel, Make or other commands; do not invent a universal build invocation.
- Keep build outputs outside source files as the project expects. Reproduce with its prescribed debug/test configuration and the actual library/application under test. Beware stale installed libraries, wrong shared-library lookup paths and configuration-dependent tests.
- Reduce the issue to a bounded reproducer that fails on the recorded base and passes after the fix. Distinguish a compiler warning, crash, memory error, race, numerical discrepancy and API-contract failure. A passing compilation is not a behavioral test.

## Fix the real contract

- Check lifetime/ownership, iterator and reference invalidation, integer conversion/overflow, bounds, initialization, error propagation and exception safety where applicable. Preserve resource cleanup on early failure. Avoid repairing a symptom while introducing undefined behavior.
- Preserve supported language versions and C/C++ linkage. For public libraries check ABI/API compatibility, exported symbols, struct layout/alignment, calling conventions and downstream consumers as relevant. Do not change layouts or signatures silently.
- Validate platform-specific code on the real supported platform where possible. Consider pointer/size widths, signedness, endianness, alignment, compiler extensions and Windows/POSIX differences. A renamed mock fixture is not cross-platform testing.
- Keep security contracts, input bounds and concurrency invariants intact. Do not disable validation or synchronization just to make a test pass. Handle vulnerability findings under the project's disclosure policy.

## Validate proportionately

- Run the repository's focused regression and required aggregate tests, formatting, static analysis and warning policy. Use its supported sanitizer configurations: ASan for memory errors, UBSan for undefined behavior, and TSan for races where compatible. These are complementary configurations, not universally combinable flags. Report unavailable or unsupported sanitizer runs honestly.
- For performance changes compare equivalent optimized builds and repeat representative workloads, recording hardware, compiler flags, noise and correctness checks. Do not claim a speedup from one debug run or change workloads to favor the patch.
- Exercise error and boundary paths. For concurrency fixes use deterministic coordination where practical; stress tests alone cannot prove race freedom. Fuzz only within authorized resources and scope.
- Record final head, exact commands and results, including skipped platform jobs. A green local Linux build does not certify macOS/Windows, all compilers or an ABI guarantee.

## Maintainer handoff

Explain the original failure, why the fix respects ownership/compatibility constraints, the regression evidence, supported configurations tested and residual limitations. Keep a code change small enough to review but complete enough to solve the issue. Do not submit speculative refactors or demand an upstream C/C++ rewrite when a project uses another language.
