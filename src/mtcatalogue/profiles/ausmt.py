"""The AusMT portal profile. The station-detail path is AusMT's published convention
(documented at the portal's API reference), not an MTCAT rule."""
from __future__ import annotations

from . import Profile


class AusmtProfile(Profile):
    name = "ausmt"

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
