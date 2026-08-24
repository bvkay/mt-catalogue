"""Profiles: URL layouts are portal conventions. Pure-spec mode resolves nothing it was not
given; the AusMT profile states AusMT's published convention and only that."""
import json
from pathlib import Path

import pytest

from mtcatalogue import Catalog
from mtcatalogue.profiles import load

FIX = Path(__file__).parent / "fixtures"


class FakeSession:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, timeout=None):
        return FakeResponse(self.pages[url])


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_pure_spec_mode_fetches_no_detail():
    cat = Catalog(str(FIX / "mtcat-snapshot.json"))
    assert cat.station("au.auslamp-nsw-2016-21.A23").detail() is None


def test_ausmt_profile_resolves_the_published_convention():
    snapshot = json.loads((FIX / "mtcat-snapshot.json").read_text(encoding="utf-8"))
    a23 = json.loads((FIX / "station-A23.json").read_text(encoding="utf-8"))
    fake = FakeSession({
        "https://portal.example/data/mtcat.json": snapshot,
        "https://portal.example/data/products/auslamp-nsw-2016-21/A23/station.json": a23,
    })
    cat = Catalog("https://portal.example/data/mtcat.json", profile="ausmt", session=fake)
    doc = cat.station("au.auslamp-nsw-2016-21.A23").detail()
    assert doc.ausmt_id == "au.auslamp-nsw-2016-21.A23"


def test_an_id_outside_the_convention_resolves_nothing():
    prof = load("ausmt")
    row = {"station_id": "weird-shape", "survey_id": "s"}
    assert prof.station_detail_url("https://x/data/mtcat.json", row) is None


def test_unknown_profile_name_is_an_error():
    with pytest.raises(ValueError):
        load("no-such-profile")


def test_a_partial_local_mirror_reads_as_absence_not_an_error():
    # a fixtures dir carries mtcat but no products tree; detail() returns None
    cat = Catalog(str(FIX / "mtcat-ts-snapshot.json"), profile="ausmt")
    assert cat.station("au.newer-volcanic-province-2019.C4").detail() is None
