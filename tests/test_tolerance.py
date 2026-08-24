"""Forward tolerance: documents from newer minor versions, unknown keys, and absent
optionals must all load."""
import json
from pathlib import Path

from mtcatalogue import Catalog

FIX = Path(__file__).parent / "fixtures"


def _future_doc(tmp_path):
    doc = json.loads((FIX / "mtcat-snapshot.json").read_text(encoding="utf-8"))
    doc["portal"]["version"] = "2.9"
    doc["portal"]["future_portal_key"] = {"nested": True}
    doc["surveys"][0]["future_survey_key"] = [1, 2]
    doc["stations"][0]["future_station_key"] = "x"
    doc["future_top_level"] = "y"
    p = tmp_path / "future.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_a_newer_minor_version_loads_and_keeps_its_unknown_keys(tmp_path):
    cat = Catalog(str(_future_doc(tmp_path)))
    assert cat.portal.version == "2.9"
    assert cat.portal.raw["future_portal_key"] == {"nested": True}
    assert cat.surveys()[0].raw["future_survey_key"] == [1, 2]
    assert cat.stations()[0].raw["future_station_key"] == "x"
    assert cat.raw["future_top_level"] == "y"


def test_absent_optionals_read_as_absent_not_errors():
    cat = Catalog(str(FIX / "mtcat-snapshot.json"))
    row = cat.stations()[0]
    assert row.get("has_time_series") in (None, True)
    assert row.get("no_such_key") is None


def test_validation_is_advisory_and_construction_succeeds(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"portal": {"portal_id": 7}, "stations": "wrong"}), encoding="utf-8")
    cat = Catalog(str(p))
    assert cat.portal.portal_id == 7
    assert cat.problems(schema=FIX / "mtcat.schema.snapshot.json")
