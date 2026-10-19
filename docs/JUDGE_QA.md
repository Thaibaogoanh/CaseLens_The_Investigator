# Questions to rehearse

## What is the core customer problem?

A customer escalation requires reconstructing events, commitments and current
uncertainty from fragmented records. CaseLens makes the reconstruction inspectable
and records how the conclusion changes as new evidence arrives.

## What actually uses AI?

Live investigation creates a structured report from the selected project sources.
Live Q&A answers a new question. Optional Review uses a separate model call to
assess each claim against sources. Sample replay is explicitly authored and makes
no model call. Diagnostics, provenance checks, timelines, maps, diffs, exports and
case-file validation are deterministic application code.

## Why is this more than a summary?

Demonstrate conditional commitments, event versus send time, conflicting status,
unknowns, source inspection, source exclusion, preserved versions and reviewer
decisions. Explain their effect on the CS user's next action.

## How do you prevent hallucinations?

We constrain output structure, limit context to a selected project, require exact
quotes, reject invalid references and distinguish unknown/inferred claims. We
add optional semantic review and human notes. These measures reduce certain
failure modes but do not guarantee that every interpretation is correct.

## Is the second reviewer independent?

It is a separate pass, not necessarily a different model. OPENAI_REVIEW_MODEL
can select another supported model. Models can share errors; the review is
advisory and does not authenticate facts or replace a human decision.

## Why count uncited sources?

It makes potential omissions visible. A report can correctly omit irrelevant
records, so coverage is not accuracy. Repeated text across channels is explicitly
flagged and must not be treated as independent corroboration.

## Why retain versions?

An investigation needs a record of what was known at the time. A later correction
can change an answer without erasing the earlier question. Comparing snapshots
lets a reviewer inspect the exact source set used for each conclusion.

## Does exclusion prove causality?

No. It measures dependence on the selected evidence context. It helps find a
fragile claim or a key receipt, but it is not a causal experiment on the actual
customer incident.

## What happens if a user edits a saved JSON file?

On restore, schema and quotations are checked again. The resulting report is
labeled imported/origin-unverified. We discard previous AI reviews. Exact quote
validation still cannot authenticate the original record or reviewer identity.

## What are the main limits?

This demo uses bounded context and fictional records, a stateless server with
an in-memory cache, and local portable case files. It has no real connectors,
authenticated tenant accounts, durable central history or production audit
identity. EML parsing supports text/plain, not HTML extraction or attachments.

## What have you measured?

Show the supplied verification report and, after you run it, your actual live
evaluation output. Separate backend tests, DOM checks, browser acceptance and
model quality. Do not infer live accuracy from passing authored sample tests.

## What would you build next?

Start with an authenticated read-only connector and tenant authorization, then
durable version storage and representative escalation evaluations. Add chunked
retrieval only when source volume requires it, measuring missed-context risk.

## How would you evaluate business value?

Measure time to an accurate, reviewed investigation and whether the next action
is correct. Include human verification time, model latency and corrections.
Compare representative cases with a manual baseline and disclose sample size.
