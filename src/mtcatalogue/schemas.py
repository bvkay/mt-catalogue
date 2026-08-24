"""Schema fetch and advisory validation. Validation never blocks: a document from a newer
minor version must load, so problems are reported, not raised."""
from __future__ import annotations

_cache: dict = {}


def fetch(url: str, fetch_json) -> dict:
    if url not in _cache:
        _cache[url] = fetch_json(url)
    return _cache[url]


def problems(doc: dict, schema: dict) -> list:
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema is not installed; validation skipped"]
    v = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'/'.join(str(p) for p in e.path)}: {e.message}" for e in v.iter_errors(doc)]
