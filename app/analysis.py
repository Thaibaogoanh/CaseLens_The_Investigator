"""Deterministic evidence relationships and input diagnostics, not AI confidence."""
import hashlib
from collections import Counter
from .validation import timestamp


def claims_from_report(report):
    claims = [dict(id='summary', section='summary', title=report['summary']['title'],
                   statement=report['summary']['statement'], kind=report['summary']['kind'],
                   evidence=report['summary']['evidence'])]
    for section in ('timeline', 'commitments', 'findings'):
        for index, record in enumerate(report[section]):
            if section == 'commitments':
                title = record['promise']
                statement = f"Owner: {record['owner']}. Promise: {record['promise']}. Due: {record['due']}. Status: {record['status']}. Condition: {record.get('condition', 'Not assessed')}. Prerequisite: {record.get('condition_status', 'unknown')}. Rationale: {record.get('status_reason', 'Not assessed')}."
            elif section == 'timeline':
                title = record['title']
                statement = f"Event time: {record['occurred_at']}. Actor: {record['actor']}. {record['statement']}"
            else:
                title, statement = record['title'], record['statement']
            claims.append(dict(id=f'{section}-{index}', section=section, title=title,
                               statement=statement, kind=record.get('kind', record.get('status', 'event')),
                               evidence=record['evidence']))
    for index, action in enumerate(report.get('next_actions', [])):
        claims.append(dict(id=f'next_actions-{index}', section='next_actions',
            title='Recommended action', statement=action, kind='recommendation', evidence=[]))
    return claims


def input_diagnostics(sources):
    by_body = {}
    for source in sources:
        normalized = ' '.join(source['body'].casefold().split())
        by_body.setdefault(hashlib.sha256(normalized.encode()).hexdigest(), []).append(source['id'])
    duplicates = [ids for ids in by_body.values() if len(ids) > 1]
    return dict(source_count=len(sources), channels=dict(Counter(s['kind'] for s in sources)),
                authors=sorted(set(s['author'] for s in sources)), duplicate_body_groups=duplicates,
                first_sent_at=min(sources, key=lambda s: timestamp(s['sent_at']))['sent_at'],
                last_sent_at=max(sources, key=lambda s: timestamp(s['sent_at']))['sent_at'],
                body_characters=sum(len(s['body']) for s in sources))


def evidence_analysis(report, sources):
    claims = claims_from_report(report)
    links = {s['id']: [] for s in sources}
    single_source = []
    for claim in claims:
        cited = set(ref['source_id'] for ref in claim['evidence'])
        for sid in cited:
            links[sid].append(claim['id'])
        if len(cited) == 1:
            single_source.append(claim['id'])
    return dict(claims=claims,
                sources=[dict(source_id=s['id'], kind=s['kind'], title=s['title'],
                              claim_ids=links[s['id']], claim_count=len(links[s['id']])) for s in sources],
                cited_source_count=sum(bool(ids) for ids in links.values()),
                uncited_source_ids=[sid for sid, ids in links.items() if not ids],
                single_source_claim_ids=single_source,
                diagnostics=input_diagnostics(sources),
                note='Citation coverage and dependency counts are descriptive. They do not measure accuracy, importance or independent corroboration.')
