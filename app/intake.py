"""Explicit JSON, CSV and plain-text EML adapters; never fetch remote content."""
import csv
import hashlib
import io
import json
from email import policy
from email.parser import Parser
from email.utils import parsedate_to_datetime

from .analysis import input_diagnostics
from .validation import AppError, text, validate_project


def normalize(payload):
    if not isinstance(payload, dict):
        raise AppError('Expected an import object.')
    kind = payload.get('format', 'json')
    content = payload.get('content')
    if kind == 'json':
        if content is not None:
            text(content, 'JSON content', 230000)
            try:
                candidate = json.loads(content)
            except (json.JSONDecodeError, RecursionError):
                raise AppError('The imported file is not valid JSON.')
        else:
            candidate = payload
    elif kind == 'csv':
        text(content, 'CSV content', 230000)
        try:
            reader = csv.DictReader(io.StringIO(content.lstrip('\ufeff')), strict=True)
            required = {'id', 'project_id', 'kind', 'author', 'sent_at', 'title', 'body'}
            if not reader.fieldnames or set(reader.fieldnames) != required or len(reader.fieldnames) != len(required):
                raise AppError('CSV headers must be exactly: id,project_id,kind,author,sent_at,title,body.')
            rows = []
            for row in reader:
                if None in row:
                    raise AppError('A CSV row has extra columns. Quote fields containing commas or line breaks.')
                rows.append(row)
                if len(rows) > 60:
                    raise AppError('CSV imports support at most 60 records.')
            candidate = dict(project=payload.get('project'), sources=rows)
        except csv.Error:
            raise AppError('The CSV cannot be parsed. Check quoting and column counts.')
    elif kind == 'eml':
        text(content, 'Email content', 180000)
        project = payload.get('project')
        if not isinstance(project, dict):
            raise AppError('Project metadata is required for an email import.')
        try:
            message = Parser(policy=policy.default).parsestr(content)
            date = parsedate_to_datetime(str(message.get('Date', '')))
            if date.tzinfo is None:
                raise ValueError('Missing timezone')
            if message.is_multipart():
                part = message.get_body(preferencelist=('plain',))
                if part is None:
                    raise AppError('Only email with a text/plain body is supported. HTML-only mail is not converted.')
            else:
                part = message
            if part.get_content_type() != 'text/plain':
                raise AppError('Only a text/plain email body is supported.')
            body = part.get_content().strip()
            source_id = 'EML-' + hashlib.sha256(content.encode()).hexdigest()[:12]
            row = dict(id=source_id, project_id=project.get('id'), kind='email',
                       author=str(message.get('From', 'Unknown sender')),
                       sent_at=date.isoformat(), title=str(message.get('Subject', 'Untitled email')), body=body)
            candidate = dict(project=project, sources=[row])
        except (ValueError, TypeError, LookupError, UnicodeError):
            raise AppError('The EML needs a readable plain-text body and a valid Date header with timezone.')
    else:
        raise AppError('Import format must be json, csv or eml.')
    project, sources = validate_project(candidate)
    return dict(project=project, sources=sources, diagnostics=input_diagnostics(sources))
