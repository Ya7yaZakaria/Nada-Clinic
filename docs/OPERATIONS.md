# Operations and handoff

## Working folder

Run project commands from the repository root, for example:

```text
D:\Nada-Clinic
```

## Local startup

With the project virtual environment active:

```powershell
python run.py
```

For Flask CLI commands, set the application when the shell/environment has not already done so:

```powershell
$env:FLASK_APP = "app"
flask routes
flask db current
flask db heads
```

Do not run migrations against the real database merely as a verification shortcut. Migration testing should use disposable databases when the task requires clean migration evidence.

## Test workflow

See `docs/TESTING.md`. The full suite remains a checkpoint/release gate; focused and marker-filtered runs are used for a faster development loop.

## Documentation source order

- `AGENTS.md` — implementation workflow and guard rules.
- `MEMORY.md` — concise current state, constraints, known issues, next work.
- `README.md` — project overview and local entry points.
- `CHANGELOG.md` — historical product/engineering changes.
- `docs/ARCHITECTURE.md` — current structural map.
- `docs/TESTING.md` — canonical test architecture and commands.
- `docs/ROADMAP.md` — current future-work priorities.
- `docs/AGENT_LESSONS.md` — mistakes/prevention rules worth retaining.
- `docs/history/` — historical stage/sprint evidence; not current authority.

## Evidence labels

Implementation and verification reports must separate:

- Verified
- Expected but unverified
- Failed
- Remaining work

Do not convert planned or historical claims into current verified status without fresh evidence.
