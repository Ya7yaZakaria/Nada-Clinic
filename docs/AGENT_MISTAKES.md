# Agent Mistakes Log

This file records mistakes made by the AI assistant/agent so future sessions do not repeat them.

Before generating scripts, patches, or implementation plans, the assistant must read this file and apply the prevention rules.

---

## Mistake 001 — Patched the wrong duplicate redirect

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

## Mistake 002 — Queried SettingsService outside Flask app context

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

## Mistake 003 — Touched unrelated dashboard/admin templates

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

## Mistake 004 — Documentation said pending after verification was complete

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

## Mistake 005 — Suggested new sprint too early

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
