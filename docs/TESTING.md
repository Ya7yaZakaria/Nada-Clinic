# Testing

## Structure

```text
tests/
├── conftest.py      # shared pytest fixtures
├── factories.py     # reusable test-data builders
└── <domain folders>/
```

Keep scenario-specific setup local when sharing it would make a test harder to understand.

## Rules

- Test behavior and project contracts, not implementation details.
- Avoid duplicate tests and duplicate setup.
- Preserve regression, security/RBAC, migration, cross-record isolation, and domain-invariant coverage.
- Delete tests only when duplicate, obsolete, or superseded by stronger current coverage.
- Use valid low-cost hashes for ordinary test users; keep the real production hash path in password/security tests.
- Mark genuinely expensive tests `slow` and migration-specific tests `migration`.
- Do not use shared database state, transactional shortcuts, or parallel execution until isolation is proven.

## Useful commands

Focused test/domain:

```powershell
python -m pytest tests/<domain-or-file> -q
```

Fast broad development run when slow/migration coverage is unrelated:

```powershell
python -m pytest -m "not slow and not migration" -q
```

Full checkpoint regression:

```powershell
python -m pytest -q
```

After moving/reorganizing tests:

```powershell
python -m pytest --collect-only -q
```

Performance investigation when needed:

```powershell
python -m pytest -q --durations=30
```
