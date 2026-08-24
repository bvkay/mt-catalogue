"""The THREDDS-era surfaces, against lane-build snapshots (refresh from live after deploy):
the projection keys, time_series resource rows, routes() finding real archive URLs, and the
AusMT hand-off route convention."""
import json
from pathlib import Path

from mtcatalogue import Catalog, StationDetail
from mtcatalogue.profiles import load

FIX = Path(__file__).parent / "fixtures"


def test_the_projection_keys_read_naturally():
    cat = Catalog(str(FIX / "mtcat-ts-snapshot.json"))
    flagged = [s for s in cat.stations() if s.get("has_time_series") is True]
    assert len(flagged) == 49
    sv = cat.surveys(survey_id="newer-volcanic-province-2019")[0]
    assert sv.n_stations_time_series_verified == 49
    # true-or-absent: no station row anywhere carries a false
    assert not any(s.get("has_time_series") is False for s in cat.stations())


def test_routes_find_the_archive_url_on_a_real_document():
    doc = StationDetail(json.loads((FIX / "station-C4-ts.json").read_text(encoding="utf-8")))
    rows = doc.resources(kind="time_series")
    assert len(rows) == 1 and rows[0].processing_level == "raw"
    routes = doc.routes()
    assert len(routes) == 1
    assert routes[0]["url"].startswith("https://thredds.nci.org.au/thredds/fileServer/")
    assert " " not in routes[0]["url"]


def test_the_handoff_route_is_a_profile_convention():
    prof = load("ausmt")
    row = {"station_id": "au.newer-volcanic-province-2019.C4",
           "survey_id": "newer-volcanic-province-2019"}
    url = prof.handoff_url("https://ausmt.auscope.org.au/data/mtcat.json", row, "raw_packed")
    assert url == "https://ausmt.auscope.org.au/go/ts/newer-volcanic-province-2019/C4/raw_packed"
    # a local-path catalogue has no origin to hand off to
    assert prof.handoff_url(str(FIX / "mtcat-ts-snapshot.json"), row, "raw_packed") is None
    # pure-spec mode has no such concept at all
    assert not hasattr(load(None), "handoff_url")


def test_ts_access_snapshot_membership_is_open_only():
    ts = json.loads((FIX / "ts_access-snapshot.json").read_text(encoding="utf-8"))
    assert len(ts) == 49
    assert all(k.startswith("au.newer-volcanic-province-2019.") for k in ts)
    assert all("url_path" in row for levels in ts.values() for row in levels.values())
