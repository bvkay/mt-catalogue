"""Fetch one station's full record: identity, runs, resources.

    python examples/station_detail.py [station-id] [catalogue-url-or-path]
"""
import sys

from mtcatalogue import Catalog

sid = sys.argv[1] if len(sys.argv) > 1 else "au.newer-volcanic-province-2019.C4"
source = sys.argv[2] if len(sys.argv) > 2 else "https://ausmt.auscope.org.au/data/mtcat.json"
cat = Catalog(source, profile="ausmt")
row = cat.station(sid)
if row is None:
    sys.exit(f"{sid}: not in this catalogue")
doc = row.detail()
if doc is None:
    sys.exit("this catalogue source resolves no station detail (local file or no profile)")
print(f"{doc.ausmt_id} ({doc.get('survey')}) - schema {doc.schema} {doc.version}")
for run in doc.get("runs", []):
    print(f"  run {run['id']}: {run.get('sample_rate_hz', '?')} Hz, "
          f"logger {(run.get('data_logger') or {}).get('model', '?')}")
for res in doc.resources():
    print(f"  {res.kind}: {res.get('path') or res.get('access_url')}")
