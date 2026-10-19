# Submission content to complete

Replace the two URL placeholders with real, tested links. Only state live AI
readiness after testing it on the deployed application.

**Project name:** CaseLens — The Investigator

**Challenge:** The Investigator / Customer success

**Live application:** [ADD DEPLOYED HTTPS URL]

**Public repository:** [ADD PUBLIC GITHUB REPOSITORY URL]

## Short description

CaseLens reconstructs customer escalations from tickets, email and chat. It
builds a source-linked timeline, tracks conditional commitments, surfaces
conflicting accounts and preserves uncertainty when evidence is missing.

Reviewers can inspect exact source quotations, compare investigation versions,
exclude a source to test dependence on evidence, and record their own decisions.
An optional second AI pass evaluates each claim's support. Portable case files
and printable briefs make investigations reproducible and easy to hand over.

## How to try

Open the live application and follow the three-minute judge walkthrough. Begin
with Cedar: investigate before and after the correction email, compare Versions,
then inspect Evidence map. Use Live AI to analyze fresh inputs and ask follow-up
questions once the deployment's API access has been verified.

## Technical notes

Python backend and a dependency-free browser UI. Model output is constrained by
a strict JSON schema and separately checked for project scope and exact quote
provenance. Semantic review is advisory. Demo records and replay reports are
clearly labeled; authored replay is never presented as a live model result.

## Validation statement to complete

Backend/HTTP and interface checks are documented in TEST_REPORT.md. Add the
date, model, live scenario results and any known failures from your own deployed
evaluation. No overall accuracy percentage is claimed from a small synthetic set.
