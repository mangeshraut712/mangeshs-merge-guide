# Installation and troubleshooting

Start with the [README installation steps](../README.md). The installed skill is named `oss-contribution-insights`; the npm installer executable is named `merge-guide`.

| Symptom | Check | Safe next step |
| --- | --- | --- |
| Copy says target exists | Existing directory, file or symlink at the destination | Inspect and back up your existing install; do not overwrite or delete it blindly |
| Source SKILL.md missing | Shell working directory | Run the copy block from the repository root containing `skills/` |
| Skill absent in runtime | Supported user-skill location and exact frontmatter name | Use your runtime's documented discovery/refresh procedure; confirm file access |
| Display title absent | Runtime version and optional metadata support | The legacy invocation is `oss-contribution-insights`; see tested version in results |
| Runtime or sandbox fails before task | Actual error and environment | Use supported setup/support flow; do not copy credentials or bypass controls |
| Helper cannot run | Python 3.10+; for live collection an already authenticated `gh` | Offline ledger/tests need no GitHub login; live access is separate |
| Partial collector result | Recorded errors, sampled head and coverage | Keep the incomplete interval pending; do not treat it as no feedback |
| Output already exists | Non-destructive helper behavior | Choose a new authorized private output path |
| Plugin not listed after install | `/plugin` shows marketplaces and installed plugins; Claude Code version | On versions before 2.1.275, add the marketplace first, then install `mangeshs-merge-guide@mangeshraut712`. Run `claude plugin validate --strict .` on a clone to rule out a packaging problem |
| Plugin refused by claude.ai or Cowork | Those surfaces reject plugins with a top-level `bin/` | Use the plugin from this repository, where the npm CLI lives in `cli/` |
| `open_pr_triage.py`: GraphQL not available or 401 | `gh auth status`; some sandboxes block GraphQL | Run it where `gh` has normal API access, or use `collect_pr_evidence.py` per PR, which uses REST |
| `merge_stats.py`: more than 1000 results | GitHub search returns at most 1000 items | Narrow with `--since YYYY-MM-DD` and combine the runs yourself |
| `noise_check.py` exits 1 | Exit 1 means something was flagged; 2 means the file isn't a snapshot | Read the advice it prints; give it files saved by `collect_pr_evidence.py` |

Installation means files were copied. Discovery means the runtime found an enabled skill. Invocation means a task actually ran using it. None proves a contribution was accepted.

For an upgrade, inspect the new source and diff first. Keep user-local modifications and private ledgers separate; the README block intentionally refuses existing targets rather than implementing an updater. To remove an installation, identify the exact installed folder and back up local changes, then use your runtime's supported removal procedure. This repository has no background daemon to uninstall.

Installer checks and agent discovery are different: see the dated platform results rather than assuming that copying files proves an agent can execute the skill. See [results and limitations](results.md).
