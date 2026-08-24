"""The AusMT portal profile. The station-detail path is AusMT's published convention
(documented at the portal's API reference), not an MTCAT rule."""
from __future__ import annotations

from . import Profile


class AusmtProfile(Profile):
    name = "ausmt"

    def handoff_url(self, catalog_url: str, station_row: dict, level: str):
        """AusMT's measured hand-off route (/go/ts/<survey>/<station>/<level>): a 302 to the
        archive, 404 for anything the portal suppressed. Portal convention, not MTCAT."""
        sid = station_row.get("station_id", "")
        survey = station_row.get("survey_id", "")
        prefix = f"au.{survey}."
        if not (sid.startswith(prefix) and level):
            return None
        origin = catalog_url.split("/data/")[0] if "/data/" in catalog_url else None
        if origin is None or not origin.startswith(("http://", "https://")):
            return None
        return f"{origin}/go/ts/{survey}/{sid[len(prefix):]}/{level}"

    def station_detail_url(self, catalog_url: str, station_row: dict):
        base = catalog_url.rsplit("/", 1)[0]
        sid = station_row.get("station_id", "")
        survey = station_row.get("survey_id", "")
        # au.<survey_id>.<station> is AusMT's id shape; the station segment is what remains
        # after the catalogue's own survey_id prefix. Nothing else is parsed out of the id.
        prefix = f"au.{survey}."
        if not sid.startswith(prefix):
            return None
        return f"{base}/products/{survey}/{sid[len(prefix):]}/station.json"
