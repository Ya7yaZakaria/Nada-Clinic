# Project Memory

## Current source state

- Project: Nada Clinic.
- Workflow authority: `AGENTS.md` (ProCoder Guarded v4 plus the repository test rules).
- Source contains models/routes/services/forms/templates for the current clinic domains documented in `docs/ARCHITECTURE.md`.
- Latest migration file present in source: `20260808_0072_reconcile_model_indexes.py`. The actual local database revision must be verified with `flask db current`; file presence alone is not runtime migration evidence.
- Development Role Preview exists as a development-only feature. Historical evidence is retained in `docs/DEVELOPMENT_ROLE_PREVIEW.md`.
- Major new product stages should not start automatically; continue personal-trial/refinement unless the user explicitly changes direction.

## Current verified test baseline

Developer-provided runtime evidence reviewed on 2026-08-09:

```text
544 tests collected in 3.08s
544 passed in 203.31s (0:03:23)
```

The suite now uses domain folders, `tests/conftest.py`, `tests/factories.py`, `slow`/`migration` runtime tiers, evidence-based redundancy rules, and valid low-cost test credentials where cryptographic strength is not the subject. Direct hashing/seed credential tests still use the production path.

Current test structure and commands are in `docs/TESTING.md`.

## Test constraints

- Do not recreate old flat duplicate test files after domain organization.
- Run `pytest --collect-only` after structural test changes.
- Preserve regression, security/RBAC, cross-record isolation, migration, and domain-invariant coverage.
- Do not apply a global transactional DB fixture or xdist parallelism until isolation is proven for the affected domains.

## Documentation policy

Canonical active docs are intentionally limited. Old sprint/stage documents were consolidated under `docs/history/` during the documentation cleanup. Their original text is retained there for traceability, but current source and fresh runtime evidence take priority.

## Next engineering work

- Continue real personal trial and verified fixes.
- If test runtime needs further optimization, inspect database lifecycle domain-by-domain rather than deleting coverage.
- Re-read the freshest project source and `AGENTS.md` before every implementation/repair/verification task.
