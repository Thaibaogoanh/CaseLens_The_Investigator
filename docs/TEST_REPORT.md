# Verification — CaseLens 2.3.0

## Recorded checks

- 74 backend tests passed on local Python 3.12.
- Four authored replay scenarios passed, including the corrected Cedar state.
  Full outputs: sample-evaluation.json. These are not real-model benchmarks.
- 22 DOM integration checks passed. They cover case navigation, provenance highlights, versions, imports,
  exports, notes, exclusion, restore and personal-key controls.
- JavaScript syntax checked for app.js and extensions.js.

New regressions verify Atlas delivery overdue + prerequisite not_met, Beacon
explicit post-deadline incompletion, Cedar missing receipt remaining unknown,
invalid prerequisite states, legacy import preservation and reviewer visibility
of prerequisite/rationale plus recommendation premises.

Other tests cover real local HTTP routing and limits, exact quotes, scoped
sources, transport request shapes, provider errors/refusals, client disconnects,
request-scoped credential isolation, disabled server fallback and visitor cache
bypass. Provider transports are mocked: no real key used by the test suite.

## Material limits

The user successfully ran Live Gemini Atlas and AI Review on v2.1.1 and shared
outputs in chat. This is user-observed integration evidence, not a saved,
independently reproduced benchmark. The new 2.3 prompts/schema require a fresh
live run and manual interpretation review before submission.

Earlier v2.0 isolated Chromium testing passed 15 desktop/mobile paths. That is
not a native-browser rerun of 2.3. Windows/Python3.14, cross-browser behavior,
screen-reader acceptance, Docker build, actual Render deployment and GitHub CI
execution have not been verified in this environment. Run the deployment
checklist against the real public URL.

Prompt constraints reduce opportunities for causal overstatement but do not
prove model correctness. Exact-quote validation proves the quoted text is in
the supplied source, not that the source is true or its interpretation sound.
