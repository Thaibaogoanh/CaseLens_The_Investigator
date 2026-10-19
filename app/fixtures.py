"""Fictional cases and explicitly curated replay reports. No AI is simulated."""
from copy import deepcopy


def source(project, sid, kind, author, date, title, body):
    return dict(id=sid, project_id=project, kind=kind, author=author, sent_at=date, title=title, body=body)


def ref(sid, quote):
    return dict(source_id=sid, quote=quote)


def claim(title, statement, kind, *refs):
    return dict(title=title, statement=statement, kind=kind, evidence=list(refs))


def event(at, title, statement, actor, *refs):
    return dict(occurred_at=at, title=title, statement=statement, actor=actor, evidence=list(refs))


def commitment(owner, promise, due, status, *refs):
    return dict(owner=owner, promise=promise, due=due, status=status, condition="Not stated", condition_status="not_stated",
                status_reason="Completion has not been verified from the available records.", evidence=list(refs))


ATLAS = [
    source("atlas", "ATL-E01", "email", "Maya Chen · Customer Success", "2026-10-12T09:00:00Z", "Confirmed onboarding date", "We confirm that Atlas investor onboarding will go live by 17:00 UTC on 16 October. I am the delivery owner. This commitment assumes the signed mapping arrives by 14 October."),
    source("atlas", "ATL-T01", "ticket", "Leo Park · Engineering", "2026-10-13T11:00:00Z", "ATL-142: Mapping dependency", "ATL-142 is blocked. The signed investor-field mapping has not arrived. Engineering cannot finalize the import until it is received."),
    source("atlas", "ATL-C01", "chat", "Maya Chen · Customer Success", "2026-10-14T16:00:00Z", "#atlas-launch", "The signed mapping is still missing at 16:00 UTC on 14 October. I will request a revised launch date from the client; no new date is approved yet."),
    source("atlas", "ATL-E02", "email", "Nora Diaz · Atlas client", "2026-10-15T09:00:00Z", "Signed mapping attached", "We delivered the signed mapping at 08:45 UTC today, 15 October. We still expect the Friday launch unless you confirm otherwise."),
    source("atlas", "ATL-T02", "ticket", "Leo Park · Engineering", "2026-10-15T14:00:00Z", "ATL-142: Import built; QA pending", "The mapping was received at 08:45 UTC on 15 October. Import implementation is complete. End-to-end QA and client acceptance are still pending."),
    source("atlas", "ATL-C02", "chat", "Maya Chen · Customer Success", "2026-10-16T15:00:00Z", "#atlas-launch: Unapproved revised date", "Engineering proposes 19 October for launch. This is a proposal only; the client has not approved it. Do not treat it as a replacement commitment."),
    source("atlas", "ATL-E03", "email", "Nora Diaz · Atlas client", "2026-10-16T18:00:00Z", "Escalation: onboarding unavailable", "It is now 18:00 UTC on 16 October and investor onboarding is unavailable. You confirmed 17:00 UTC today. Please explain what happened and who owns the recovery."),
]
ATLAS_REPORT = dict(
    summary=claim("A launch commitment remains unresolved", "Maya confirmed a conditional 16 October launch. The mapping arrived after the stated prerequisite date, a revised date was proposed but not approved, and the client reported onboarding unavailable after the committed time.", "confirmed",
                  ref("ATL-E01", "This commitment assumes the signed mapping arrives by 14 October."), ref("ATL-E02", "We delivered the signed mapping at 08:45 UTC today, 15 October."), ref("ATL-C02", "This is a proposal only; the client has not approved it."), ref("ATL-E03", "It is now 18:00 UTC on 16 October and investor onboarding is unavailable.")),
    timeline=[
        event("2026-10-12T09:00:00Z", "Launch commitment recorded", "Conditional go-live confirmed for 16 October, 17:00 UTC.", "Maya Chen", ref("ATL-E01", "We confirm that Atlas investor onboarding will go live by 17:00 UTC on 16 October.")),
        event("2026-10-13T11:00:00Z", "Dependency blocks engineering", "Signed mapping is required before import can be finalized.", "Leo Park", ref("ATL-T01", "Engineering cannot finalize the import until it is received.")),
        event("2026-10-14T16:00:00Z", "Prerequisite still missing", "Customer Success plans to request a new date, without approval.", "Maya Chen", ref("ATL-C01", "I will request a revised launch date from the client; no new date is approved yet.")),
        event("2026-10-15T08:45:00Z", "Mapping received", "Event occurred at 08:45; reported by the client's 09:00 email and later ticket.", "Nora Diaz", ref("ATL-E02", "We delivered the signed mapping at 08:45 UTC today, 15 October.")),
        event("2026-10-15T14:00:00Z", "Implementation complete; acceptance pending", "Engineering completion does not establish launch readiness.", "Leo Park", ref("ATL-T02", "End-to-end QA and client acceptance are still pending.")),
        event("2026-10-16T15:00:00Z", "New date proposed", "19 October is proposed, not an agreed replacement deadline.", "Maya Chen", ref("ATL-C02", "Engineering proposes 19 October for launch. This is a proposal only; the client has not approved it.")),
        event("2026-10-16T18:00:00Z", "Client escalates", "Client reports unavailable onboarding after the promised time.", "Nora Diaz", ref("ATL-E03", "It is now 18:00 UTC on 16 October and investor onboarding is unavailable.")),
    ],
    commitments=[commitment("Maya Chen", "Launch Atlas investor onboarding, conditional on signed mapping by 14 October.", "16 October 2026 · 17:00 UTC", "not_verified", ref("ATL-E01", "We confirm that Atlas investor onboarding will go live by 17:00 UTC on 16 October. I am the delivery owner. This commitment assumes the signed mapping arrives by 14 October."))],
    findings=[claim("The proposed date is not a new agreement", "19 October has not replaced the original commitment because the client has not approved it.", "confirmed", ref("ATL-C02", "Do not treat it as a replacement commitment.")),
              claim("Late mapping is a plausible contributor", "Late input may have compressed delivery time; the messages do not establish a causal link or allocation of responsibility.", "inference", ref("ATL-T01", "Engineering cannot finalize the import until it is received."), ref("ATL-E02", "We delivered the signed mapping at 08:45 UTC today, 15 October.")),
              claim("Current recovery readiness is unknown", "The latest engineering evidence still lists QA and client acceptance as pending. No completed launch or recovery approval is evidenced.", "unknown", ref("ATL-T02", "End-to-end QA and client acceptance are still pending."))],
    next_actions=["Ask Maya to obtain an explicitly approved recovery date from the client.", "Verify end-to-end QA and client acceptance before confirming launch readiness.", "Confirm the critical path with engineering before attributing the delay to one cause."])

ATLAS_REPORT['commitments'][0].update(
    status='overdue', condition='Signed mapping arrives by 14 October.', condition_status='not_met',
    status_reason='The target time passed and the client explicitly reported onboarding unavailable. The mapping prerequisite was not met; this does not establish an unconditional breach or prove the cause of delay.')
ATLAS_REPORT['commitments'][0]['evidence'].extend([
    ref('ATL-E02', 'We delivered the signed mapping at 08:45 UTC today, 15 October.'),
    ref('ATL-E03', 'It is now 18:00 UTC on 16 October and investor onboarding is unavailable.')])

BEACON = [
    source("beacon", "BCN-E01", "email", "Ava Stone · Customer Success", "2026-10-14T08:00:00Z", "Export recovery promise", "I will restore Beacon's complete investor CSV export by 12:00 UTC on 15 October. Complete means all investor rows, not only active investors."),
    source("beacon", "BCN-T01", "ticket", "Sam Roy · Engineering", "2026-10-15T10:00:00Z", "BCN-88: Status changed to Done", "BCN-88 status: Done. CSV endpoint responds with HTTP 200. The automated test checks active investors only; archived investor coverage was not tested."),
    source("beacon", "BCN-C01", "chat", "Ava Stone · Customer Success", "2026-10-15T10:30:00Z", "#beacon-support", "The ticket says Done. I have not yet checked the client's full export and have not received client acceptance."),
    source("beacon", "BCN-E02", "email", "Ben Li · Beacon client", "2026-10-15T13:00:00Z", "Export still incomplete", "Our 12:45 UTC export contains 800 of 1,000 expected investors. All 200 archived investors are missing. Please reopen this incident."),
    source("beacon", "BCN-T02", "ticket", "Sam Roy · Engineering", "2026-10-15T14:00:00Z", "BCN-88: Reopened", "BCN-88 status: Reopened. The archived-investor filter is the confirmed cause of missing rows. Full-export recovery is not complete."),
]
BEACON_REPORT = dict(
    summary=claim("Ticket completion did not mean customer recovery", "The ticket was marked Done after an active-investor-only check. The client later reported 200 missing archived investors, and engineering reopened the incident with the filter identified as the cause.", "confirmed", ref("BCN-T01", "The automated test checks active investors only; archived investor coverage was not tested."), ref("BCN-E02", "All 200 archived investors are missing."), ref("BCN-T02", "The archived-investor filter is the confirmed cause of missing rows.")),
    timeline=[event("2026-10-14T08:00:00Z", "Full export promised", "All investors, including archived rows, are in scope.", "Ava Stone", ref("BCN-E01", "Complete means all investor rows, not only active investors.")),
              event("2026-10-15T10:00:00Z", "Ticket marked Done", "Only active investors were tested.", "Sam Roy", ref("BCN-T01", "BCN-88 status: Done."), ref("BCN-T01", "The automated test checks active investors only; archived investor coverage was not tested.")),
              event("2026-10-15T10:30:00Z", "Acceptance unverified", "Customer Success has not checked the complete output.", "Ava Stone", ref("BCN-C01", "I have not yet checked the client's full export and have not received client acceptance.")),
              event("2026-10-15T12:45:00Z", "Client observes missing rows", "The export observation precedes its 13:00 email report.", "Ben Li", ref("BCN-E02", "Our 12:45 UTC export contains 800 of 1,000 expected investors.")),
              event("2026-10-15T14:00:00Z", "Incident reopened", "Engineering confirms the archived filter as the missing-row cause.", "Sam Roy", ref("BCN-T02", "The archived-investor filter is the confirmed cause of missing rows."))],
    commitments=[commitment("Ava Stone", "Restore complete investor CSV export, including archived investors.", "15 October 2026 · 12:00 UTC", "overdue", ref("BCN-E01", "I will restore Beacon's complete investor CSV export by 12:00 UTC on 15 October."), ref("BCN-T02", "Full-export recovery is not complete."))],
    findings=[claim("Done conflicts with customer impact", "The ticket's Done status was insufficient evidence of full recovery; the client's export was still incomplete afterward.", "conflict", ref("BCN-T01", "BCN-88 status: Done."), ref("BCN-E02", "All 200 archived investors are missing.")),
              claim("A cause is explicitly confirmed", "Engineering identifies the archived-investor filter as the cause of missing rows. This supports a cause statement without inferring one from timing alone.", "confirmed", ref("BCN-T02", "The archived-investor filter is the confirmed cause of missing rows."))],
    next_actions=["Test active and archived investor counts against the expected 1,000 rows.", "Obtain client verification of the complete export before closing BCN-88.", "Ask Ava to communicate an updated recovery commitment."])

BEACON_REPORT['commitments'][0]['status_reason'] = 'The client observed an incomplete export after the 12:00 deadline and engineering later confirmed recovery was not complete.'

CEDAR = [
    source("cedar", "CDR-E01", "email", "Iris Nguyen · Customer Success", "2026-10-13T09:00:00Z", "SFTP delivery commitment", "I will deliver Cedar's first settlement file to SFTP by 18:00 UTC on 14 October. I own the delivery confirmation."),
    source("cedar", "CDR-T01", "ticket", "Owen Tran · Operations", "2026-10-14T17:00:00Z", "CDR-31: File generated", "Settlement file generation completed at 16:50 UTC. SFTP upload confirmation is not attached to this ticket."),
    source("cedar", "CDR-C01", "chat", "Owen Tran · Operations", "2026-10-14T17:10:00Z", "#cedar-ops", "I started the SFTP upload at 17:05 UTC. Waiting for the transfer receipt. File generation alone is not delivery confirmation."),
    source("cedar", "CDR-E02", "email", "Lena Wu · Cedar client", "2026-10-15T08:00:00Z", "Where is the settlement file?", "I cannot find the settlement file in the folder I checked. Did delivery happen before yesterday's 18:00 UTC deadline?"),
]
CEDAR_SUPPLEMENT = source("cedar", "CDR-E03", "email", "Lena Wu · Cedar client", "2026-10-15T10:00:00Z", "Correction: delivery receipt and acceptance", "Correction: I checked the wrong folder. Our SFTP receipt confirms the complete file arrived at 17:22 UTC on 14 October. We accept this delivery as complete and on time.")
CEDAR_REPORT = dict(
    summary=claim("Delivery cannot yet be verified", "The file was generated and an upload started, but neither event proves SFTP delivery. The client asks whether delivery occurred; no transfer receipt is available in this evidence set.", "unknown", ref("CDR-T01", "SFTP upload confirmation is not attached to this ticket."), ref("CDR-C01", "Waiting for the transfer receipt.")),
    timeline=[event("2026-10-13T09:00:00Z", "SFTP delivery promised", "Iris owns confirmation of a delivery due on 14 October.", "Iris Nguyen", ref("CDR-E01", "I will deliver Cedar's first settlement file to SFTP by 18:00 UTC on 14 October.")),
              event("2026-10-14T16:50:00Z", "File generated", "Generation occurred before the 17:00 ticket update.", "Owen Tran", ref("CDR-T01", "Settlement file generation completed at 16:50 UTC.")),
              event("2026-10-14T17:05:00Z", "Upload started", "An initiated transfer is not proof of delivery.", "Owen Tran", ref("CDR-C01", "I started the SFTP upload at 17:05 UTC.")),
              event("2026-10-15T08:00:00Z", "Client requests confirmation", "The client cannot find the file in the folder checked.", "Lena Wu", ref("CDR-E02", "I cannot find the settlement file in the folder I checked."))],
    commitments=[commitment("Iris Nguyen", "Deliver first settlement file to Cedar SFTP and confirm delivery.", "14 October 2026 · 18:00 UTC", "not_verified", ref("CDR-E01", "I own the delivery confirmation."), ref("CDR-C01", "Waiting for the transfer receipt."))],
    findings=[claim("Missing evidence is not proof of failed delivery", "The evidence does not establish whether the upload completed. Calling the delivery late or failed would exceed the available facts.", "unknown", ref("CDR-C01", "File generation alone is not delivery confirmation."))],
    next_actions=["Request the SFTP receipt with destination, completion time and file identity.", "Ask the client to verify the destination folder.", "Update the commitment status only after delivery evidence is available."])
CEDAR_UPDATED = deepcopy(CEDAR_REPORT)
CEDAR_UPDATED["summary"] = claim("New evidence verifies on-time delivery", "The client corrected the folder mistake, confirmed receipt at 17:22 UTC on 14 October and accepted the delivery as complete and on time. This resolves the earlier uncertainty.", "confirmed", ref("CDR-E03", "Our SFTP receipt confirms the complete file arrived at 17:22 UTC on 14 October. We accept this delivery as complete and on time."))
CEDAR_UPDATED["timeline"].extend([
    event("2026-10-14T17:22:00Z", "Delivery completed", "The 15 October correction reports an earlier delivery time; timeline uses the event time.", "Lena Wu", ref("CDR-E03", "Our SFTP receipt confirms the complete file arrived at 17:22 UTC on 14 October.")),
    event("2026-10-15T10:00:00Z", "Client corrects the record", "Client explains the folder mistake and accepts delivery.", "Lena Wu", ref("CDR-E03", "Correction: I checked the wrong folder."), ref("CDR-E03", "We accept this delivery as complete and on time."))])
CEDAR_UPDATED["commitments"][0]["status"] = "fulfilled"
CEDAR_UPDATED["commitments"][0]["status_reason"] = "The receipt and client acceptance establish completion before the deadline."
CEDAR_UPDATED["commitments"][0]["evidence"].append(ref("CDR-E03", "We accept this delivery as complete and on time."))
CEDAR_UPDATED["findings"] = [claim("Conclusion changed because the evidence changed", "The previously unverified delivery is now supported by a client-confirmed receipt. The earlier question is retained in the timeline instead of being erased.", "confirmed", ref("CDR-E02", "Did delivery happen before yesterday's 18:00 UTC deadline?"), ref("CDR-E03", "We accept this delivery as complete and on time."))]
CEDAR_UPDATED["next_actions"] = ["Attach the confirmed SFTP receipt to CDR-31.", "Record the verified folder path in the delivery runbook to prevent a repeat search error."]


def case(pid, title, customer, description, tag, sources, report, question):
    return dict(project=dict(id=pid, title=title, customer=customer), description=description,
                tag=tag, sources=sources, report=report, question=question)


CASES = [
    case("atlas", "The launch that slipped", "Atlas Capital", "A deadline, a late dependency, and a replacement date nobody approved.", "Commitment trail", ATLAS, ATLAS_REPORT, "Who owned the original launch commitment?"),
    case("beacon", "Done is not resolved", "Beacon Partners", "Engineering closed the ticket. The customer's problem continued.", "Conflicting evidence", BEACON, BEACON_REPORT, "Why did Done not establish recovery?"),
    case("cedar", "The missing receipt", "Cedar Ventures", "An uncertain delivery, until one new email changes the investigation.", "Evolving evidence", CEDAR, CEDAR_REPORT, "Can we prove that delivery was late?"),
]


def public_cases():
    rows = []
    for item in CASES:
        row = deepcopy({k: v for k, v in item.items() if k != "report"})
        if item["project"]["id"] == "cedar":
            row["supplement"] = deepcopy(CEDAR_SUPPLEMENT)
        rows.append(row)
    return rows
