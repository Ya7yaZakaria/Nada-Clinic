# Agent Mistakes Log

This file records mistakes made by the AI assistant/agent so future sessions do not repeat them.

Before generating scripts, patches, or implementation plans, the assistant must read this file and apply the prevention rules.

---

## Mistake 001 â€” Patched the wrong duplicate redirect

Date: 2026-07-15

Context:
Sprint 12.4 Workflow Defaults.

What went wrong:
The script replaced the first matching return redirect in app/routes/auth.py, which was the already-authenticated user branch, not the successful login branch.

Root cause:
Used generic replace_once on duplicated code without targeting both branches.

How detected:
Focused tests failed:
- test_login_respects_today_clinic_default_landing
- test_login_respects_patients_default_landing

Correction:
Restored affected files from HEAD and explicitly patched:
- current_user.is_authenticated branch
- successful login branch

Prevention rule:
When a pattern appears more than once, never use blind replace_once. Read the file and patch exact blocks.

Related commit:
1589f8d feat(settings): add sprint 12.4 workflow defaults

---

## Mistake 002 â€” Queried SettingsService outside Flask app context

Date: 2026-07-15

Context:
Sprint 12.4 correction script.

What went wrong:
The script called a DB-backed SettingsService method outside Flask app context.

Root cause:
Static sanity check called Setting.query without app.app_context().

How detected:
PowerShell showed RuntimeError: Working outside of application context.

Correction:
Removed DB-backed assertion outside app context.

Prevention rule:
Any service method that may query models must run inside app.app_context() or through tests.

---

## Mistake 003 â€” Touched unrelated dashboard/admin templates

Date: 2026-07-15

Context:
Initial Sprint 12.4 script.

What went wrong:
The script modified:
- app/templates/index.html
- app/templates/admin/index.html

These were out of scope.

Root cause:
Mixed workflow default feature with dashboard cleanup.

Correction:
Restored unrelated templates from HEAD and narrowed the script.

Prevention rule:
List allowed files before patching. Do not touch files outside scope.

---

## Mistake 004 â€” Documentation said pending after verification was complete

Date: 2026-07-15

Context:
Stage 12 freeze documentation.

What went wrong:
MEMORY.md still said verification/commit pending after tests and push succeeded.

Root cause:
Docs were written before final verification and not corrected after push.

Correction:
Updated MEMORY/README/CHANGELOG and handoff doc with final state.

Prevention rule:
After push, update MEMORY from final terminal output, not planned state.

---

## Mistake 005 â€” Suggested new sprint too early

Date: 2026-07-15

Context:
After Sprint 12.4.

What went wrong:
Suggested Printing Preferences while user wanted Settings Freeze.

Root cause:
Assumed next feature direction.

Correction:
Switched to Stage 12 Settings Freeze.

Prevention rule:
After a sprint closes, ask whether to freeze, continue, or pause before proposing new features.

---

## General Prevention Checklist

Before generating scripts:

- Read MEMORY.md.
- Read docs/Project_Handoff_Pause_After_Stage_12.md.
- Read this mistakes log.
- Read current relevant repo files.
- Identify duplicate patterns before replacement.
- Do not call DB-backed services outside app context.
- List allowed files before patching.
- Ask user approval before file changes unless direct script requested.
- Avoid unrelated cleanup.
- Do not write pending docs after final verification.
- Do not propose new stages during pause/trial mode.
- Never claim success without terminal output.

---

## Mistake 006 â€” Ignored repository agent instructions

Date: 2026-07-16

Context:
Personal Trial Sprint P1 application shell and dashboard work.

What went wrong:
Implementation started before reading docs/AGENT.md and
docs/AGENT_MISTAKES.md.

Root cause:
Relied on conversation assumptions instead of the mandatory
repository source order.

How detected:
The user provided the exact docs/AGENT.md path.

Correction:
Read both repository agent files before continuing.

Prevention rule:
Always read MEMORY.md, the handoff document, docs/AGENT_MISTAKES.md,
and docs/AGENT.md before project scripts.

---

## Mistake 007 â€” Patched stale state instead of current local files

Date: 2026-07-16

Context:
P1 correction scripts after local uncommitted changes existed.

What went wrong:
Generated exact-block replacements from an older repository state
after earlier scripts had already changed the local files.

Root cause:
Used GitHub state as patch input instead of current local file content
and git diff.

How detected:
Correction scripts reported that expected blocks were not found.

Correction:
Collected and reviewed P1_LOCAL_REVIEW.txt containing current local
files and git diff.

Prevention rule:
When the working tree is dirty, patch only from current local file
content supplied by the user.

---

## Mistake 008 â€” Delivered invalid Python scripts

Date: 2026-07-16

Context:
P1 correction delivery.

What went wrong:
Multiple generated Python scripts contained SyntaxError and did not run.

Root cause:
Nested quoting and multiline replacement code were not validated before
delivery.

How detected:
Python reported an unclosed parenthesis.

Correction:
Use simpler scripts and run py_compile before claiming script validity.

Prevention rule:
Never state that a generated Python script was validated unless
py_compile completed successfully.

---

## Mistake 009 â€” Introduced UTF-8 mojibake

Date: 2026-07-16

Context:
P1 templates and tests.

What went wrong:
Characters such as em dashes, apostrophes, separators, arrows, and
Arabic test text became mojibake.

Root cause:
Text passed through incompatible PowerShell and Python encodings.

How detected:
Current local templates contained strings such as malformed arrows and
separators.

Correction:
Rewrite affected files as explicit UTF-8 and prefer ASCII UI separators
inside generated terminal scripts.

Prevention rule:
After generated-file writes, inspect for mojibake and use explicit
UTF-8 encoding.

---

## Mistake 010 â€” Protected sidebar but leaked clinical dashboard links

Date: 2026-07-16

Context:
P1 permission-aware navigation.

What went wrong:
Visits was hidden from the Reception sidebar but remained linked from
the Open Visits card and Recent Visits dashboard section.

Root cause:
Permission review covered navigation only, not all links rendered by
the dashboard.

How detected:
The Reception P1 regression test found href="/visits/" in dashboard HTML.

Correction:
Make clinical dashboard data and sections conditional on clinical.view.

Prevention rule:
Permission review must cover routes, sidebar, topbar, cards, quick
actions, tables, and empty states.

---

## Mistake 011 â€” Violated prescription print freeze isolation

Date: 2026-07-16

Context:
Stage 5 unified prescription print preview.

What went wrong:
The shared topbar rendered the authenticated user's Doctor role inside
the print preview HTML.

Root cause:
Shell redesign did not review frozen print-content tests.

How detected:
test_stage_5_freeze_print_page_excludes_doctor_identity_and_safety_notes
failed.

Correction:
Hide user identity and logout controls for prescription and
investigation print preview endpoints.

Prevention rule:
Before changing base.html, run and review all print isolation tests.

---

## Mistake 012 â€” Modified tests before behavior was fully corrected

Date: 2026-07-16

Context:
P1 regression correction.

What went wrong:
Some obsolete expectations were updated while real permission and print
regressions still existed.

Root cause:
Treated all failures as test maintenance instead of classifying each
failure first.

How detected:
Focused tests continued to fail after test updates.

Correction:
Classify failures as regression, obsolete expectation, or test defect
before changing tests.

Prevention rule:
Fix product behavior first; update tests only when the documented
requirement changed.

---

## Mistake 013 â€” Used download workflow after direct VS Code request

Date: 2026-07-16

Context:
P1 script delivery.

What went wrong:
Asked the user to download and move scripts despite an explicit request
for a direct VS Code terminal workflow.

Root cause:
Used artifact delivery instead of following the requested developer
workflow.

How detected:
The user explicitly objected to repeated downloads.

Correction:
Deliver one PowerShell block that creates, runs, and removes the
temporary script inside the repository.

Prevention rule:
When the user requests a direct VS Code script, do not require external
downloads.
