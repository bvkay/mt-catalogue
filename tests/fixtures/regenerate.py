"""Regenerate the fixtures from the live portal: a reduced but unedited snapshot (three
surveys, all their stations) plus three exemplar station documents and the schema snapshots.
Run from this directory."""
import json
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).parent
BASE = "https://ausmt.auscope.org.au/data/"
KEEP = {"newer-volcanic-province-2019", "vulcan-2024-25", "auslamp-nsw-2016-21"}
# The -ts fixtures were first cut from the THREDDS lane's certified pre-release build; from the
# first post-deploy run of this script they come from live like everything else.
STATIONS = [("station-A23.json", "products/auslamp-nsw-2016-21/A23/station.json"),
            ("station-C4-ts.json", "products/newer-volcanic-province-2019/C4/station.json"),
            ("station-Vul24-13.json", "products/vulcan-2024-25/Vul24-13/station.json"),
            ("station-C4.json", "products/newer-volcanic-province-2019/C4/station.json")]
SCHEMAS = [("mtcat.schema.snapshot.json", "schemas/mtcat/2.0/mtcat.schema.json"),
           ("ausmt-station.schema.snapshot.json",
            "schemas/ausmt-station/0.1/ausmt-station.schema.json")]


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return r.read()


if __name__ == "__main__":
    full = json.loads(get("mtcat.json"))
    doc = {"portal": full["portal"],
           "surveys": [s for s in full["surveys"] if s["survey_id"] in KEEP],
           "stations": [s for s in full["stations"] if s["survey_id"] in KEEP],
           "collections": full.get("collections", [])}
    (HERE / "mtcat-snapshot.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    for name, path in STATIONS:
        (HERE / name).write_text(json.dumps(json.loads(get(path)), indent=1), encoding="utf-8")
    for name, path in SCHEMAS:
        (HERE / name).write_bytes(get(path))
    print(f"{len(doc['surveys'])} surveys, {len(doc['stations'])} stations")
