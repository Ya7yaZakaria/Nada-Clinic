# Visual Acceptance Checklist

Use only the rows relevant to the accepted scope.

## Evidence-locked automation design
- [ ] Current `AGENTS.md` and freshest affected source re-read
- [ ] Every planned click/assertion mapped to current-source evidence
- [ ] Authentication controls/redirect verified from source
- [ ] Required role/permission/feature flag verified
- [ ] Visibility/state gates verified
- [ ] Required fixture/data shape verified
- [ ] Route/endpoint/method/parameters verified
- [ ] Selector exists and is unique/stable in current source/runtime
- [ ] Async/modal/drawer mounting lifecycle verified
- [ ] Expected response/redirect/DOM state verified
- [ ] Deterministic isolated fixture created when state is required
- [ ] Fixture prerequisites programmatically asserted before browser run
- [ ] Acceptance-critical endpoints/state preflighted when practical
- [ ] Verifier compiles/parses and source-contract checks pass before delivery
- [ ] No obsolete credentials/environment assumptions remain

## Browser
- [ ] Real application started successfully
- [ ] Correct source/checkpoint verified
- [ ] Correct route opened
- [ ] Required role authenticated
- [ ] Synthetic/disposable data used where actions mutate state

## Functional
- [ ] Primary workflow succeeds
- [ ] Validation behavior checked when relevant
- [ ] Modal/drawer lifecycle works
- [ ] HTMX/AJAX target updates correctly
- [ ] No unintended navigation
- [ ] Required fallback works when in scope

## Browser errors
- [ ] No unresolved page errors
- [ ] No unresolved console errors
- [ ] No critical failed network requests

## Responsive
- [ ] Desktop
- [ ] Tablet when required
- [ ] Mobile
- [ ] No unintended horizontal overflow
- [ ] No clipping/overlap
- [ ] Primary actions remain reachable

## Accessibility / keyboard
- [ ] Logical Tab order where relevant
- [ ] Visible focus
- [ ] Enter/Space activation
- [ ] Escape closes modal/drawer when required
- [ ] Focus returns after close
- [ ] Controls have accessible names

## Theme / direction
- [ ] Light when required
- [ ] Dark when required
- [ ] LTR when required
- [ ] RTL when required

## Evidence
- [ ] Meaningful screenshots captured
- [ ] Screenshots reviewed
- [ ] No PHI/PII/secrets in evidence
- [ ] Trace retained only on failure/retry
- [ ] No video
- [ ] browser-summary.json written
- [ ] manifest.json references every artifact
