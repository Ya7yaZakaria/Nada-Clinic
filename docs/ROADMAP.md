# Roadmap

## Current operating mode

Nada Clinic is in personal-trial and refinement mode. New stages should not start automatically. Real clinic workflow feedback and verified defects should drive the next implementation work.

## Near-term engineering priorities

1. Continue real personal trial of Patients, Today Clinic, Visit, prescription, investigations, documents, ultrasound, surgery, partner, finance, settings, and printing workflows.
2. Fix verified workflow friction with the smallest safe change.
3. Keep test runtime disciplined using the canonical test architecture in `docs/TESTING.md`.
4. Consider database test-lifecycle optimization only domain-by-domain after isolation proof.
5. Consider parallel pytest execution only after SQLite/filesystem/config isolation is proven.
6. Development-only user impersonation may be planned separately if still desired; it must not silently combine with Development Role Preview and must remain disabled/protected outside development.
7. Do not start a new major product stage until the personal-trial findings justify it.

## Deferred ideas

Historical planning contains additional future ideas. They are preserved in `docs/history/LEGACY_ROADMAP.md` and must be revalidated against current source and current priorities before implementation.
