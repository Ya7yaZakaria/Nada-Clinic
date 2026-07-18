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

---

## Mistake 014 - Broke frozen print and navigation HTML contracts

Date: 2026-07-16

Context:
Personal Trial Sprint P2.1-P2.2 sidebar behavior and visual design.

What went wrong:
The sidebar redesign introduced two regressions:
- The authenticated role name was rendered inside the shared sidebar
  footer during prescription print preview.
- Navigation names were duplicated inside visible labels,
  data-tooltip attributes, and aria-label attributes, breaking frozen
  HTML occurrence-count tests.

The first implementation script also used a text-layout-dependent
regular expression and failed on multiline navigation labels.

Root cause:
The implementation reviewed the visual sidebar structure but did not
preserve all existing base.html output contracts before generating the
patch. The script matched presentation formatting instead of stable
route identifiers, and focused tests were run only after file changes.

How detected:
The following tests failed:
- test_stage_5_freeze_print_page_excludes_doctor_identity_and_safety_notes
- test_stage_5_freeze_visit_prescription_nav_has_single_mobile_presets_link
- test_print_templates_sidebar_link_visible_for_doctor

Correction:
- Hide authenticated sidebar identity during print previews.
- Preserve exactly one desktop and one mobile visible navigation label.
- Match navigation anchors using their url_for endpoint rather than
  label formatting.
- Run print and navigation freeze tests before accepting base.html
  changes.

Prevention rule:
Before changing base.html:
- Read all frozen shell and print tests.
- Inventory text occurrence contracts and identity-isolation rules.
- Use route endpoints as stable patch anchors.
- Validate generated transformations in memory before writing files.
- Run prescription, investigation, and print-template focused tests
  immediately after the patch.

---

## Mistake 015 - Assumed a test filename without checking repository

Date: 2026-07-16

Context:
Personal Trial Sprint P2.1-P2.2 verification.

What went wrong:
The verification commands referenced tests/test_investigation_print_ui.py,
but that file does not exist in the repository.

Root cause:
Assumed a test filename instead of reading the current tests directory.

How detected:
Pytest returned:
ERROR: file or directory not found: tests/test_investigation_print_ui.py

Correction:
Search the current repository for relevant test files before issuing
focused verification commands.

Prevention rule:
Never provide an exact test-file command without verifying that the file
exists in the current repository. Use repository search or list matching
test files first.

---

## Mistake 016 - Rendered application shell on anonymous auth pages

Date: 2026-07-16

Context:
Personal Trial Sprint P2.1-P2.2 sidebar redesign.

What went wrong:
The redesigned application sidebar and topbar remained visible on the
anonymous login page. The login page also retained internal development
copy such as Stage 1 / Sprint 1.1.

Root cause:
The shell review covered authenticated Doctor and Reception states,
mobile navigation, and print preview, but did not include the anonymous
authentication state or review the existing login template content.

How detected:
Manual browser review of /auth/login showed the compact sidebar, user
placeholder, application topbar, and obsolete sprint text.

Correction:
- Add a dedicated anonymous auth-page shell state.
- Hide application navigation and topbar on authentication pages.
- Redesign the login page as a standalone branded access screen.
- Remove stage, sprint, and development wording from user-facing copy.

Prevention rule:
Every shared-shell change must be manually reviewed in these states:
- anonymous login
- authenticated Doctor
- authenticated Reception
- mobile drawer
- print preview
- light and dark themes

User-facing templates must not contain stage, sprint, development, or
implementation-status wording.


---

## Mistake 018 - Used brittle exact indentation matching on dirty template

Date: 2026-07-16

Context:
P2 login shell duplicate Jinja block correction.

What went wrong:
The correction script searched for an exact multiline block including
specific indentation. The current local base.html used different
spacing, so the script found zero matches and made no correction.

Root cause:
Used exact text replacement on a dirty local template instead of a
structure-aware or whitespace-tolerant match.

How detected:
The script reported:
Remove nested duplicate content block: expected 1 match, found 0

Correction:
Use a whitespace-tolerant regular expression for the exact Jinja block
structure, then verify the final number of content and auth_content
blocks before writing.

Prevention rule:
For dirty HTML or Jinja templates, do not depend on indentation.
Match stable structural tokens and validate the transformed template
before writing files.

---

## Mistake 017 - Defined the Jinja content block twice

Date: 2026-07-16

Context:
P2 anonymous login shell separation.

What went wrong:
The base template defined the Jinja block named content once inside the
authenticated application shell and again inside the anonymous auth
branch.

Root cause:
Tried to reuse the existing content block by nesting another content
block inside auth_content.

How detected:
Jinja raised:
TemplateAssertionError: block 'content' defined twice

The error prevented all templates extending base.html from rendering.

Correction:
- Keep content as the single authenticated application-page block.
- Use auth_content as a separate anonymous authentication-page block.
- Make auth/login.html override auth_content only.

Prevention rule:
Every Jinja block name must be unique inside one template. After editing
a shared base template, count block definitions and render both an
authenticated page and an anonymous page before broader tests.

## 2026-07-18 - Do not delay requested runnable commands

Issue:
- The assistant continued planning when the user expected an immediate runnable
  development command.

Prevention:
- When the user explicitly asks for code or a command to run, provide the narrow
  runnable command first.
- Clearly distinguish implemented features from planned features.
- Do not imply that an unimplemented development control already exists.

## 2026-07-18 - Avoid interactive Git pagers in user-run commands

Issue:
- A `git diff` command opened Git's interactive pager and left the terminal
  waiting at `(END)`, which made it look like the command had stopped.

Prevention:
- Use `git --no-pager diff` in commands intended for the user to run.
- For session-wide behavior in PowerShell, set:
  `$env:GIT_PAGER = "cat"`.
- When `(END)` appears, instruct the user to press `q` to return to the terminal.
- Avoid giving long interactive terminal commands without explaining how to exit.

## 2026-07-18 - Avoid Unicode punctuation in terminal-generated documentation

Issue:
- A Unicode em dash in a Python script pasted through PowerShell was written as
  `?` in the generated Markdown heading because of terminal encoding behavior.

Prevention:
- Use plain ASCII punctuation such as `-` in terminal-generated file content.
- Do not use em dashes, smart quotes, or other Unicode punctuation in PowerShell
  here-strings unless encoding behavior has been verified.
- Read generated files using `utf-8-sig` and write them explicitly as UTF-8.
- Review generated headings after writing files.
- Prefer ASCII-safe documentation text in scripts that users paste into Windows
  PowerShell.

## 2026-07-18 - Use Python instead of Get-Content for UTF-8 verification

Issue:
- PowerShell Get-Content displayed valid UTF-8 punctuation as mojibake such as
  ??? and made it unclear whether the file itself was corrupted or only the
  terminal display was incorrect.

Prevention:
- Use Python to read and print UTF-8 files when verifying generated content.
- Do not rely on Get-Content to validate Unicode or UTF-8 punctuation.
- Read files with encoding="utf-8-sig" when a BOM may exist.
- Use Get-Content only for ASCII-safe content or when PowerShell encoding has
  been explicitly configured and verified.
- Preferred verification pattern:
  from pathlib import Path
  text = Path("path/to/file.md").read_text(encoding="utf-8-sig")
  for line in text.splitlines():
      print(line)

## 2026-07-18 - Verify local file names and local file state before commands

Issue:
- The assistant supplied test file names that did not exist in the repository.
- The assistant also retried template replacements using assumptions after a
  partially completed script changed the local implementation state.

Prevention:
- Read or discover actual local test filenames before generating pytest
  commands.
- Use `Path("tests").glob(...)` when exact local filenames are not confirmed.
- After a partially failed write script, inspect the local file and Git diff
  before generating a correction.
- Never assume the working tree still matches the repository version after a
  partial script execution.
- Build correction scripts from the user's current local output, not from the
  original source snapshot.
