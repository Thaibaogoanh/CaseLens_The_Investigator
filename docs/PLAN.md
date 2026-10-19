# Delivery plan — 17–19 October 2026

Scope: public Investigator challenge; private portal requirements still need
comparison. Goal: a small live application judges can test with verifiable
evidence and an actually working AI path.

## Implemented in this package

- Browser workspace, three fictional cases, source inspection and search.
- Authored sample replay with exact-input matching and clear labeling.
- Live Responses integration with a strict schema and server-side API key.
- Timeline, commitments, findings, unknowns, recommended next steps.
- New-evidence correction, JSON/CSV/EML import, Markdown/HTML export and live Q&A.
- Optional claim-by-claim semantic AI review; human reviewer notes.
- Evidence map, scope experiments, version comparison and portable case files.
- Automated backend/HTTP tests, Docker configuration and setup documentation.

## Remaining before submission

| Priority | Task | Definition of done |
| --- | --- | --- |
| P0 | Compare full portal brief | Mandatory private requirements mapped to implementation |
| P0 | Configure API access | Real request succeeds; no keys in repository |
| P0 | Real AI evaluation | Four scenario checks run; inspect semantic quality manually |
| P0 | Browser acceptance | Desktop and mobile checks in QA_CHECKLIST.md completed |
| P0 | Public GitHub repo | Source browsable, README has live URL, CI passes |
| P0 | Live deploy | Fresh browser can investigate with Live AI and inspect evidence |
| P0 | Submit | Repo + app URL present; portal shows submitted |
| P1 | Demo recording | Short backup walkthrough using the real deployed application |
| P2 | Product extensions | Only after P0; avoid extra connectors or role systems now |

## Schedule (Vietnam time)

| Window | Focus |
| --- | --- |
| 17 October evening | Run locally, review source, link repo, configure API |
| 18 October morning | Live evaluations and fixes; compare private challenge brief |
| 18 October afternoon | Deploy; complete browser acceptance; fix important issues |
| 18 October evening | README, submission description, English demo rehearsal |
| 19 October morning | Final live test from a fresh browser; backup recording |
| 19 October before 18:00 | Submit and verify status; retain time for recovery |

## Scoring alignment (official weights)

| Criterion | Weight | Evidence to show |
| --- | ---: | --- |
| Depth | 30% | Conditional promises; conflicting status; evidence-driven correction |
| Architecture | 20% | Bounded analysis + deterministic validation; failure behavior |
| Product quality | 20% | One-click samples; inspectable sources; export; clear mode labels |
| Complexity | 15% | Multi-source chronology and ambiguity rather than more integrations |
| Use of AI | 15% | Live analysis and grounded Q&A; honestly distinguish authored replay |

No expected score is claimed. The current implementation has no authenticated
external connectors, no persistent account system, and no autonomous actions.
