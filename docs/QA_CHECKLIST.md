# Browser acceptance checklist

Local isolated Chromium checks are marked below where actually tested.
Repeat against your deployed URL and target browsers. Live AI and semantic
quality remain unverified without API credentials.

- [x] Open app in a fresh browser; all styles load without external CDN access.
- [x] On desktop, case list, report and source panel are legible without overlap.
- [x] At 390px width, controls and report are usable without page-wide overflow.
- [ ] Keyboard tab order reaches controls; focus indicators are visible.
- [x] Atlas sample: report, timeline and commitments open.
- [x] Citation opens correct source and highlights the exact quote.
- [ ] Search and email/ticket/chat filters work, including no-result state.
- [ ] Beacon report distinguishes Done from actual client recovery.
- [x] Cedar before correction is unknown; after correction is fulfilled.
- [ ] Previous client question remains in the corrected timeline.
- [x] Export downloads a Markdown brief for the current evidence set.
- [x] Import examples/custom-project.json; records stay in the selected project.
- [ ] Modified/imported sources cannot use a built-in replay report.
- [x] Missing API key gives a useful message; no false live-AI label appears.
- [ ] Live AI succeeds with configured key; inspect interpretation and citations.
- [ ] Live follow-up answers a question; unsupported facts are marked unknown.
- [ ] Case switching and imports are blocked during an in-flight operation.
- [ ] Reload clears imported workspace data as documented.
- [ ] Deployed /health returns status ok; repo and app are accessible to judges.

## Version 2 acceptance

- [x] Evidence map renders claim-to-source relationships.
- [x] New correction creates a comparable version with one added source.
- [x] Excluding correction returns the authored case to unknown.
- [x] Excluded source can be restored through Evidence room.
- [x] Human review notes are retained in the case file and brief.
- [x] Native case-file download and restore succeeds.
- [x] Imported reports are labeled origin-unverified.
- [x] Printable HTML download contains source material.
- [x] Judge walkthrough opens/closes and selects Cedar.
- [ ] Live semantic review completes with a real provider key.
- [ ] Keyboard-only and screen-reader assessment on the deployed app.
