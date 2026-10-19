"""Input boundaries and mechanically verifiable evidence checks.

Exact quotes prove provenance, not that the model's interpretation is correct.
"""
import hashlib
import json
import re
from datetime import datetime


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def text(value, label, maximum=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise AppError(f"{label} must be non-empty text, at most {maximum} characters.")
    return value


def timestamp(value):
    text(value, "Timestamp", 50)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed
    except ValueError:
        raise AppError("Timestamps must be ISO 8601 with a timezone, e.g. 2026-10-15T09:00:00Z.")


def validate_project(payload):
    if not isinstance(payload, dict):
        raise AppError("Expected a JSON object.")
    project = payload.get("project")
    sources = payload.get("sources")
    if not isinstance(project, dict):
        raise AppError("A project object is required.")
    project = {key: text(project.get(key), f"project.{key}", 200)
               for key in ("id", "title", "customer")}
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", project["id"]):
        raise AppError("Project ID must use letters, numbers, underscores or hyphens.")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 60:
        raise AppError("Provide between 1 and 60 sources.")
    clean, ids = [], set()
    for item in sources:
        if not isinstance(item, dict):
            raise AppError("Every source must be an object.")
        row = {key: text(item.get(key), f"source.{key}", maximum)
               for key, maximum in (("id", 80), ("project_id", 80), ("kind", 20),
                                    ("author", 200), ("sent_at", 50), ("title", 300), ("body", 12000))}
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", row["id"]):
            raise AppError("Source IDs must use letters, numbers, underscores or hyphens.")
        if row["id"] in ids:
            raise AppError("Duplicate source IDs are not allowed.")
        ids.add(row["id"])
        if row["project_id"] != project["id"]:
            raise AppError("Every source must belong to the selected project. Mixed projects are rejected.")
        if row["kind"] not in ("email", "ticket", "chat"):
            raise AppError("Source kind must be email, ticket or chat.")
        timestamp(row["sent_at"])
        clean.append(row)
    if sum(len(s["body"]) for s in clean) > 80000:
        raise AppError("Combined source text exceeds 80,000 characters.")
    clean.sort(key=lambda s: (timestamp(s["sent_at"]), s["id"]))
    return project, clean


def fingerprint(project, sources):
    return hashlib.sha256(json.dumps({"project": project, "sources": sorted(sources, key=lambda s: s["id"])},
                                     sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def check_schema(value, schema, path="result"):
    """Validate the small JSON Schema subset used by our provider contract."""
    kind = schema.get("type")
    valid = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str)}.get(kind, False)
    if not valid:
        raise AppError(f"Invalid AI output at {path}: expected {kind}.", 502)
    if "enum" in schema and value not in schema["enum"]:
        raise AppError(f"Invalid AI output at {path}: unexpected value.", 502)
    if kind == "string" and (not value.strip() or len(value) > 5000):
        raise AppError(f"Invalid AI text at {path}.", 502)
    if kind == "object":
        props = schema["properties"]
        if set(value) != set(props):
            raise AppError(f"Invalid AI fields at {path}.", 502)
        for key, sub in props.items():
            check_schema(value[key], sub, f"{path}.{key}")
    if kind == "array":
        if len(value) > 80:
            raise AppError("AI output contains too many items.", 502)
        for i, item in enumerate(value):
            check_schema(item, schema["items"], f"{path}[{i}]")


def validate_evidence(record, sources):
    refs = record["evidence"]
    if not refs and record.get("kind") != "unknown":
        raise AppError("AI returned a claim without evidence. No report was accepted.", 502)
    source_map = {s["id"]: s for s in sources}
    for ref in refs:
        source = source_map.get(ref["source_id"])
        if not source or ref["quote"] not in source["body"]:
            raise AppError("AI returned an unverifiable quotation. No report was accepted.", 502)
    return len(refs)
