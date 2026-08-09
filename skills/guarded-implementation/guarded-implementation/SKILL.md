---
name: guarded-implementation
description: Apply an accepted backend, frontend, or full-stack plan safely through VS Code using guarded PowerShell or a guarded Python installer, then hand off exact verification commands.
---

# Guarded Implementation

## Goal

Apply an accepted implementation plan through the safest practical VS Code workflow while preserving current architecture, permissions, data, and frontend patterns.

## Trigger

Use only after:

- inspection is complete;
- the implementation checklist is accepted;
- UI/UX design is accepted for user-facing work;
- required source files are available and current.

## Required inputs

- accepted implementation plan;
- verified inspection report;
- current source;
- user platform and shell;
- explicit constraints such as no commit, no migration, or no destructive action.

## 1. Confirm boundaries

Before writing changes, list:

- files to create;
- files to modify;
- files not to modify;
- backend, migration, and permission dependencies;
- responsive and visual requirements when applicable;
- verification requirements.

Stop when the current source no longer matches the accepted plan.

## 2. Select delivery method

### Direct PowerShell patch

Use when:

- few files change;
- edits are deterministic;
- the command remains readable;
- source guards can verify the expected state.

The command must:

- state the exact repository folder where it must run;
- verify repository identity and required files;
- verify expected source fragments;
- stop safely on mismatch;
- write UTF-8 files;
- print changed files;
- run safe formatting/lint fixes and focused verification when practical.

### Downloadable guarded Python installer

Use when:

- many files change;
- files are created across modules;
- models, migrations, routes, templates, scripts, and tests change together;
- an inline command would be fragile.

The installer must:

- verify repository identity;
- verify required paths and expected source fragments;
- verify migration parent when applicable;
- use guarded replacements;
- avoid unrelated changes;
- be idempotent where practical;
- print every created or modified file;
- never commit, push, reset, delete unrelated files, overwrite data, or apply destructive migrations;
- run safe auto-formatting/lint fixes and focused verification where practical;
- print a clear final failure report containing the failed check, first meaningful traceback, and required next action when safe auto-repair is not possible.

Do not create a separate TXT report unless explicitly requested; summarize terminal evidence in chat.

## 3. Backend implementation rules

- reuse canonical models and services;
- preserve immutable and signed records;
- enforce permissions server-side;
- preserve audit and notification behavior;
- add migrations only when the accepted plan requires them;
- never run destructive migrations automatically;
- never weaken a valid test to make it pass.

## 4. Frontend implementation mode

Activate for user-facing work.

- reuse the current page shell, macros/components, tokens, JavaScript utilities, icons, and accessibility patterns;
- do not introduce a second frontend framework or duplicate component system without approval;
- align visible controls with server-side authorization;
- implement normal, loading, empty, error, disabled, permission-aware, and responsive states;
- provide Back or Cancel behavior where appropriate;
- preserve semantic labels, focus, contrast, and keyboard access;
- do not claim visual verification from source or unit tests alone.

## 5. Verification commands

Run focused checks before the full suite. Adapt commands to the actual stack.

For a Flask/Python project, a typical sequence is:

```powershell
python -m ruff check app tests --fix
python -m pytest <focused-test> -q
python -m pytest
python -m ruff check app tests
python -m flask --app run.py check
python -m flask --app run.py db current
git diff --check
git status
```

When an accepted migration is involved:

```powershell
python -m flask --app run.py db upgrade
python -m flask --app run.py init-system
```

Do not execute migration commands blindly when the migration head or target database is unresolved.

Frontend work must also include the relevant build/lint tests, route/component tests, permission visibility tests, and a manual browser checklist.

## 6. Failure handling

When output fails:

1. read the first meaningful traceback;
2. identify the exact failing function, route, selector, or line;
3. inspect the current source;
4. classify the cause;
5. repair the actual cause;
6. rerun the focused check;
7. rerun the full suite and relevant checks.

Do not hide failures, remove valid tests, weaken assertions, or substitute static text checks for real workflow verification.



## 6A. Surgical-change policy

- Apply only accepted changes and required supporting edits.
- Match the current repository style even when another style is preferred.
- Do not reformat, rename, reorganize, or refactor adjacent working code unless required by the accepted plan.
- Remove only imports, functions, files, or generated artifacts made obsolete by the current change.
- Do not create `Shared/Core` abstractions for one-off logic.
- Do not update dependencies unless the accepted plan contains a verified compatibility reason.

## 6B. Bounded repair loop

For each focused check:

1. run the check once;
2. capture the first meaningful traceback, assertion, console error, failed request, or migration error;
3. classify the root cause;
4. apply the smallest deterministic repair only when supported by current source and accepted behavior;
5. rerun the same focused check;
6. allow at most two automatic repair attempts for the same failure;
7. after success, run affected regression, lint, migration, and browser checks;
8. stop and report the exact blocker when the same failure repeats, a new unrelated failure appears, behavior is ambiguous, or destructive/external action is required.

Do not repeatedly apply the same patch or continue an unbounded loop.

## 6C. Project-memory synchronization

When `PROJECT_MAP.md` exists, update it only after a material verified change to architecture, workflow, migration, checkpoint status, or a blocker. Treat it as derived documentation. Never mark work complete there without corresponding test or runtime evidence.

## Completion standard

Implementation is not complete merely because files were written.

Report separately:

- source changes applied;
- focused checks passed or failed;
- full checks passed or failed;
- migration status;
- browser behavior verified or unverified;
- responsive/visual behavior verified or unverified;
- remaining work.

## Required output

Use `resources/IMPLEMENTATION_HANDOFF.md`.

## 7. Mandatory pre-delivery guard gate

Before showing or attaching any implementation script, PowerShell patch, guarded Python installer, replacement-file package, or generated source files, run the following guard passes against the complete proposed payload.

The embedded guard instructions are located at:

```text
skills/guarded-implementation/guards/clean-code-guard/SKILL.md
skills/guarded-implementation/guards/test-guard/SKILL.md
skills/guarded-implementation/guards/docs-guard/SKILL.md
```

Project instructions and accepted requirements override generic guard preferences when they conflict, but they never override correctness, test integrity, or truthful documentation.

### 7.1 Clean-code guard — always required

Review every generated or modified production-code file and the installer logic itself.

Block delivery for must-fix findings including:

- invented packages, APIs, routes, models, permissions, files, or configuration;
- hard-coded success paths or placeholder behavior;
- broad exception handling that hides real failures;
- speculative abstraction, unnecessary framework additions, or feature creep;
- duplicated logic that should reuse a verified existing service, where reuse is clearly supported;
- destructive or unrelated edits;
- dead code introduced by the proposed change;
- unsafe handling of secrets, private data, clinical data, permissions, migrations, or signed records;
- comments or formatting that obscure rather than clarify the change.

Use the guard as a focused second pass, not as permission for unrelated refactoring.

### 7.2 Test guard — required when tests are touched or used as evidence

Review all generated or modified tests before trusting their results.

Block delivery when the proposed tests:

- weaken, delete, skip, or bypass a valid regression test;
- assert implementation details instead of required behavior without justification;
- mock the unit under test or mock away the behavior being verified;
- use unrealistic state objects where real project models or fixtures are required;
- claim database or migration behavior without exercising the real test database/migration path;
- contain assertions too weak to prove the accepted behavior;
- duplicate cases that should be parametrized without a project-specific reason;
- hide failures through broad exception handling, excessive tolerances, or unconditional passes.

If tests are not modified, still inspect the selected existing focused tests to confirm they genuinely cover the change.

### 7.3 Docs guard — required when technical documentation changes

Verify every generated or modified technical claim against current source or generated artifacts:

- symbols, functions, classes, routes, endpoints, commands, flags, environment variables, configuration keys, permissions, migrations, and file paths must exist;
- examples must use real signatures and safe fictional data;
- documentation must describe actual implemented behavior, not planned behavior;
- completion, compatibility, performance, and production-readiness claims require repository evidence;
- all affected documentation surfaces must move together when a documented symbol or behavior changes;
- no TODO/coming-soon filler may be presented as completed documentation.

### 7.4 Guard-fix loop before delivery

Use a bounded pre-delivery loop:

```text
Generate proposed payload
→ run selected static guard passes
→ collect must-fix findings with file/section evidence
→ correct the proposed payload
→ rerun the same guards
→ deliver only when no must-fix guard finding remains
```

- Maximum guard-correction rounds: 2 for the same finding.
- Do not repeatedly apply the same correction.
- Stop and report a precise blocker when a finding cannot be corrected without changing accepted scope, guessing missing behavior, weakening a test, or requiring unavailable repository/runtime evidence.

### 7.5 Runtime checks embedded in the installer

Static guard review does not replace execution. The delivered installer must run the applicable project checks after applying changes, when safe and available:

- formatter and linter;
- focused tests;
- affected regression tests;
- full tests when practical;
- compile/build checks;
- migration/current-head and clean-migration checks when applicable;
- documentation sample/link/command checks when the project has them;
- browser and visual verification handoff for user-facing work.

The installer may automatically repair only deterministic safe issues allowed by this skill. It must not ask an LLM to rewrite arbitrary source at runtime.

### 7.6 Required guard summary in the implementation handoff

Before delivery, report:

- `clean-code-guard`: PASS / BLOCKED, files reviewed, findings corrected;
- `test-guard`: PASS / NOT_APPLICABLE / BLOCKED, tests reviewed and integrity result;
- `docs-guard`: PASS / NOT_APPLICABLE / BLOCKED, claims verified;
- runtime checks embedded but not yet executed;
- checks actually executed in the current environment, if any;
- remaining unverified behavior.

No implementation script may be labelled ready when a selected guard has an unresolved must-fix finding.
