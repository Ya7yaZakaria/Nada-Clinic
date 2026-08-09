---
name: verification-and-acceptance
description: Evidence-based verification for repairs, features, phases, releases, and final ZIPs. Selects the smallest sufficient verification profile, generates concise LLM-readable evidence, and expands diagnostics only when a check fails.
---

# Verification and Acceptance

## Purpose

Verify implemented software using actual evidence and decide whether a repair, feature, phase, release, or final package is genuinely acceptable.

This skill is the final stage of the workflow:

```text
Project Inspection
→ Implementation Planning
→ Guarded Implementation
→ Verification and Acceptance
```

Use it only after implementation has produced a handoff, or when the user provides terminal output, browser evidence, screenshots, a release ZIP, or a completed checkpoint for review.

For user-facing frontend verification, delegate browser/visual acceptance to `../visual-browser-verification/SKILL.md` and incorporate that specialist evidence into the final decision.

## Core rules

1. Generate only evidence that can change the acceptance decision or help diagnose a failure.
2. A successful run produces concise summaries, not large raw logs.
3. A failed run produces the first meaningful error plus targeted diagnostic evidence.
4. Never generate or retain browser video.
5. Do not create empty artifact folders.
6. Do not generate duplicate HTML, JSON, screenshots, or diagrams that communicate the same result.
7. Prefer machine-readable summaries that can be supplied to another LLM.
8. Never treat file existence, source inspection, a visible menu item, or a passing unit test as proof that a real workflow works.

Classify every result as one of:

- Verified
- Failed
- Expected but unverified
- Missing implementation
- Remaining work

## Inputs

Use the most current available evidence:

- current repository or explicitly identified latest ZIP;
- accepted implementation plan;
- implementation handoff;
- terminal output;
- focused and full test output;
- lint and application checks;
- migration state;
- Git diff and status;
- browser automation output;
- selected screenshots, traces, console logs, and network errors;
- acceptance criteria and project requirements.

When sources conflict, stop and identify the conflict instead of guessing.

---

# Verification profile selection

Select the smallest profile that can prove the requested scope. Escalate only when the affected layer or a failure requires it.

## Profile A — Small repair

Use for:

- import errors;
- unsupported arguments;
- isolated test repairs;
- deterministic one-file or few-file fixes;
- small non-UI logic corrections.

Default checks:

1. Ruff format and lint on affected Python files;
2. focused test for the repaired behavior;
3. relevant broader suite when shared behavior changed;
4. application/framework check when imports or startup changed;
5. `git diff --check` and Git status.

Default evidence:

```text
artifacts/verification/
├── summary.md
├── manifest.json
├── changed-files.txt
└── test-summary.json
```

Do not generate screenshots, traces, coverage, accessibility output, or schema evidence unless the repair affects those layers.

## Profile B — Feature verification

Use for:

- a new or materially changed workflow;
- a form, route, permission, service, or user-facing screen;
- a database-backed feature;
- a group of related files.

Add only checks relevant to the affected layer:

- UI change → browser workflow and selected screenshots;
- accessibility-sensitive UI → axe scan on affected pages and keyboard smoke test;
- business logic → focused and integration tests;
- permission change → allowed and denied behavior;
- database change → migration check and schema delta;
- package/configuration change → repository hygiene checks.

Default evidence adds only the applicable files:

```text
browser-summary.json
accessibility-summary.json
schema-delta.md
migration-summary.json
screenshots/
```

## Profile C — Phase acceptance

Use for a complete phase or major module.

Include:

- requirement-to-evidence coverage;
- clean temporary database where practical;
- migrations and initialization;
- focused and full suites;
- representative end-to-end workflows;
- permissions, denied actions, audit, and immutability where relevant;
- selected desktop and mobile screenshots;
- coverage summary when the phase adds substantial logic;
- accessibility summary for changed critical pages;
- package and secret/private-data checks when delivery files are involved.

## Profile D — Release verification

Use for a release candidate, final ZIP, deployment checkpoint, or final project package.

Include:

- clean installation or reproducible environment check;
- complete migration path;
- full automated suite;
- critical browser journeys;
- selected responsive screenshots;
- coverage summary;
- accessibility summary;
- secrets, private-data, database, upload, and accidental-large-file checks;
- package-content inspection;
- requirement matrix;
- architecture or ER baseline only when required by the release or when the database architecture changed materially.

---

# Relevance gate

Before running or generating each check, answer:

```text
Can this evidence change the acceptance decision,
prove an affected requirement,
or diagnose a failure?
```

If no, do not generate it.

Examples:

- Template-only change → no ER diagram.
- Import repair → no coverage HTML.
- Service logic change → no screenshots unless user-visible behavior changed.
- Database migration → schema delta, not a full ER diagram by default.
- Successful browser workflow → no trace.
- Failed browser workflow → screenshot plus trace and error summary.

---

# Verification sequence

Adapt commands to the repository stack. For Flask/Python projects, use this order when applicable.

## Formatting and lint

Run safe automatic fixes first, scoped to affected files when practical:

```powershell
python -m ruff format <affected-paths>
python -m ruff check <affected-paths> --fix
python -m ruff format --check <affected-paths>
python -m ruff check <affected-paths>
```

For phase or release acceptance, expand to the repository's canonical Python paths.

## Tests and framework checks

```powershell
python -m pytest <focused-test> -q
python -m pytest
python -m flask --app run.py check
python -m flask --app run.py db current
git diff --check
git status
```

Do not run every command blindly. Use only commands valid for the inspected repository.

When migration work is part of the accepted plan:

```powershell
python -m flask --app run.py db upgrade
python -m flask --app run.py init-system
```

Do not run destructive database actions automatically.

## Clean database acceptance

For a phase or release, verify from an empty temporary database where practical:

1. create an isolated temporary database;
2. run every migration from the base revision;
3. run required initialization or synthetic seed commands;
4. start the application;
5. execute representative workflows;
6. confirm no dependency on an old local database.

Never claim migration success without migration output.

---

# Failure repair workflow

When a command or browser test fails:

1. identify the first meaningful traceback, assertion, console error, failed request, or failed requirement;
2. identify the exact file, function, route, selector, migration, or line;
3. classify the defect:
   - application logic;
   - migration;
   - permission design;
   - test setup;
   - invalid assumption;
   - template;
   - import;
   - database constraint;
   - environment mismatch;
   - browser-only issue;
4. inspect the current source;
5. repair the real cause;
6. rerun the focused check;
7. rerun the relevant broader suite;
8. rerun lint, application, migration, or browser checks affected by the repair;
9. write `failures.json` only when a failure remains or when its diagnostic history is needed.

Do not:

- hide failures;
- delete valid tests;
- weaken correct assertions;
- replace workflow verification with static text checks;
- report success from partial output;
- preserve massive raw logs when a concise failure record is sufficient.

## Failure evidence

On failure, retain only the evidence required to diagnose it:

```text
artifacts/verification/
├── failures.json
├── raw-failed-command.txt
├── screenshots/<failed-step>.png        # browser/UI failures only
└── traces/<failed-workflow>.zip          # browser failure or flaky retry only
```

`failures.json` should include:

- failed check;
- first meaningful error;
- exact file and line when available;
- defect classification;
- linked screenshot or trace when applicable;
- required next action.

---

# Automated browser verification

When user-facing behavior, layout, responsive behavior, theme, RTL, modal/drawer behavior, or browser-only interaction is in scope, **invoke the specialist skill**:

```text
../visual-browser-verification/SKILL.md
```

Do not duplicate a separate browser-verification policy here. The specialist skill owns:

- Playwright or repository browser-framework selection;
- source/selector/route inspection before automation;
- synthetic/disposable data safety;
- real browser workflow execution;
- HTMX/AJAX verification;
- responsive viewport selection;
- screenshots and visual review;
- console, page-error, and critical network failure capture;
- keyboard/accessibility smoke checks when relevant;
- optional visual-regression comparison;
- failure screenshots and Playwright traces;
- visual evidence packaging and statuses.

The specialist must return one of:

```text
VISUALLY_VERIFIED
FUNCTIONALLY_VERIFIED_VISUAL_PENDING
VISUAL_FAILED
BLOCKED_BY_MISSING_BROWSER_EVIDENCE
BLOCKED_BY_ENVIRONMENT
BLOCKED_BY_SOURCE_CONFLICT
```

## Parent acceptance responsibilities

After the specialist returns, this skill must:

1. inspect the specialist evidence paths and summary;
2. confirm screenshots correspond to the claimed route, role, viewport, and state;
3. confirm browser console/page/network findings are reconciled;
4. confirm any required responsive/theme/RTL/role variants were actually tested;
5. combine browser evidence with tests, migrations, lint, runtime checks, requirements, Git/diff review, and guard results;
6. refuse final visual acceptance if the specialist result is not `VISUALLY_VERIFIED`.

If the specialist skill is missing or cannot execute, report:

```text
BLOCKED_BY_MISSING_BROWSER_EVIDENCE
```

or the more specific specialist blocker. Do not silently fall back to source inspection and call the UI verified.

## Browser evidence in the parent evidence package

Reference, do not duplicate, the specialist artifacts:

```text
artifacts/verification/visual-browser/
```

The parent manifest should link to:

- visual status;
- browser-summary.json;
- screenshots;
- console/page/network summaries when present;
- accessibility summary when selected;
- trace only on failure/retry;
- remaining visual risks.

Never retain browser video.

# Accessibility verification

Accessibility checks should be scoped to changed or critical pages, not the entire application after every repair.

When relevant, use axe-core or the repository's existing accessibility tool to detect:

- controls without labels;
- buttons or links without accessible names;
- serious contrast violations;
- invalid ARIA use;
- broken heading order;
- duplicate IDs;
- focusable elements that cannot be used by keyboard.

Also perform a targeted keyboard smoke test where interaction matters:

- logical Tab order;
- visible focus;
- Enter and Space activation;
- Escape behavior for dialogs or drawers;
- focus containment and return;
- completion of the critical form without a mouse when practical.

Generate `accessibility-summary.json` only when accessibility was relevant to the scope or when violations were found.

Use concise counts and the highest-impact findings. Do not create a large HTML report unless explicitly required for a phase or release.

---

# Coverage policy

Coverage is supporting evidence, not proof of correctness.

Generate a coverage summary when:

- substantial business logic was added or changed;
- a feature, phase, or release is being accepted;
- the user explicitly requests coverage;
- a regression suggests untested paths.

Do not generate full HTML coverage for an isolated repair unless it is needed to diagnose missing tests.

Preferred LLM-readable output:

```text
coverage-summary.json
```

Include:

- total line coverage;
- branch coverage when configured;
- affected files and their coverage;
- uncovered lines relevant to the change;
- regression from a known checkpoint when available.

Generate HTML only for phase/release acceptance when a human needs line-by-line browsing.

---

# Database and migration evidence

## Normal database changes

Prefer a concise `schema-delta.md` over regenerating a full ER diagram.

It should state:

- added, removed, or changed tables/columns;
- relationship changes;
- migration revision;
- upgrade result;
- compatibility or data-migration risk;
- unresolved downgrade status if not tested.

## Full ER or architecture diagram

Generate or update a full ER diagram only when:

- creating the first architecture baseline;
- accepting a major phase;
- preparing a final release;
- performing a material database redesign;
- the user explicitly requests it.

A GUI application such as DBeaver may be used for human inspection, but the automated skill should prefer reproducible schema exports such as Mermaid, Graphviz, SchemaSpy, or SQLAlchemy metadata when available.

## Integrity checks

Run only when relevant:

- models versus migration schema drift;
- orphaned foreign keys;
- duplicate canonical identities;
- invalid states;
- records missing required patient or encounter links;
- signed/finalized record immutability;
- audit gaps.

---

# Repository hygiene and sensitive-data checks

## Always for modified text/code files

- Ruff format and lint where applicable;
- trailing whitespace and malformed patch checks via `git diff --check`;
- unresolved merge-conflict markers;
- changed-file review.

## Phase, release, packaging, or configuration changes

Add checks for:

- invalid YAML, TOML, or JSON;
- accidental large files;
- `.env` files;
- private keys, tokens, and likely secrets;
- committed local databases;
- patient uploads or private documents;
- real clinical identifiers or data;
- generated artifacts accidentally included in the delivery ZIP.

Use `pre-commit` when the inspected repository already defines it. Do not silently introduce new hooks during verification.

---

# LLM-readable evidence package

The default artifact root is:

```text
artifacts/verification/
```

The minimal successful evidence package is:

```text
artifacts/verification/
├── summary.md
├── manifest.json
├── changed-files.txt
└── test-summary.json
```

Add files only when relevant:

```text
├── browser-summary.json
├── accessibility-summary.json
├── coverage-summary.json
├── schema-delta.md
├── migration-summary.json
├── requirements-evidence.json
├── package-summary.json
├── failures.json
├── raw-failed-command.txt
├── screenshots/
└── traces/
```

Delete or do not create empty folders.

## `summary.md`

This is the primary handoff for a human or another LLM. Keep it concise and include:

- scope;
- source/checkpoint;
- changed files;
- checks and outcomes;
- relevant evidence paths;
- first meaningful failure when present;
- remaining risks;
- final classification.

## `manifest.json`

Use `manifest.json` as the machine-readable index. It should include:

- selected verification profile;
- scope;
- final status;
- changed files;
- each check as `passed`, `failed`, `not_required`, or `not_run`;
- evidence paths;
- failures;
- remaining risks.

Every generated artifact must be referenced by `manifest.json`.

## Raw logs

Do not retain full raw logs for successful commands by default.

Retain raw output only when:

- a command failed;
- output contains evidence not captured by the structured summary;
- the user explicitly requests raw logs;
- a release policy requires archival logs.

---

# Evidence completeness review

Before reporting completion, verify that:

- every claimed evidence path exists;
- every artifact is listed in `manifest.json`;
- screenshots correspond to the claimed viewport and workflow;
- a trace exists only for failure or retry;
- no video exists;
- no empty evidence directories remain;
- successful commands are summarized without unnecessary raw dumps;
- failed checks include the first meaningful error and exact next action.

If evidence generation itself fails, classify it as `Failed evidence generation`, not as verified behavior.

---



# Loop closure and bounded retry

Verification closes the implementation loop; it does not create an endless repair cycle.

For a failing required check:

1. record the first meaningful failure;
2. permit at most two deterministic repair attempts for that same focused failure;
3. rerun the focused check after each repair;
4. rerun affected broader checks only after focused success;
5. stop when the failure repeats, requirements conflict, evidence is missing, source differs from the accepted checkpoint, or the fix requires destructive action, secrets, external approval, or an architectural decision.

Classify the outcome as one of:

- `VERIFIED`;
- `FAILED`;
- `EXPECTED_BUT_UNVERIFIED`;
- `MISSING_IMPLEMENTATION`;
- `BLOCKED_BY_CONFLICT`;
- `BLOCKED_BY_MISSING_EVIDENCE`.

Never convert a blocked or unverified item into acceptance merely to empty a pending list.

# Project-map reconciliation

When `PROJECT_MAP.md` exists:

- compare its source checkpoint, architecture, workflows, migrations, and pending items with actual repository evidence;
- correct stale derived documentation only when within accepted scope;
- report unsupported completion claims as documentation drift;
- do not use an empty `[ORPHANS & PENDING]` section as proof of completion.

# Reporting

Use:

```text
resources/VERIFICATION_REPORT.md
```

for Profile A or Profile B.

Use:

```text
resources/ACCEPTANCE_REPORT.md
```

for Profile C or Profile D.

Reports must clearly separate:

- Verified
- Failed
- Expected but unverified
- Missing implementation
- Remaining work

Never claim visual verification without reviewed browser evidence or screenshots.
Never claim migration success without migration output.
Never claim acceptance when required evidence is missing.
Never commit, push, reset, delete source files, or perform destructive migrations unless the user explicitly asks.

## Mandatory independent guard verification

Verification and Acceptance must independently confirm that the implementation-stage guard gate was not merely self-reported.

Read and apply, as relevant:

```text
../guarded-implementation/guards/clean-code-guard/SKILL.md
../guarded-implementation/guards/test-guard/SKILL.md
../guarded-implementation/guards/docs-guard/SKILL.md
```

### Order of review

1. Inspect the actual diff and changed-file inventory.
2. If tests changed, review the test diff with `test-guard` **before** accepting any passing test output.
3. Review production-code changes with `clean-code-guard`.
4. Review changed technical documentation with `docs-guard`.
5. Rerun focused and broader verification independently.
6. Reconcile guard findings, test evidence, runtime/browser evidence, migrations, requirement status, and documentation claims.

### Acceptance blocking rules

Acceptance is blocked when:

- a must-fix clean-code finding remains;
- test changes weaken or bypass valid behavior;
- documentation states behavior not supported by source/runtime evidence;
- the implementation handoff claims a guard ran but provides no inspectable scope or evidence;
- generated installer checks were not run and their outcome is being represented as verified;
- pre-existing issues are confused with regressions introduced by the current change.
- a user-facing change requires visual verification but `visual-browser-verification` did not return `VISUALLY_VERIFIED`.

Report guard outcomes separately as:

- `GUARD_VERIFIED`;
- `GUARD_FAILED`;
- `GUARD_NOT_APPLICABLE`;
- `GUARD_EXPECTED_BUT_UNVERIFIED`;
- `BLOCKED_BY_MISSING_EVIDENCE`.
