# Nada Clinic — Dashboard vNext Implementation Checklist

**Status:** Approved guide  
**Goal:** Rebuild the Dashboard as a compact, premium clinic command center.  
**Rule:** Finish each section completely before moving to the next one.

---

# 0. Before We Touch the Dashboard

- [ ] Re-read the latest synced project.
- [ ] Re-read the current `AGENTS.md`.
- [ ] Check Git status and current uncommitted changes.
- [ ] Re-read the current dashboard route, service, template, CSS, JS, permissions, and tests.
- [ ] Confirm the current database/migration state without changing the real database.
- [ ] Confirm the existing Admin / Doctor / Reception permissions and available dashboard data.
- [ ] Record the current baseline screenshots and test status if anything changed since the last dashboard inspection.

**Stop here if the current source conflicts with the approved plan.**

---

# 1. Build the New Top of the Dashboard

This section replaces the oversized opening area and makes the first screen immediately useful.

## 1.1 Compact Clinic Command Bar

- [ ] Remove/reduce the large greeting hero.
- [ ] Keep the current date visible.
- [ ] Keep clinic status if already supported by the existing backend.
- [ ] Keep Patient Search.
- [ ] Keep New Patient / Add Patient based on the existing permission.
- [ ] Keep date-range controls:
  - Today
  - 7 Days
  - This Month
  - Last Month
  - Custom
- [ ] Keep the bar compact on desktop.
- [ ] Collapse controls intelligently on mobile.
- [ ] Make sure role permissions still control the actions.
- [ ] Do not invent new clinic-status behavior or routes.

## 1.2 Today Clinic — directly below the command bar

Keep Today Clinic as the first operational section.

Show the supported current-day states:

- [ ] Appointments
- [ ] Waiting
- [ ] In Progress if the existing workflow supports it
- [ ] Completed
- [ ] No-show / Cancelled as currently modeled
- [ ] Emergency
- [ ] Keep `Open Today Clinic`.

For each counter:

- [ ] Use existing filters/routes for drill-down where available.
- [ ] Do not invent a destination just to make the card clickable.
- [ ] Use compact semantic status colors.
- [ ] Make the section readable within a few seconds.
- [ ] Avoid repeating the same Today Clinic information elsewhere.

## 1.3 Needs Attention — directly after Today Clinic

Convert Needs Attention from simple counts into actionable items.

Each supported item should show, where the data exists:

```text
Severity
Problem
Count / amount
Age / overdue context
Action
```

Example:

```text
HIGH
63 results awaiting review
8 older than 48h
Review results →
```

Possible existing categories to verify before using:

- [ ] Results awaiting review
- [ ] No-shows
- [ ] Outstanding balances
- [ ] Existing overdue/preparation items already supported by the backend

For every attention item:

- [ ] Verify the data source.
- [ ] Verify which roles can see it.
- [ ] Define a deterministic non-clinical severity rule where appropriate.
- [ ] Do not invent medical severity thresholds.
- [ ] Provide a real action/destination where one already exists.
- [ ] Keep the layout compact on desktop and mobile.

## Section 1 verification

- [ ] Dashboard focused tests pass.
- [ ] Admin screenshot reviewed.
- [ ] Doctor screenshot reviewed.
- [ ] Reception screenshot reviewed.
- [ ] Desktop first viewport shows operational information early.
- [ ] Mobile first viewport no longer consists mainly of greeting/filter UI.
- [ ] No broken permission-dependent actions.
- [ ] No horizontal overflow.

**Do not continue until the top of the Dashboard feels correct.**

---

# 2. Make the Dashboard Truly Role-Specific

Do not build one Admin grid and hide cards from other roles.

Each role gets a purposeful composition using the same design system.

## 2.1 Admin Dashboard

Target order:

```text
Clinic Command Bar
Today Clinic
Needs Attention
Core KPIs
Activity Trend
Clinic Agenda
More Insights / Finance
```

- [ ] Keep operational + clinical + finance visibility according to current permissions.
- [ ] Do not put all analytics on the home page.
- [ ] Keep finance useful but below the current-day operational state.

## 2.2 Doctor Dashboard

Target order:

```text
Clinic Command Bar
Today Clinic
Clinical Needs Attention
Clinical workload KPIs
Upcoming patients / surgery
Activity Trend
More Clinical Insights
```

- [ ] Prioritize results requiring review and clinical workload.
- [ ] Keep upcoming patient/surgery work prominent.
- [ ] Do not let finance dominate the Doctor home page.
- [ ] Keep all existing RBAC protections.

## 2.3 Reception Dashboard

Target order:

```text
Clinic Command Bar
Today Clinic
Quick Actions
Waiting / Appointment state
No-shows
Upcoming appointments
Operational KPIs
```

Quick actions may use only existing verified actions such as:

- [ ] Book Appointment
- [ ] New Patient
- [ ] Open Today Clinic
- [ ] Patient Search

Must fix:

- [ ] Remove the current empty structural gaps created when Admin/Doctor cards are hidden.
- [ ] Do not reserve invisible columns for restricted data.
- [ ] Do not call restricted backend helpers unnecessarily.

## Section 2 verification

- [ ] Admin layout is purposeful.
- [ ] Doctor layout is purposeful.
- [ ] Reception layout is purposeful.
- [ ] Reception has no permission-created empty holes.
- [ ] RBAC tests pass.
- [ ] Restricted backend services remain protected.
- [ ] Role-preview screenshots are reviewed for all three roles.

---

# 3. Upgrade the KPI Strip

Replace isolated numbers with meaningful context.

## 3.1 Choose the KPIs

Verify the exact existing data first.

Likely Admin set:

- [ ] Appointments
- [ ] Visits
- [ ] Collected
- [ ] Outstanding

Likely Doctor set:

- [ ] Appointment / patient workload
- [ ] Visits
- [ ] Results requiring review
- [ ] Relevant clinical workload metric

Likely Reception set:

- [ ] Appointments
- [ ] Waiting
- [ ] No-shows
- [ ] Upcoming / confirmation metric only if existing data supports it

## 3.2 Add period comparison where meaningful

Target format:

```text
Appointments
39
↑ 12% vs previous period
```

Implement:

- [ ] Current-period boundaries.
- [ ] Equivalent previous-period boundaries.
- [ ] Absolute difference.
- [ ] Percentage difference where mathematically valid.
- [ ] Positive change.
- [ ] Negative change.
- [ ] No change.
- [ ] Previous period = zero.
- [ ] Empty current period.
- [ ] Custom date range behavior.

Do not add a percentage where it would be misleading.

Some KPIs may use operational context instead:

```text
Outstanding
EGP 3,450
5 patients • oldest balance 18 days
```

## 3.3 KPI interactions

- [ ] Add drill-down only when an existing destination/filter supports it.
- [ ] Keep role permissions intact.
- [ ] Keep cards compact.
- [ ] Ensure values remain readable on mobile.
- [ ] Make trend/delta colors semantic but restrained.

## Section 3 verification

- [ ] Comparison unit tests pass.
- [ ] Divide-by-zero cases tested.
- [ ] Custom-date cases tested.
- [ ] Role rendering tested.
- [ ] Light/dark screenshots reviewed.
- [ ] Mobile KPI layout reviewed.

---

# 4. Replace the Long Analytics Dump with Agenda + Insights

This is where the current page becomes much shorter.

## 4.1 Keep one primary Overview chart

Preferred primary chart:

**Activity Trend**

- [ ] Keep only one major chart on Overview unless later evidence proves another is essential.
- [ ] Keep it linked to the selected date range.
- [ ] Keep chart height controlled.
- [ ] Verify mobile behavior.
- [ ] Verify dark mode.
- [ ] Verify RTL.
- [ ] Provide a readable fallback/text summary where appropriate.

## 4.2 Build one Clinic Agenda

Replace separate competing `Upcoming Appointments` and `Upcoming Surgeries` blocks with one chronological list.

Target:

```text
NEXT 7 DAYS

TODAY
09:00  Patient A    Appointment
11:30  Patient B    Appointment

THU
14:00  Patient C    Surgery
```

Tasks:

- [ ] Reuse existing appointments data.
- [ ] Reuse existing surgery data.
- [ ] Merge into one presentation/read model.
- [ ] Sort chronologically.
- [ ] Visually distinguish item type.
- [ ] Add useful empty state.
- [ ] Add `All / Appointments / Surgery` filter only if it improves usability.
- [ ] Keep existing navigation and permissions.
- [ ] Do not duplicate domain business logic inside the template.

## 4.3 Move deep analytics into Insights

Create a deeper analytics area instead of keeping all charts on Overview.

Target organization:

```text
Insights
├── Clinical
├── Appointments
├── Journeys
└── Finance
```

or an equivalent tabbed Dashboard structure if that fits the existing routes better.

### Clinical

Review:

- [ ] Visits by Type
- [ ] Clinical activity
- [ ] Investigation activity
- [ ] Ultrasound activity
- [ ] Surgery activity

### Appointments

Review:

- [ ] Appointment Status
- [ ] Appointment Types
- [ ] Appointment Sources
- [ ] No-show behavior
- [ ] Booking trend if already supported

### Journeys

Review:

- [ ] Journey Mix
- [ ] Active Journeys
- [ ] Other existing journey metrics

### Finance

Review:

- [ ] Revenue vs Expenses
- [ ] Collected by Service
- [ ] Outstanding balances
- [ ] Existing payment activity

For every existing chart decide only once:

```text
KEEP
MOVE
CONVERT
MERGE
REMOVE
```

Use these questions:

- [ ] What question does it answer?
- [ ] Which role needs it?
- [ ] Is Overview the right place?
- [ ] Is the chart type actually useful?
- [ ] Is the same information shown elsewhere?
- [ ] Would a horizontal bar/list/table be clearer?
- [ ] Does it have a meaningful drill-down?
- [ ] Does it work in dark mode?
- [ ] Does it work in RTL?
- [ ] Is it still useful on mobile?

Prefer bars/lists over doughnuts when precise category comparison is the real task.

## 4.4 Clean up chart implementation while moving them

- [ ] Remove obsolete chart initialization.
- [ ] Make chart JS tolerate role-specific missing canvases.
- [ ] Replace dashboard hard-coded chart colors with existing/approved design tokens.
- [ ] Keep light/dark/accent themes consistent.
- [ ] Do not add another ad-hoc CSS override layer.

## Section 4 verification

- [ ] Overview is materially shorter.
- [ ] Overview has only high-value information.
- [ ] Agenda ordering tested.
- [ ] Chart JS has no role-specific errors.
- [ ] Light/dark chart screenshots reviewed.
- [ ] Mobile screenshots reviewed.
- [ ] No duplicate overview information.
- [ ] Insights retain useful analytics instead of deleting them blindly.

---

# 5. Finish the Dashboard Across Mobile, RTL, Dark Mode and Accessibility

Do this after the information architecture is stable so the same work is not repeated.

## 5.1 Mobile

Target mobile order:

```text
Compact Header
Today Clinic
Needs Attention
Quick Actions
Clinic Agenda
Core KPIs
Primary Trend
More Insights
```

- [ ] Do not stack the full desktop Dashboard unchanged.
- [ ] Compact date controls.
- [ ] Reduce decorative/greeting content.
- [ ] Keep touch targets usable.
- [ ] Avoid multiple full-size charts in Overview.
- [ ] Keep quick actions reachable.
- [ ] Measure final page height.
- [ ] Compare against the current ~7127 px baseline.
- [ ] Confirm no horizontal overflow.

## 5.2 Tablet / iPad

- [ ] Verify grid breakpoints.
- [ ] Prevent chart compression.
- [ ] Keep cards balanced.
- [ ] Keep touch actions usable.
- [ ] Avoid a squeezed desktop layout.

## 5.3 RTL / Arabic

Translate/review all Dashboard-visible strings:

- [ ] Heading
- [ ] Greeting if retained
- [ ] Today Clinic
- [ ] Reporting Period
- [ ] KPI labels
- [ ] Needs Attention
- [ ] Agenda labels
- [ ] Date controls
- [ ] Chart legends
- [ ] Empty states
- [ ] Comparison text
- [ ] Actions

Fix:

- [ ] Locale-aware dates.
- [ ] Date-range bidi ordering.
- [ ] `<bdi>` / bidi isolation where required.
- [ ] Custom date panel currently escaping the RTL viewport.
- [ ] Direction-aware positioning.
- [ ] Chart legends/labels/tooltips in RTL.
- [ ] Desktop RTL.
- [ ] Mobile RTL.

## 5.4 Dark mode

- [ ] Preserve the current strong dark-mode look.
- [ ] Verify all new components.
- [ ] Verify chart contrast.
- [ ] Verify semantic colors.
- [ ] Verify focus states.

## 5.5 Accessibility

- [ ] Identify and fix the previously detected unnamed interactive control.
- [ ] Give icon-only buttons accessible names.
- [ ] Verify labels for custom date controls.
- [ ] Verify keyboard access to date controls and Dashboard actions.
- [ ] Verify keyboard access to Agenda/Insights controls.
- [ ] Verify visible focus states.
- [ ] Review heading hierarchy and landmarks.

## 5.6 Browser cleanup

- [ ] Inspect the existing `/favicon.ico` 404.
- [ ] Fix it only if appropriate to the current manifest/static setup.
- [ ] Verify console errors/warnings.
- [ ] Verify failed requests.
- [ ] Verify page errors.

## Section 5 verification

Capture and inspect:

### Roles
- [ ] Admin
- [ ] Doctor
- [ ] Reception

### Viewports
- [ ] Desktop 1536×960
- [ ] Laptop 1366×768
- [ ] Tablet 1024×1366
- [ ] Mobile 390×844

### Modes
- [ ] Light English
- [ ] Dark English
- [ ] RTL/Arabic

For each relevant scenario:

- [ ] Viewport screenshot
- [ ] Full-page screenshot
- [ ] Key section screenshots if needed
- [ ] Overflow check
- [ ] Console review
- [ ] Page-error review
- [ ] Network-failure review

---

# 6. Backend and Performance Check After the UI Is Complete

Do not refactor the backend before the new Dashboard actually requires it.

Current measured baseline:

```text
14 dashboard service calls
34 SQL queries
~143 ms cumulative isolated service time
```

## 6.1 Re-profile

Using a disposable database:

- [ ] Measure Dashboard service timings again.
- [ ] Measure SQL query counts again.
- [ ] Compare with baseline.
- [ ] Check for new N+1 behavior.
- [ ] Investigate only meaningful regressions.

## 6.2 DashboardService architecture

The service is large, but current performance was acceptable.

Only split it if the new implementation has made responsibilities genuinely difficult to maintain.

Possible future split, only if justified:

```text
ClinicalDashboardQueries
OperationsDashboardQueries
FinanceDashboardQueries
TodayDashboardQueries
```

Do not refactor merely because the file is long.

## Section 6 verification

- [ ] No backend errors.
- [ ] No unjustified query explosion.
- [ ] No meaningful performance regression left unexplained.
- [ ] Real database was not used for experimentation.

---

# 7. Final Project Verification

Only after Sections 1–6 are complete.

## 7.1 Code quality

- [ ] Run selected Guard Skills.
- [ ] Compilation passes.
- [ ] Ruff/lint passes if configured.
- [ ] Template syntax passes.
- [ ] `git diff --check` passes.
- [ ] Review final Dashboard diff for unrelated changes.

## 7.2 Tests

- [ ] Relevant Dashboard tests pass.
- [ ] RBAC tests pass.
- [ ] KPI comparison tests pass.
- [ ] Attention tests pass.
- [ ] Agenda tests pass.
- [ ] Broad/full regression suite passes.

Do not weaken a test to make it pass.

## 7.3 Runtime

- [ ] Run with disposable migrated/seeded data.
- [ ] Dashboard loads successfully.
- [ ] Admin works.
- [ ] Doctor works.
- [ ] Reception works.
- [ ] Date controls work.
- [ ] Today drill-downs work.
- [ ] Attention actions work.
- [ ] KPI drill-downs work where supported.
- [ ] Agenda links work.
- [ ] Insights work.
- [ ] Light/dark/RTL work.

## 7.4 Visual acceptance

Do not call the Dashboard visually verified until screenshots confirm:

- [ ] Header is compact.
- [ ] Today is prominent.
- [ ] Needs Attention is prominent.
- [ ] Reception has no empty layout holes.
- [ ] Mobile information priority is correct.
- [ ] Mobile page is significantly shorter than the old ~7127 px baseline.
- [ ] No page horizontal overflow.
- [ ] RTL custom date panel stays inside viewport.
- [ ] RTL dates remain readable.
- [ ] Dark mode charts are readable.
- [ ] Agenda is scannable.
- [ ] Permission differences do not break layout.

## 7.5 Documentation and checkpoint

After verification only:

- [ ] Update `CHANGELOG.md`.
- [ ] Update `MEMORY.md` if appropriate.
- [ ] Update Dashboard/architecture documentation if behavior changed.
- [ ] Mark requirements completed in this file.
- [ ] Review final Git status.
- [ ] Review migration state.
- [ ] Recommend a checkpoint only if the complete evidence is clean.
- [ ] Commit/push only when explicitly requested.

---

# Final Definition of Done

The Dashboard vNext is finished when:

- [ ] The first screen tells us what is happening now.
- [ ] Today Clinic is immediately visible and useful.
- [ ] Needs Attention tells us what requires action.
- [ ] KPIs explain direction/context instead of showing isolated numbers.
- [ ] Admin, Doctor, and Reception each have a purposeful layout.
- [ ] Reception has no permission-created empty gaps.
- [ ] Upcoming Appointments and Surgeries are organized into one Clinic Agenda.
- [ ] Deep analytics live in Insights instead of overwhelming Overview.
- [ ] Overview has only one primary chart unless evidence justifies more.
- [ ] Mobile is intentionally designed and significantly shorter.
- [ ] RTL/Arabic date and popup problems are fixed.
- [ ] Dark mode remains strong.
- [ ] Accessibility issues are addressed.
- [ ] Backend performance remains acceptable.
- [ ] Focused and regression tests pass.
- [ ] Browser/runtime verification passes.
- [ ] Desktop/laptop/tablet/mobile screenshots are reviewed.
- [ ] Light/dark/RTL screenshots are reviewed.
- [ ] Admin/Doctor/Reception screenshots are reviewed.
- [ ] Final diff and Git status are reviewed.
- [ ] No destructive real-database work occurred.
- [ ] No commit/push occurred without explicit permission.

---

# Execution Order

```text
0. Fresh inspection
↓
1. New top of Dashboard
   Command Bar + Today + Needs Attention
↓
2. Role-specific layouts
   Admin + Doctor + Reception
↓
3. KPI upgrade
   Context + comparisons
↓
4. Agenda + Insights
   Shorten Overview + organize charts
↓
5. Finish UI everywhere
   Mobile + Tablet + RTL + Dark + Accessibility
↓
6. Backend/performance recheck
↓
7. Full verification + checkpoint review
```

That is the complete implementation path. Each feature is handled once, with its frontend, backend, role, responsive, and verification work kept together.
