# Worked contribution examples

These three examples are **synthetic**, not claims of submitted or merged work. Use them as task patterns. Actual authorization and repository policies still apply.

## Beginner: a reproducible bug

**Request:** “Help with this issue. Work locally and prepare a PR draft; do not publish.”

1. Read issue context, current contribution instructions and competing PRs. If an active fix exists, inspect it rather than starting a duplicate.
2. Record supported version and base revision. Reproduce the reported failure using the project's documented test harness.
3. Add a behavioral test that fails for the same reason. Implement the bounded fix and rerun it; run applicable final checks.
4. Prepare a handoff with the problem, fix, red/green evidence, exact commands and remaining limits. Do not invent successful execution.

**Example output structure:** Target/head → reproduced failure → changed files → failing-before/passing-after checks → unrun checks → draft PR → author or maintainer next step.

**Stop condition:** the supported branch is already fixed, the issue is claimed, reproduction fails, or project policy forbids the proposed assistance. Report the specific reason rather than manufacturing a patch.

## Existing PR: respond to a review

**Request:** “Address this review on my current PR. Draft the response but do not send.”

Suppose a reviewer asks whether a new helper is called by the public API. Inspect actual wiring and current head, not only helper tests. Add or run a consumer-level regression where authorized. Map each comment to the change/evidence or a reasoned explanation.

**Draft pattern, only when facts are verified:** “The public entry point now exercises [path]. [Test command] covers [behavior] on [head]. [Remaining limitation].”

A reviewer request is evidence of wanted work, not permission for unrelated API changes. Do not resolve threads or publish replies automatically. A passing test does not replace required approvals.

## Expert: native-library compatibility

**Request:** “Investigate this C++ crash and prepare a compatible fix.”

Confirm compiler, standard, build configuration and affected version. Reduce the crash; examine ownership and undefined behavior. Prefer a fix preserving public layout and ABI when required. Run regression tests and supported sanitizer configurations separately. Document platforms and configurations not tested.

**Decision example:** a private implementation correction may be preferable to changing a public structure if both solve the defect, but prove the choice against this project's contract. Do not assert universal ABI safety or a performance improvement without measurement.

See [C/C++ contribution guidance](../skills/oss-contribution-insights/references/c-cpp-contributions.md).

## Run the bundled synthetic evidence example

From the source repository, with Python 3.10+:

```sh
python3 skills/oss-contribution-insights/scripts/ledger.py summary skills/oss-contribution-insights/assets/example-ledger.json
```

This reads only the bundled synthetic ledger and prints a summary. It does not query GitHub, modify a repository, publish a PR or contact a maintainer. Compare the output with the fixture rather than interpreting its example counts as the author's contribution history.

To preview installation without changing your agent configuration:

```sh
node bin/merge-guide.js install --target codex --scope project --dry-run
```

Expected output is a JSON description with `dryRun: true`, the destination and the planned file count. Exact paths depend on your checkout. Remove `--dry-run` only when you want the installation; an existing target is refused. See [installer options](installer.md).
