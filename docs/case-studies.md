# Three accepted contributions: facts and transferable decisions

Public GitHub PR metadata and changed-file patches checked on 12 November 2026. Each PR below is authored by `mangeshraut712`, has `merged: true` and a non-null merge timestamp. These are selected examples, not a complete contribution inventory or controlled experiment. No private ledger is published. Test code was inspected; upstream tests were **not rerun** for this documentation. Acceptance does not prove the guide caused a merge or that code cannot have later defects.

## 1. Fix the real CLI entry point

**Accepted contribution:** [Walmart Labs JSON-to-GraphQL #50](https://github.com/walmartlabs/json-to-simple-graphql-schema/pull/50), merged 11 November 2026 at 21:05 UTC. [Acceptance commit](https://github.com/walmartlabs/json-to-simple-graphql-schema/commit/47b855cb101981812f4bebf3cbde44b5488bfe7e).

**Problem reported:** the CLI's yargs subpath import failed under Node 22+. **Observed change:** `app.js` imports the package root instead. The [reviewed test](https://github.com/walmartlabs/json-to-simple-graphql-schema/blob/ab93dc5a8ab80c5ec32495da2f7dcb0ee5ce8585/test/integration.spec.js) spawns `node app.js` with `--baseType` and `--prefix`, supplies a fixture through stdin and asserts the generated schema.

**Evidence boundary:** the PR reports 12 tests passing plus lint/format checks. That is author-reported execution, not a new independent run here. The code demonstrates an entry-point integration assertion, not a certified all-Node-version compatibility matrix.

**Decision to reuse:** test the command users actually run, including options and input flow, rather than proving only a library helper works. This is a test-design lesson, not an established reason the maintainer accepted the PR.

## 2. Assert the user-visible diagnostic contract

**Accepted contribution:** [AWS Labs Stickler #553](https://github.com/awslabs/stickler/pull/553), merged 11 November 2026 at 22:24 UTC. [Acceptance commit](https://github.com/awslabs/stickler/commit/f6a0493e13df0733d4678c965dc73ac6ef9ae06d).

**Problem reported:** warnings from the public `StructuredModel.compare_with` call pointed at an internal library line. **Observed change:** explicit stack levels account for the wrapper and `warn_once` frames, with a changelog entry. The [regression file](https://github.com/awslabs/stickler/blob/0be6e62aad79a2300362cc5c227fea1c73c15acd/tests/structured_object_evaluator/test_compare_with_warning_stacklevel.py) calls the public API and asserts warning category, filename and exact caller line. It resets warning memoization so the test can observe the warning.

**Evidence boundary:** the PR reports focused and broader verification. This documentation verifies the assertions in the public patch, not execution of the full suite or every diagnostic path.

**Decision to reuse:** define observable success precisely. “A warning happened” would not prove its location is useful to a caller. Test the contract the user depends on, including relevant wrappers.

## 3. Test keyboard behavior, not merely handler configuration

**Accepted contribution:** [Adobe React Spectrum #10868](https://github.com/adobe/react-spectrum/pull/10868), merged 11 November 2026 at 21:46 UTC. [Acceptance commit](https://github.com/adobe/react-spectrum/commit/6fc06c8e39770dd5530809b85a6fbdef94d86afc).

**Problem reported:** select-all handling in an open multi-select ComboBox interfered with selecting input text. **Observed change:** `disallowSelectAll: true` is passed to the collection behavior. The [final-head test](https://github.com/adobe/react-spectrum/blob/c613318748179d3c7377ea9319ad01ea1c0fdf75/packages/react-aria-components/test/ComboBox.test.js) opens the popover, focuses input, sends Ctrl+A, checks selection bounds, types replacement text, checks filtered options and asserts that option-selection callbacks were not triggered.

**Evidence boundary:** this inspected test uses Ctrl+A and a test environment. It does not independently establish every browser, OS modifier or assistive-technology interaction. The original PR summary is less detailed than the final patch, so the final patch is the source for the test description.

**Decision to reuse:** exercise the promised interaction and relevant side effects. Verify final accepted code, not only the original PR description or a configuration flag.

## Apply without overgeneralizing

All three show bounded changes with explicit behavioral assertions in accepted patches. That common observation does not isolate the cause of acceptance. Project need, policy, competing work, reviewer judgment and timing differ. Use these examples to improve a test plan, not to promise a merge rate or skip repository-specific review.
