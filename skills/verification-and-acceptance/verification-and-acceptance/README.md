# Verification and Acceptance Skill

This package provides the final verification stage for the four-skill software workflow.

It uses adaptive verification profiles so small repairs stay lightweight while features, phases, and releases receive the additional evidence they genuinely require.

Key behavior:

- safe Ruff formatting and lint verification;
- focused and relevant full tests;
- clean-database and migration validation when applicable;
- Playwright/browser workflow checks for user-facing changes;
- selected desktop and mobile screenshots only at meaningful checkpoints;
- tablet screenshots only when relevant;
- Playwright traces only on browser failure or flaky retry;
- no browser video generation;
- targeted accessibility and keyboard checks;
- coverage only when it adds decision value;
- schema deltas for normal database changes and full ER diagrams only at architecture checkpoints;
- concise LLM-readable evidence through `summary.md` and `manifest.json`;
- raw logs and expanded diagnostics only when a failure requires them;
- honest classification of verified, failed, unverified, missing, and remaining work.

Upload this ZIP as one skill package.


## Visual Browser Verification integration

For any user-facing frontend change, this skill delegates real-browser and visual acceptance to:

```text
../visual-browser-verification/SKILL.md
```

The specialist returns browser/visual evidence and a visual status. Verification and Acceptance remains the final orchestrator and combines that evidence with tests, migrations, guards, runtime checks, requirements, and Git review.
