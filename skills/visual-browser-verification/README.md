# Visual Browser Verification

Specialist skill for real-browser functional and visual acceptance.

## What it does

- Prefers existing Playwright/browser tooling.
- Verifies real routes and workflows.
- Requires an evidence-locked automation map before script generation; unresolved selectors, permissions, state gates, routes, fixtures, or async behavior must be inspected rather than guessed.
- Builds deterministic isolated fixtures and preflights acceptance-critical endpoints/state before browser clicks when applicable.
- Captures responsive screenshots.
- Checks console, page, and critical network errors.
- Supports HTMX/AJAX interaction verification.
- Adds targeted keyboard/accessibility smoke checks.
- Supports visual-regression comparison when an accepted baseline exists.
- Produces concise LLM-readable evidence.
- Never records browser video.
- Never claims visual verification without browser/screenshot evidence.

## Recommended orchestration

```text
Project Inspection
→ Implementation Planning
→ Guarded Implementation
→ Verification and Acceptance
   → Visual Browser Verification
```

`verification-and-acceptance` remains the final acceptance orchestrator. This skill supplies the browser/visual evidence.

## Safety

Use synthetic or disposable data for workflow actions. Do not capture real clinical/private data in screenshots. Do not silently add browser dependencies to production requirements.
