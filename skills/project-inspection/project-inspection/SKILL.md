---
name: project-inspection
description: Inspect the current repository and, when user-facing screens are involved, its frontend architecture and UX constraints before any planning or implementation.
---

# Project Inspection

## Goal

Produce a factual, scoped inspection handoff grounded in the current source of truth. Activate the frontend inspection section only when the request affects screens, navigation, forms, responsive behavior, accessibility, JavaScript interactions, or visual design.

## Trigger

Use when:

- a new repository, ZIP, checkpoint, or source set is provided;
- the user requests a feature, repair, redesign, or implementation plan;
- terminal output suggests the local source changed;
- the current checkpoint is uncertain;
- a frontend or UI/UX task must be understood before design.

## Required inputs

- current user request;
- latest explicitly identified repository, ZIP, branch, or checkpoint;
- repository `AGENTS.md` when present;
- stable project specifications when relevant;
- latest terminal, browser, or screenshot evidence.

## Procedure

### 1. Establish the source of truth

Record:

- exact source name and location;
- branch, commit, migration head, or checkpoint when available;
- why it is treated as current;
- older sources that are intentionally ignored.

Do not assume that an older upload still matches the local project. Stop when conflicting sources cannot be resolved by inspection.

### 2. Inspect the minimum relevant structure

Begin with:

- repository root and `AGENTS.md`;
- dependency and configuration files;
- application entry point;
- module or blueprint registration;
- canonical models and services;
- migrations;
- permissions and policies;
- tests and fixtures;
- relevant templates, static assets, and frontend entry points.

Inspect only the files needed for the requested workflow.

### 3. Trace the real workflow

Locate and connect:

- entry route or page;
- service layer;
- canonical model;
- status transitions;
- permission checks;
- audit and notification hooks;
- forms and validation;
- templates or components;
- tests;
- migration impact.

A menu label or filename does not prove that a workflow exists.

### 4. Frontend inspection mode

Activate this section for user-facing tasks.

Verify:

- frontend stack and build process;
- CSS architecture and design tokens;
- JavaScript entry points and interaction patterns;
- page shell, navigation, cards, tables, forms, drawers, modals, badges, alerts, and empty states;
- route and permission controlling each affected screen;
- data passed into the screen;
- current user journey;
- loading, empty, validation, system-error, disabled, and permission-denied states;
- responsive strategy, localization, RTL, light/dark themes, and accessibility patterns;
- related frontend or browser tests.

Identify confirmed issues such as missing Back or Cancel actions, misleading clickable cards, inconsistent priorities, inaccessible labels, missing focus, poor contrast, mobile overflow, duplicated CSS, or unauthorized actions shown in the UI.

Do not call browser behavior verified from source inspection alone.

### 5. Record evidence levels

Classify every finding as:

- **Verified in source**
- **Verified by terminal/browser/screenshot**
- **Inferred**
- **Not verified**

Inference must not become a planning fact.

### 6. Identify constraints and risks

Record:

- canonical models and services that must be reused;
- immutable or signed records;
- role and permission boundaries;
- migration chain and database compatibility;
- test-fixture behavior;
- files that must not be modified;
- frontend/backend dependencies;
- unresolved questions and stop conditions.



## Simplicity, dependency, and project-memory inspection

- Identify the smallest verified workflow affected by the request and reject unrelated expansion.
- Inspect dependency pins and runtime versions from repository files before considering upgrades.
- Search official release and security information only when the requested work materially depends on a dependency decision.
- Do not recommend the newest version by default; record compatibility, support status, breaking-change risk, and whether an upgrade is actually required.
- Inspect `PROJECT_MAP.md` when present, but verify every material claim against source, migrations, tests, Git state, or runtime evidence.
- Record orphaned routes, templates, services, imports, migrations, or pending integrations only when directly relevant to the requested scope.

## Prohibited behavior

- no implementation checklist before inspection is complete;
- no invented routes, APIs, permissions, models, files, or migrations;
- no stale source assumptions;
- no runtime or browser claims without evidence;
- no redesign recommendations detached from the real workflow.

## Required output

Use `resources/INSPECTION_REPORT.md`.

For frontend tasks, also complete the frontend-specific sections in the same report.

## Quality gate

Inspection is complete only when the next planner can answer without guessing:

- what exists now;
- what must be reused;
- what must change;
- which files and dependencies are involved;
- what is verified, inferred, or unknown;
- whether a frontend design stage is required.

## Guard-aware inspection handoff

When the task may create or modify production code, tests, or technical documentation, the inspection handoff must identify the exact guard surfaces:

- production-code files that will require `clean-code-guard` review;
- test files that will require `test-guard` review;
- documentation, README, changelog, examples, docstrings, route/API references, or configuration samples that will require `docs-guard` review;
- existing project-specific lint, test, documentation, and verification commands;
- pre-existing guard violations in affected files, separated from violations introduced by the requested change.

The inspection stage does not rewrite affected files. It provides verified evidence so later guard passes can distinguish current debt from newly introduced problems.
