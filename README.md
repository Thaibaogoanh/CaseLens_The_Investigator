# CaseLens — The Investigator

Evidence-first investigation of customer escalations across tickets, emails and
chat. Built for Anduin Hackathon 2026, Customer Success / The Investigator.

**Version 2.3.0.** Live app: add your deployed URL here before submitting.

## Experience the core workflow

1. Run a case in **Sample replay** without an API key, or select **Live AI**.
2. Open any citation to inspect its exact source quote.
3. In Cedar, add the correction email and investigate again. Compare Versions.
4. Use Evidence map to exclude a source and test which conclusion changes.
5. Review interpretations with a second AI pass and record a separate human note.
6. Save the case file or export Markdown / a printable HTML brief.

Atlas separates an observed missed target from an unmet prerequisite. Beacon
shows why a Done ticket does not establish customer recovery. Cedar preserves
uncertainty until delivery evidence appears. All records are fictional.

## Run locally

Requires Python 3.11+. No runtime packages, database or Node.js are required.

```bash
python server.py
```

Open http://127.0.0.1:8000. On Windows, double-click `start_windows.bat`.
See [START_HERE_VI.md](START_HERE_VI.md) for Vietnamese setup and GitHub steps.

For Live AI, use **API settings** to provide your own Gemini or OpenAI key/model.
The key lives in tab memory and is forwarded through this server for AI requests.
It is not placed in saved case files or browser storage. Use a trusted HTTPS
host or localhost. Reload or Clear my key removes it. Visitor reports bypass
server caching; call limits remain shared across visitors.

For optional server credentials, copy `.env.example` to `.env`, configure the
provider/key/model, and restart. `ALLOW_SERVER_AI=false` disables server-key
fallback and requires a visitor key. Never commit `.env`.

## What is implemented

- Scoped JSON, CSV and plain-text EML imports; source editing by adding records.
- Structured report, chronology, ownership, commitments, unknowns and conflicts.
- Separate delivery status, prerequisite assessment and supporting explanation.
- Exact-quote/source checks after generation; citations open the original body.
- Evidence matrix, exclusion experiments, ten report snapshots per project.
- Per-claim AI review including the factual premises of recommendations.
- Manual review notes; save/restore with origin marked unverified on import.
- OpenAI Responses or Gemini generateContent; personal or server credentials.

Causality instructions prohibit turning chronology into proof. Explicit causal
attributions must remain attributed; unproven causal ideas must be labeled as
inference. This is a model instruction and review process, not a truth guarantee.

## Repository map

| Path | Purpose |
| --- | --- |
| `server.py` | HTTP routes, bounded input, origin checks, request credential context |
| `app/engine.py` | Provider calls, prompts, validation orchestration and bounded cache |
| `app/schema.py`, `validation.py` | Output contract, project and citation validation |
| `app/fixtures.py` | Synthetic sources and exact-input authored replays |
| `app/analysis.py`, `intake.py` | Claim/source map, diagnostics and import adapters |
| `static/` | Two JS modules, one CSS file, HTML and SVG icon |
| `tests/`, `scripts/` | Backend tests, optional UI checks, evaluation, preflight |
| `examples/` | Importable JSON, CSV and email examples |
| `docs/` | Architecture, deployment, demo, evaluation and submission |
| `Dockerfile`, `render.yaml` | Reproducible deployment configuration |

## Verify

```bash
python -m unittest discover -s tests -v
python scripts/evaluate.py --mode sample
python scripts/preflight.py
```

Optional Node.js development checks: `npm ci` then `npm test`.
For native Chromium checks: install `playwright@1.51.1` without saving, run
`npx playwright install chromium`, then `node scripts/browser_test.cjs`.

Live evaluation may consume provider quota or money:

```bash
python scripts/evaluate.py --mode live --stress --review --output artifacts/live-evaluation.json
```

Up to 16 provider attempts, normally fewer due to cache. Inspect the saved
answers manually. Four authored scenarios are not an overall accuracy benchmark.
See [verification](docs/TEST_REPORT.md) for executed checks and limitations.

## Deploy and submit

Use a Render **Docker Web Service**, not a static site. Follow
[DEPLOY_VI.md](docs/DEPLOY_VI.md). The Blueprint defaults to a Free service with
server AI disabled; visitors supply keys. A non-Free instance avoids Free
spin-down for judging, subject to the plan you select in Render.

Submit the public live URL and full public GitHub source. See
[SUBMISSION.md](docs/SUBMISSION.md) for the public brief, rubric mapping and
submission text; replace all URL placeholders before submitting.

## Scope and limitations

This is a synthetic-data hackathon application, not a production customer-data
system. No authenticated accounts, persistent database, mail/ticket connectors
or verified user approvals. The provider receives sources on live calls; its
data terms apply. Portable exports contain source data and should be handled
accordingly. Reports/notes stay in tab memory until exported.

One process: 2 simultaneous AI calls, 50 attempts per UTC day by default,
15 POSTs/minute per observed IP, 60 sources, up to 250 KB normal request bodies
and 500 KB for review/inspect. Restarts reset process limits/cache. Reverse-proxy
clients may share an IP bucket. Use provider billing controls for money limits.

# CaseLens_The_Investigator
