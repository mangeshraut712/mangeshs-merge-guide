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

Installation means files were copied. Discovery means the runtime found an enabled skill. Invocation means a task actually ran using it. None proves a contribution was accepted.

For an upgrade, inspect the new source and diff first. Keep user-local modifications and private ledgers separate; the README block intentionally refuses existing targets rather than implementing an updater. To remove an installation, identify the exact installed folder and back up local changes, then use your runtime's supported removal procedure. This repository has no background daemon to uninstall.

Installer checks and agent discovery are different: see the dated platform results rather than assuming that copying files proves an agent can execute the skill. See [results and limitations](results.md).
