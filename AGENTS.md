# AGENTS.md — ProCoder Guarded v4

## Required sequence

```text
Project Inspection
→ Implementation Planning
→ Guarded Implementation
→ Verification and Acceptance
```

Use the repository copy of `AGENTS.md` when available. Treat the latest explicitly identified repository, ZIP, Git checkpoint, or uploaded source as current.

## Skills

1. `skills/project-inspection/project-inspection/SKILL.md`
2. `skills/implementation-planning/implementation-planning/SKILL.md`
3. `skills/guarded-implementation/guarded-implementation/SKILL.md`
4. `skills/verification-and-acceptance/verification-and-acceptance/SKILL.md`
5. `skills/visual-browser-verification/SKILL.md` — specialist UI/browser acceptance skill, invoked by Verification and Acceptance when user-facing behavior or layout changes.

Embedded guard passes used by implementation and verification:

- `skills/clean-code-guard/clean-code-guard/SKILL.md`
- `skills/test-guard/test-guard/SKILL.md`
- `skills/docs-guard/docs-guard/SKILL.md`

## Global rules

- Inspect before planning.
- Plan before implementation.
- Verify before completion.
- When a user-facing screen, frontend interaction, responsive layout, theme, RTL behavior, modal/drawer, or browser-only workflow changes, `verification-and-acceptance` must invoke `visual-browser-verification`.
- Do not mark UI work `VISUALLY_VERIFIED` without reviewed browser evidence or screenshots produced by that specialist workflow.
- Do not invent routes, APIs, permissions, models, files, migrations, packages, commands, or browser behavior.
- Do not implement until the checklist accurately reflects the request, affected files, risks, guard scope, and verification.
- Do not commit, push, reset, delete, overwrite data, or run destructive migrations unless explicitly requested.
- Never weaken a valid test merely to make it pass.
- State the exact folder where commands must run.
- Separate verified, failed, expected but unverified, missing implementation, blockers, and remaining work.


## Test rules

Keep project tests consistent with the current pytest structure:

- Put shared pytest fixtures in `tests/conftest.py`.
- Put reusable test-data builders/helpers in `tests/factories.py`.
- Keep tests organized in the existing domain folders; do not recreate duplicate flat copies under `tests/`.
- Avoid duplicate scenarios and duplicate setup. Parametrize true input/output variants when it improves clarity.
- Preserve regression, security/RBAC, migration, cross-record isolation, and domain-invariant tests.
- Delete a test only when it is proven duplicate, obsolete, or covered by a stronger current test.
- Mark genuinely expensive tests `slow` and migration-specific tests `migration`; markers organize runs but do not remove required checkpoint coverage.
- Ordinary test users may use valid low-cost password hashes; tests of password creation/hashing must use the real production path.
- Do not add shared database-state shortcuts, global transaction tricks, or parallel execution until isolation is proven.
- During development run focused tests first. Before a checkpoint run the applicable regression/full suite and review `pytest --collect-only` after test-tree reorganization.

## Mandatory implementation guard gate

Before any implementation script or replacement package is delivered:

1. Run `clean-code-guard` on all proposed production-code and installer changes.
2. Run `test-guard` when tests are changed or used as acceptance evidence.
3. Run `docs-guard` when technical documentation or documented behavior changes.
4. Correct must-fix findings and rerun the selected guards, with at most two rounds for the same finding.
5. Do not deliver while a must-fix guard finding remains.
6. Clearly distinguish static pre-delivery review from runtime checks that can only be verified after the user executes the installer in the repository.

## Unified bounded loop

```text
Observe current source and evidence
→ define focused success
→ apply smallest safe change
→ run selected static guards
→ correct must-fix guard findings
→ deliver guarded installer
→ run focused runtime checks after application
→ analyze first meaningful failure
→ make deterministic safe repair when possible
→ rerun focused and affected regression checks
→ record evidence or stop with a precise blocker
```

Maximum automatic repair attempts for the same focused runtime failure: 2.


## Frontend verification routing

For any user-facing frontend change:

```text
Verification and Acceptance
→ Visual Browser Verification
→ real browser workflow
→ responsive screenshots
→ console/page/network review
→ visual acceptance evidence
```

`visual-browser-verification` is a specialist verifier, not a replacement for the parent acceptance skill.

The parent `verification-and-acceptance` skill remains responsible for combining visual/browser evidence with tests, migrations, lint, runtime checks, requirements, Git/diff review, and final checkpoint status.

For healthcare or sensitive systems, browser verification must prefer synthetic/disposable data and must not intentionally capture PHI/PII or secrets in screenshots.
