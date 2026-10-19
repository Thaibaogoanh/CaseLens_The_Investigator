def obj(**properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def arr(item):
    return {"type": "array", "items": item}


STR = {"type": "string"}
EVIDENCE = arr(obj(source_id=STR, quote=STR))
CLAIM = obj(title=STR, statement=STR,
            kind={"type": "string", "enum": ["confirmed", "inference", "conflict", "unknown"]},
            evidence=EVIDENCE)
REPORT_SCHEMA = obj(
    summary=CLAIM,
    timeline=arr(obj(occurred_at=STR, title=STR, statement=STR, actor=STR, evidence=EVIDENCE)),
    commitments=arr(obj(owner=STR, promise=STR, due=STR,
                        status={"type": "string", "enum": ["open", "fulfilled", "changed", "not_verified", "overdue"]},
                        condition=STR,
                        condition_status={"type": "string", "enum": ["not_stated", "met", "not_met", "unknown"]},
                        status_reason=STR, evidence=EVIDENCE)),
    findings=arr(CLAIM),
    next_actions=arr(STR),
)
ANSWER_SCHEMA = CLAIM

REVIEW_SCHEMA = obj(
    assessments=arr(obj(claim_id=STR,
                        verdict={"type": "string", "enum": ["supported", "partial", "unsupported", "uncertain"]},
                        explanation=STR, evidence=EVIDENCE)),
    missing_context=arr(STR),
)
