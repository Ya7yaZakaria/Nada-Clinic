---
name: implementation-planning
description: Convert a verified inspection into an accepted technical plan, with an integrated UI/UX design section for user-facing work.
---

# Implementation Planning

## Goal

Create a precise, implementable checklist grounded entirely in the verified inspection and the user’s request. For user-facing work, include an implementable UI/UX design plan that uses only real routes, permissions, data, and backend capabilities.

## Trigger

Use only after a completed inspection handoff exists.

## Required inputs

- user request;
- verified inspection report;
- accepted project specifications;
- explicit scope and constraints;
- stable branding or visual references when relevant.

## Procedure

### 1. Restate the outcome

Describe the visible and technical result without expanding scope.

### 2. Confirm the verified current state

Use only findings marked verified in the inspection. Keep inferred and unknown items separate.

### 3. Define scope

Separate:

- required;
- optional;
- explicitly out of scope;
- unresolved decisions that block safe implementation.

### 4. Build implementation checklist items

Every item must include:

- requested behavior;
- affected files;
- files to create;
- files not to modify when important;
- database and migration impact;
- permission and security impact;
- audit or notification impact;
- risks and dependencies;
- focused verification;
- full acceptance evidence.

Do not invent filenames, migration IDs, routes, permissions, or APIs.

### 5. Preserve architecture

Reuse:

- canonical domain models;
- existing services and policies;
- current permission and audit systems;
- established module and frontend patterns;
- current migration chain;
- existing design tokens and component system.

### 6. UI/UX design mode

Activate for user-facing work.

For every affected screen define:

- primary user and task;
- route/page and permission dependency;
- information needed to complete the task;
- primary and secondary actions;
- page hierarchy and progressive disclosure;
- navigation, breadcrumbs, Back, Cancel, and destructive-action confirmation;
- default, loading, empty, success, validation-error, system-error, disabled, permission-denied, and critical states;
- desktop, tablet, and mobile behavior;
- keyboard operation, visible focus, labels, contrast, semantic headings, and appropriate ARIA;
- visual direction using existing tokens;
- backend or data dependencies the implementer cannot invent.

The UI/UX section must not create fictional routes, APIs, permissions, records, or workflows.

### 7. Sequence the work

A common order is:

1. models and constraints;
2. migration;
3. services and policies;
4. routes and APIs;
5. templates/components and interactions;
6. permissions and seeds;
7. focused tests;
8. full tests and documentation;
9. browser and visual verification.

Adapt to the verified architecture.

### 8. Define acceptance criteria

Criteria must describe real behavior and evidence, not file existence.

Bad: `Laboratory page exists.`

Good: `A clinician can place a laboratory order, the laboratory can advance it through validated states, and the result remains linked to the same patient, encounter, order, audit history, and permission checks.`



### 9. Apply simplicity and loop design

For every checklist item:

- choose the smallest implementation that satisfies the accepted behavior;
- prohibit speculative flexibility, premature `Shared/Core` abstractions, unrelated refactoring, and micro-file fragmentation;
- introduce shared abstraction only when verified repeated logic already exists and the abstraction has one clear responsibility;
- define the focused success condition, affected regression checks, maximum safe repair attempts, and explicit stop/escalation conditions;
- identify whether verification is unit, integration, migration, browser, accessibility, visual, or manual runtime evidence;
- mark `PROJECT_MAP.md` updates only for material architecture, workflow, checkpoint, or blocker changes.

### 10. Define the bounded implementation loop

Each planned implementation unit must follow:

```text
implement smallest accepted change
→ focused verification
→ first meaningful failure analysis
→ safe deterministic repair, maximum 2 attempts
→ affected regression verification
→ evidence update
→ next item or controlled stop
```

The plan must not use unbounded instructions such as “continue until everything is complete” without stop conditions.

## Prohibited behavior

- no plan before verified inspection;
- no unsupported project facts;
- no silent scope expansion;
- no implementation before acceptance when planning was requested first;
- no frontend design detached from backend reality;
- no inaccessible interaction used only for visual effect;
- no claim that an untested workflow is complete.

## Required output

Use `resources/IMPLEMENTATION_PLAN.md`.

For frontend work, complete the integrated UI/UX design sections in that plan.

## Quality gate

The plan is ready only when it accurately reflects:

- requested behavior;
- exact known files and dependencies;
- migration, permission, and data risks;
- implementation order;
- focused, full, and visual verification;
- unresolved blockers;
- explicit acceptance status.

## Mandatory guard plan

Every implementation checklist must include a **Guard Review Plan** before the implementation-delivery item.

### Guard selection

- Always apply `clean-code-guard` to generated or modified production code.
- Apply `test-guard` whenever tests are created, modified, removed, skipped, parametrized, mocked, or relied upon as acceptance evidence.
- Apply `docs-guard` whenever technical documentation, README content, changelog entries, examples, docstrings, CLI commands, endpoints, configuration keys, environment variables, or documented behavior are created or changed.

### Checklist requirements

For each selected guard, define:

- exact files in scope;
- authoritative source used to verify claims;
- must-fix findings that block delivery;
- checks that will run inside the guarded installer after changes are applied;
- evidence required before the implementation script may be delivered;
- treatment of pre-existing violations: report separately and do not expand scope unless they block the accepted change.

The plan must distinguish two kinds of validation:

1. **Pre-delivery static guard review** — review the proposed code, tests, docs, and installer payload before showing the script to the user.
2. **Post-application runtime verification** — commands embedded in or handed off with the installer, such as Ruff, pytest, migration checks, documentation link/sample checks, browser checks, and project-specific acceptance scripts.

Do not claim runtime verification before the installer has been executed in the actual repository.
