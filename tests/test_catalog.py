import json
from pathlib import Path

from mtcatalogue import Catalog, StationDetail

FIX = Path(__file__).parent / "fixtures"


def _cat(**kw):
    return Catalog(str(FIX / "mtcat-snapshot.json"), **kw)


def test_reads_the_live_snapshot():
    cat = _cat()
    assert cat.portal.portal_id == "ausmt"
    assert len(cat.surveys()) == 3
    assert len(cat.stations()) == 365
    assert cat.surveys(survey_id="vulcan-2024-25")[0].survey_id == "vulcan-2024-25"
    assert cat.station("au.auslamp-nsw-2016-21.A23").survey_id == "auslamp-nsw-2016-21"
    assert cat.station("no.such.id") is None


def test_snapshot_validates_against_the_snapshot_schema():
    assert _cat().problems(schema=FIX / "mtcat.schema.snapshot.json") == []


def test_full_detail_document():
    doc = StationDetail(json.loads((FIX / "station-A23.json").read_text(encoding="utf-8")))
    assert not doc.withheld
    assert doc.resources(kind="transfer_function")
    assert all(r.get("kind") == "archive" for r in doc.resources(kind="archive"))


def test_withheld_detail_is_rendered_as_the_stub_it_is():
    doc = StationDetail(json.loads((FIX / "station-Vul24-13.json").read_text(encoding="utf-8")))
    assert doc.withheld
    assert doc.resources() == []
    assert doc.routes() == []


def test_routes_come_from_declared_fields_only():
    doc = StationDetail({"resources": [
        {"id": "a", "kind": "time_series", "access_url": "https://archive.example/x.zip",
         "processing_level": "raw"},
        {"id": "b", "kind": "transfer_function", "path": "edi/s/A1.edi"}]})
    routes = doc.routes()
    assert routes == [{"url": "https://archive.example/x.zip", "kind": "time_series",
                       "processing_level": "raw"}]
