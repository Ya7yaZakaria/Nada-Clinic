---
name: visual-browser-verification
description: Specialist browser and visual acceptance verification for user-facing software. Uses the repository's existing browser framework (prefer Playwright when available), real application routes, synthetic data, responsive screenshots, console/network checks, keyboard/accessibility smoke tests, and optional visual-regression comparison. Produces concise evidence and never claims visual verification without browser or screenshot evidence.
---

# Visual Browser Verification

## Purpose

Verify user-facing behavior and visual quality in a real browser and return evidence that can support an acceptance decision.

This is a specialist verification skill. It is normally invoked by:

```text
Verification and Acceptance
→ Visual Browser Verification
```

It may also be used directly when the user asks for:

- browser verification;
- Playwright verification;
- automated screenshots;
- responsive UI checks;
- visual regression;
- console/network-error inspection;
- keyboard or accessibility smoke testing;
- proof that a frontend workflow works in a real browser.

This skill does not replace unit, integration, migration, or backend verification.

---

# Core acceptance rule

Never classify a user-facing screen as visually verified from:

- source inspection alone;
- template/CSS inspection alone;
- unit tests alone;
- a successful HTTP response alone;
- a route existing;
- a single manually described screenshot that has not been reviewed.

Visual acceptance requires real browser evidence.

Final visual status must be one of:

- `VISUALLY_VERIFIED`
- `FUNCTIONALLY_VERIFIED_VISUAL_PENDING`
- `VISUAL_FAILED`
- `BLOCKED_BY_MISSING_BROWSER_EVIDENCE`
- `BLOCKED_BY_ENVIRONMENT`
- `BLOCKED_BY_SOURCE_CONFLICT`

---

# Authority and source freshness

Before browser verification:

1. Read current repository `AGENTS.md`.
2. Re-read the affected frontend files from the freshest accepted project source.
3. Read the accepted implementation handoff/checklist.
4. Prefer the repository's current routes, forms, templates, selectors, tests, and fixtures over old documentation.
5. If Drive, Git, local execution evidence, or an uploaded checkpoint conflict materially, stop and identify the conflict.

Do not verify against a stale build while claiming the current source passed.

---

# Tool selection

Use the repository's existing browser framework when available.

Preferred order:

1. Existing Playwright setup.
2. Existing browser automation framework already used by the repository.
3. A guarded temporary Playwright runner when Playwright is already available in the environment.
4. Manual screenshot/browser evidence only when automation is unavailable.

Do not silently add a new production dependency only to run verification.

If Playwright is missing:

- check whether it is already available globally, in a test environment, or in project tooling;
- if installation would modify the repository or environment materially, report the missing tool and provide the exact optional install step;
- do not mark visual verification passed without executing equivalent browser evidence.

---

# Safety rules

## Data safety

Prefer:

- disposable database;
- temporary database copy;
- synthetic/demo users;
- synthetic patients and records;
- isolated test uploads.

Do not create, edit, close, cancel, reschedule, charge, prescribe, or otherwise mutate real clinical/business data merely for verification unless the user explicitly authorizes it.

For healthcare or sensitive systems:

- never intentionally capture real patient identifiers in screenshots;
- mask or avoid PHI/PII;
- do not save authentication secrets, cookies, tokens, or passwords in evidence files;
- do not retain storage state containing sensitive credentials.

## Destructive UI actions

Use preview-only or synthetic-data execution for actions such as:

- irreversible end-of-period or workflow-closing actions;
- delete/archive;
- irreversible workflow completion;
- payment capture;
- destructive settings changes;
- migration-triggering admin actions.

If a destructive workflow must be verified, use an isolated disposable environment unless explicitly approved otherwise.

---

# Inspection before automation

Do not invent selectors, routes, credentials, roles, labels, or expected state.

Inspect current source for:

- application start command;
- target route;
- authentication flow;
- required roles/permissions;
- existing test users or fixtures;
- stable IDs, names, labels, `data-testid`, or accessible roles;
- form field names;
- modal/drawer behavior;
- expected redirects;
- expected state transitions;
- responsive breakpoints;
- theme and RTL support;
- existing browser tests;
- existing screenshot or visual-regression baselines.

Prefer stable semantic selectors:

```text
get_by_role(...)
get_by_label(...)
get_by_text(...) when unique and stable
data-testid only when intentionally provided
```

Avoid brittle selectors based on incidental DOM depth or generated classes.

---

# Evidence-locked automation design — mandatory no-guess gate

Browser automation must be designed from verified current-source facts, not from remembered conventions, framework defaults, old screenshots, or likely labels.

**Do not generate or deliver a browser-verification script until this gate is complete.**

## No-guess rule

For every planned browser action or assertion, identify the exact current-source evidence that proves how it should work.

Do not guess any of the following:

- application startup command or health endpoint;
- login URL, field names, submit control, redirect, or authenticated landing page;
- user/role/permission required to see or activate a control;
- feature flags, tenant rules, state gates, dates, workflow status, or other conditions controlling visibility;
- fixture requirements or test-data shape;
- route/path, HTTP method, query parameters, form action, API endpoint, RPC action, or client-side navigation target;
- visible label, accessible name, `aria-label`, ID, name, test ID, CSS class, or other selector;
- modal/drawer shell, portal target, frame, shadow root, or mounting container;
- HTMX/Turbo/AJAX/fetch/XHR lifecycle and expected target replacement;
- expected response status/content/redirect;
- expected DOM state after the action;
- breakpoint, theme, direction, or role-specific rendering behavior.

If any required fact is unresolved, **inspect more source before writing the automation**. Do not fill the gap with a plausible assumption.

## Mandatory automation evidence map

Before implementation, build a compact evidence map for each workflow checkpoint.

For each action, resolve as applicable:

```text
Checkpoint/action
→ source file/component/template
→ visibility/state condition
→ required role/permission/feature flag
→ required fixture/data state
→ trigger/control in current DOM
→ route/endpoint/navigation target
→ HTTP method + required params
→ async/update mechanism
→ expected response/redirect
→ expected DOM state/content
→ safe cleanup/reset behavior
```

The map may be held in working notes; it does not need to become permanent project documentation unless requested. But the verifier must not be generated until all acceptance-critical rows are resolved.

## Read what controls the behavior, not only what renders it

When a control is conditional, inspect both the rendering layer and the controlling logic.

Examples of controlling sources include:

- route/controller/handler;
- authorization policy, permission matrix, middleware, guard, or role service;
- model/status enum or workflow state machine;
- feature-flag/configuration source;
- test fixture/factory/seed helper;
- client-side event handler or data-fetching hook;
- modal/drawer manager;
- generated route manifest or typed API client;
- CSS/media query when visibility changes by viewport.

Seeing the button text in a template is not enough if a permission or state condition decides whether it appears.

## Selector design must follow actual source

Selector preference is conditional on what the current project actually exposes.

Prefer, in order, the most stable selector that is **verified to exist and be unique in the current source/runtime**:

1. intentional test ID or stable product-specific identifier;
2. stable accessible role/name when the accessible name has been verified;
3. associated label/name/ID verified from the form/component;
4. stable `aria-label`, route attribute, action class, or data attribute intentionally tied to behavior;
5. unique visible text when verified stable;
6. scoped structural selector as a last resort.

Do not use `get_by_role(..., name=...)` merely because it is normally recommended. First verify that the runtime accessible name is actually what the script expects.

Do not use copied CSS classes merely because they look convenient. Confirm they are behaviorally stable or intentionally exposed.

## Deterministic fixture rule

If a workflow requires a specific role, permission, record status, date, feature flag, cart state, appointment state, account state, or other prerequisite, the verifier must make that prerequisite deterministic.

Preferred order:

1. existing repository test fixture/factory/seed helper;
2. existing service/domain API used by tests;
3. isolated setup API/CLI intended for test environments;
4. minimal direct setup in a disposable database only when project architecture makes that safe and the schema is verified.

Avoid relying on whatever happens to exist in a copied real database.

For sensitive systems, prefer a fully synthetic verification identity and records inside the isolated environment rather than a real user account copied from production-like data.

After fixture creation, verify the prerequisites programmatically before opening the browser. Examples:

- required permission evaluates true;
- required record exists exactly once;
- record/status/date matches the intended state;
- destructive state is disabled or isolated;
- fixture identifiers needed by the browser are returned explicitly.

## Preflight before browser clicks

Where practical, validate the non-visual contract before interacting with the UI.

Examples:

- authenticated endpoint returns expected status;
- route resolves with required parameters;
- response contains expected modal/drawer/root marker;
- target record exists;
- required DOM shell is present;
- required trigger exists exactly once;
- required action is visible for the verification role;
- async target or portal container exists;
- page is on the expected URL after login/navigation.

A preflight is not a replacement for browser verification. It separates routing/auth/state failures from selector or rendering failures so browser errors are meaningful.

## Async and modal lifecycle inspection

Before scripting HTMX, Turbo, AJAX, SPA navigation, modal, drawer, portal, or lazy-loaded interaction, read the code that opens and mounts it.

Resolve:

- which event/request starts it;
- where returned content is inserted;
- whether the shell already exists;
- whether content replacement changes the selector root;
- which event marks completion;
- whether the component auto-opens after swap/navigation;
- how it closes;
- whether the trigger/card must be re-queried after DOM replacement.

Do not assume a returned `200` means the modal became visible.

## Evidence-backed assertions

Every acceptance-critical assertion in the script must be traceable to one of:

- accepted requirement;
- current source behavior;
- current test/fixture contract;
- verified runtime preflight.

Do not assert guessed wording, guessed counts, guessed default states, guessed URLs, or guessed timing.

If exact copy is not part of acceptance, assert a stable semantic marker instead of brittle prose.

## Pre-delivery verifier audit

Before giving the script to the user, perform a static audit of the verifier itself:

- compile/parse the script;
- confirm every source file/token/selector referenced by the verifier still exists in the accepted source;
- confirm no obsolete credential or environment dependency remains;
- confirm fixture setup happens only in the isolated environment;
- confirm destructive form submissions are absent unless explicitly required and isolated;
- confirm expected screenshot count/states match the acceptance plan;
- confirm cleanup runs on both success and failure;
- confirm evidence does not persist secrets;
- confirm failure messages include enough context to distinguish auth, state, selector, endpoint, and visual failures.

When possible, make the verifier run its own source-contract checks before starting the application.

## Failure classification: verifier defect vs application defect

When a run fails, do not immediately treat it as an application bug.

First classify the evidence:

- **Verifier defect** — wrong selector, wrong expected label, stale route, missing fixture prerequisite, incorrect timing/lifecycle assumption, wrong test identity.
- **Application defect** — current source/runtime violates an accepted requirement despite verified prerequisites and a source-backed verifier.
- **Environment defect** — browser/runtime/dependency/OS prevents valid execution.
- **Source conflict** — the executed source differs from the inspected source.

A useful diagnostic should report, where safe:

- current URL;
- selector/endpoint attempted;
- match count;
- relevant record/status/role state;
- HTTP response status;
- concise nearby DOM/header/modal text;
- screenshot/trace path on failure.

Do not enter a loop of changing one guessed assumption per run. After the first verifier-defect failure, re-audit the remaining workflow dependencies before delivering the next version.

---

# Verification profiles

Select the smallest profile that proves the changed scope.

## Profile V1 — Visual smoke

Use for a small styling/layout change.

Verify:

- page loads;
- no fatal console error;
- no failed essential request;
- changed area is visible;
- no obvious clipping/overflow;
- one representative desktop screenshot;
- mobile screenshot if responsive behavior changed.

## Profile V2 — Interactive workflow

Use for changed buttons, forms, HTMX/AJAX, modal/drawer, filtering, search, or navigation.

Verify:

- real workflow actions;
- expected state transitions;
- validation behavior when relevant;
- modal/drawer lifecycle;
- URL behavior where relevant;
- focus return for modal/drawer;
- console/page errors;
- failed network requests;
- screenshots at meaningful final states.

## Profile V3 — Responsive acceptance

Use when layout quality matters across device sizes.

Use the project's defined viewport matrix when available.

If no matrix exists and the user requested general responsive verification, representative defaults may be used and must be labeled as representative, not project requirements:

```text
Desktop: 1440 × 900
Tablet:  1024 × 1366
Mobile:   390 × 844
```

Verify at each required viewport:

- no horizontal overflow unless intentionally designed;
- no clipped controls;
- no overlapping fixed/sticky elements;
- readable primary content;
- modal/drawer fits viewport;
- primary action remains reachable;
- navigation remains usable;
- tables/cards adapt correctly.

## Profile V4 — Role/theme/direction matrix

Use only when affected requirements include role-aware UI, themes, or RTL.

Test only relevant combinations.

Possible dimensions:

- privileged / standard / restricted roles;
- Light / Dark / Auto;
- LTR / RTL;
- Desktop / Tablet / Mobile.

Do not blindly test the Cartesian product. Select combinations that can change the acceptance decision.

## Profile V5 — Visual regression

Use when:

- an approved visual baseline exists;
- a release or repeated regression check needs pixel/image comparison;
- the user explicitly requests visual regression.

Rules:

- baseline must come from an accepted checkpoint;
- do not create a new baseline from a failing or unreviewed screen;
- record threshold/configuration used;
- inspect diffs, do not auto-accept them;
- update baselines only after human/requirement acceptance.

---

# Browser responsibilities

A browser verification runner should, when relevant:

1. start or connect to the real application;
2. confirm health/startup;
3. use isolated synthetic data;
4. authenticate as required role;
5. open the real target route;
6. perform the accepted workflow;
7. assert essential headings/content/state;
8. verify important URLs or route transitions;
9. inspect JavaScript console errors;
10. capture uncaught page errors;
11. record failed essential network requests;
12. perform keyboard smoke checks where interaction matters;
13. capture selected screenshots;
14. retain trace only on failure or retry;
15. never record video.

---

# HTMX / AJAX verification

For HTMX, Turbo, fetch/XHR, or similar partial-update workflows, verify:

- request completes successfully;
- expected target is updated;
- no duplicate DOM IDs are introduced;
- modal/drawer does not remain stale after success;
- validation errors remain visible after invalid submission;
- loading state appears and clears;
- repeat click does not create duplicate actions where relevant;
- normal fallback remains functional if required;
- browser history/URL behavior matches requirements;
- focus is restored or moved appropriately;
- no unexpected full-page navigation occurs.

Do not infer successful HTMX behavior from route unit tests alone.

---

# Console, page-error, and network policy

Collect:

- `pageerror` / uncaught JavaScript exceptions;
- console `error`;
- console `warning` only when relevant to changed behavior;
- failed requests;
- essential responses with HTTP 4xx/5xx.

Classify network failures:

- expected/intentional;
- third-party/non-critical;
- application-critical.

Do not fail a screen solely because an unrelated optional third-party asset failed unless it changes the accepted behavior.

A required application request returning unexpected 4xx/5xx is a failure.

---

# Screenshot policy

Screenshots are evidence, not click-by-click documentation.

Capture only meaningful acceptance checkpoints.

Naming pattern:

```text
<screen>__<role>__<viewport>__<state>.png
```

Examples:

```text
dashboard__standard-role__desktop__default.png
dashboard__standard-role__mobile__filtered-state.png
records__restricted-role__desktop__restricted-view.png
```

For a normal changed screen, prefer:

- desktop final state;
- mobile final state;
- tablet only when required or breakpoint-sensitive;
- one failure screenshot when a workflow fails.

Do not capture:

- passwords;
- secrets/tokens;
- real PHI/PII;
- every click;
- duplicate states;
- browser chrome unless needed to prove URL/viewport behavior.

---

# Visual inspection checklist

Review screenshots and live browser state for:

## Layout

- clipping;
- overflow;
- overlapping elements;
- unintended horizontal scroll;
- broken grid/flex wrapping;
- misaligned cards;
- inconsistent spacing;
- sticky header collisions;
- drawer/modal overflow;
- content hidden under fixed navigation.

## Hierarchy and readability

- primary action is visually clear;
- headings and sections are distinguishable;
- text is readable;
- dense information remains scannable;
- empty states are intentional;
- status is not communicated by color alone.

## Interaction states

- hover/focus state is visible where relevant;
- disabled controls look disabled;
- loading state does not freeze the page;
- validation errors appear near the relevant control;
- success/error toast is visible and dismissible where required.

## Responsive behavior

- navigation adapts correctly;
- touch targets remain usable;
- cards/tables remain readable;
- modal/drawer fits smaller screens;
- filters/actions remain reachable;
- no accidental desktop-only interaction.

## Theme/direction

When in scope:

- light mode;
- dark mode;
- RTL;
- LTR;
- contrast-sensitive states;
- icon/text alignment.

---

# Keyboard and accessibility smoke

Run when the changed UI is interactive or accessibility-sensitive.

Minimum targeted checks:

- Tab reaches interactive controls in logical order;
- focused element is visibly identifiable;
- Enter/Space activates appropriate controls;
- Escape closes modal/drawer when required;
- modal/drawer traps focus when required;
- closing returns focus to a sensible trigger;
- fields have accessible names;
- buttons/links have accessible names;
- no serious ARIA misuse;
- no duplicate IDs in the changed critical area.

Use axe-core or the repository's existing accessibility scanner when already available or selected by the parent verification plan.

Do not generate a massive accessibility report for a small unrelated change.

---

# Visual regression comparison

When baseline comparison is selected:

1. confirm baseline belongs to accepted checkpoint;
2. reproduce deterministic viewport/theme/data;
3. disable or stabilize non-deterministic content when safe:
   - clocks;
   - random values;
   - animations;
   - transient timestamps;
4. capture current screenshot;
5. generate diff;
6. inspect changed regions;
7. classify differences:
   - intended;
   - harmless rendering variance;
   - regression;
8. do not overwrite baseline until the difference is accepted.

Avoid masking large UI regions merely to force a pass.

---

# Evidence package

Default root:

```text
artifacts/verification/visual-browser/
```

Successful minimal package:

```text
visual-browser/
├── summary.md
├── browser-summary.json
├── screenshots/
│   ├── <meaningful-state>.png
│   └── ...
└── manifest.json
```

Add only when needed:

```text
├── failures.json
├── network-failures.json
├── console-errors.json
├── accessibility-summary.json
├── visual-diffs/
└── traces/
```

Never create empty folders.

Never retain video.

On successful workflows, do not retain full Playwright traces by default.

---

# `browser-summary.json`

Include concise machine-readable fields:

```json
{
  "status": "VISUALLY_VERIFIED",
  "source_checkpoint": "...",
  "target_routes": [],
  "roles_tested": [],
  "viewports": [],
  "themes": [],
  "directions": [],
  "workflows": [],
  "console_errors": 0,
  "page_errors": 0,
  "critical_network_failures": 0,
  "screenshots": [],
  "traces": [],
  "remaining_risks": []
}
```

Use actual evidence only.

---

# Failure workflow

When browser verification fails:

1. stop at the first meaningful failure;
2. capture the failing state screenshot;
3. record page URL and viewport;
4. record first meaningful console/page/network error;
5. retain Playwright trace if useful;
6. identify exact route, template, JS function, selector, or CSS area;
7. classify:
   - application logic;
   - selector drift;
   - auth/permission;
   - environment;
   - network;
   - responsive layout;
   - accessibility;
   - visual regression;
   - test-data issue;
8. hand back a focused repair request to the implementation loop;
9. after repair, rerun failed workflow first;
10. rerun affected responsive/role variants;
11. stop after the parent workflow's bounded retry limit.

Do not weaken assertions or hide errors to obtain a pass.

---

# Acceptance decision

## `VISUALLY_VERIFIED`

Use only when:

- required real-browser workflow passed;
- required screenshots were captured and reviewed;
- no unresolved critical console/page errors;
- no unresolved critical network failures;
- responsive targets required by scope passed;
- required role/theme/RTL variants passed;
- evidence paths exist;
- screenshots actually correspond to the claimed state.

## `FUNCTIONALLY_VERIFIED_VISUAL_PENDING`

Use when browser interactions pass but screenshots have not been visually reviewed.

## `VISUAL_FAILED`

Use when a required visual or interaction defect is present.

## `BLOCKED_BY_MISSING_BROWSER_EVIDENCE`

Use when no browser/screenshot evidence can be produced.

## `BLOCKED_BY_ENVIRONMENT`

Use when browser tooling, runtime, credentials, or environment prevents a valid run.

---

# Integration with Verification and Acceptance

The parent `verification-and-acceptance` skill should invoke this skill when:

- a user-facing screen changed;
- frontend behavior changed;
- responsive behavior is acceptance-critical;
- browser-only behavior must be proven;
- a phase/release includes frontend acceptance.

Return to the parent:

- visual status;
- workflows executed;
- roles/viewports/themes/directions tested;
- screenshot paths;
- console/page/network summary;
- accessibility summary when selected;
- trace path only on failure/retry;
- remaining visual risks.

The parent skill remains responsible for combining this evidence with:

- tests;
- migrations;
- lint;
- runtime;
- Git/diff;
- requirements;
- final checkpoint status.

---

# Project-specific example — clinic command center

This is an example pattern only. Inspect the repository before using it.

For a clinic command-center page whose requirements include desktop, tablet, mobile, roles, HTMX actions, and dark/RTL support:

1. use a disposable/synthetic clinic database;
2. log in as the required role;
3. open the real clinic route;
4. verify the command header and required KPIs;
5. exercise non-destructive filters/search/sort;
6. exercise safe HTMX actions on synthetic records;
7. open modal/drawer interactions;
8. verify destructive or finalizing previews without confirming them on real data;
9. capture required responsive screenshots;
10. inspect console/page/network failures;
11. run dark/RTL variants only if they are in the accepted requirement;
12. classify visual acceptance from evidence.

Do not use this example to invent routes, labels, selectors, roles, or requirements.
