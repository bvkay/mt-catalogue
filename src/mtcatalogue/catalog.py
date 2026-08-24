"""The catalogue reader."""
from __future__ import annotations

import json
from pathlib import Path

from . import profiles, schemas
from .rows import Row, StationRow, Survey


class Catalog:
    """One MTCAT document. `source` is an http(s) URL or a local path (local paths make tests
    and offline work first-class). `profile` selects a portal profile by name or instance;
    None is pure-spec mode."""

    def __init__(self, source: str, profile=None, session=None):
        self.source = str(source)
        self._session = session
        self._profile = profiles.load(profile)
        self.raw = self._fetch_json(self.source)
        self.portal = Row(self.raw.get("portal", {}))

    # -- fetching -------------------------------------------------------------

    def _fetch_json(self, source: str) -> dict:
        if not source.startswith(("http://", "https://")):
            return json.loads(Path(source).read_text(encoding="utf-8"))
        if self._session is None:
            import requests
            self._session = requests.Session()
        r = self._session.get(source, timeout=60)
        r.raise_for_status()
        return r.json()

    def _detail_url(self, station_row: dict):
        return self._profile.station_detail_url(self.source, station_row)

    # -- views ----------------------------------------------------------------

    def surveys(self, **filters) -> list:
        return [Survey(s) for s in self.raw.get("surveys", []) if _match(s, filters)]

    def stations(self, **filters) -> list:
        return [StationRow(s, self) for s in self.raw.get("stations", []) if _match(s, filters)]

    def station(self, station_id: str):
        for s in self.raw.get("stations", []):
            if s.get("station_id") == station_id:
                return StationRow(s, self)
        return None

    # -- validation (advisory) ------------------------------------------------

    def problems(self, schema=None) -> list:
        """Validation problems against the schema. `schema` is a dict, a path, or None to
        resolve the document's own declared portal.schema_url (relative to the source)."""
        if schema is None:
            declared = self.raw.get("portal", {}).get("schema_url")
            if not declared:
                return ["portal.schema_url is not declared; pass a schema to validate"]
            if not declared.startswith(("http://", "https://")):
                declared = self.source.rsplit("/", 1)[0] + "/" + declared
            schema = schemas.fetch(declared, self._fetch_json)
        elif not isinstance(schema, dict):
            schema = json.loads(Path(schema).read_text(encoding="utf-8"))
        return schemas.problems(self.raw, schema)


def _match(row: dict, filters: dict) -> bool:
    return all(row.get(k) == v for k, v in filters.items())
