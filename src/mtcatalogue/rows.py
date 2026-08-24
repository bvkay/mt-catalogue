"""Thin wrappers over catalogue documents. The raw dict is the record; wrappers only add
access methods, so unknown keys survive round trips."""
from __future__ import annotations


class Row:
    def __init__(self, raw: dict):
        self.raw = raw

    def __getattr__(self, name):
        try:
            return self.raw[name]
        except KeyError:
            raise AttributeError(name) from None

    def get(self, name, default=None):
        return self.raw.get(name, default)

    def __repr__(self):
        ident = self.raw.get("station_id") or self.raw.get("survey_id") or self.raw.get("id", "?")
        return f"<{type(self).__name__} {ident}>"


class Survey(Row):
    pass


class StationRow(Row):
    """One mtcat stations[] row. detail() needs a portal profile: MTCAT declares no
    station-detail route, so without a profile there is no URL to fetch."""

    def __init__(self, raw: dict, catalog):
        super().__init__(raw)
        self._catalog = catalog

    def detail(self):
        url = self._catalog._detail_url(self.raw)
        if url is None:
            return None
        # A local catalogue may be a partial mirror, so a missing sibling file returns None.
        # Over http the fetch stays strict and failures raise.
        if not url.startswith(("http://", "https://")):
            from pathlib import Path
            if not Path(url).exists():
                return None
        return StationDetail(self._catalog._fetch_json(url), self._catalog)


class StationDetail(Row):
    """A station.json document. A withheld record is rendered as the stub it is."""

    def __init__(self, raw: dict, catalog=None):
        super().__init__(raw)
        self._catalog = catalog

    @property
    def withheld(self) -> bool:
        return self.raw.get("withheld") is True

    def resources(self, kind=None):
        rows = [Row(r) for r in self.raw.get("resources", [])]
        return [r for r in rows if kind is None or r.get("kind") == kind]

    def routes(self):
        """Resolvable download URLs from DECLARED fields only (access_url today). No URL is
        ever synthesised from a path convention."""
        return [{"url": r.get("access_url"), "kind": r.get("kind"),
                 "processing_level": r.get("processing_level")}
                for r in self.raw.get("resources", []) if r.get("access_url")]
