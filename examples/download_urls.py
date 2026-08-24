"""Every verified time-series download a portal offers: the archive URL from the record, and
the portal's measured hand-off route where its profile declares one.

    python examples/download_urls.py [catalogue-url-or-path]
"""
import sys

from mtcatalogue import Catalog
from mtcatalogue.profiles import load

source = sys.argv[1] if len(sys.argv) > 1 else "https://ausmt.auscope.org.au/data/mtcat.json"
cat = Catalog(source, profile="ausmt")
profile = load("ausmt")
flagged = [s for s in cat.stations() if s.get("has_time_series") is True]
print(f"{len(flagged)} station(s) with a verified time series")
for row in flagged[:5]:
    doc = row.detail()
    routes = doc.routes() if doc else []
    print(f"  {row.station_id}:")
    for r in routes:
        print(f"    {r['processing_level']}: {r['url']}")
        handoff = profile.handoff_url(source, row.raw, "raw_packed")
        if handoff:
            print(f"    via portal: {handoff}")
    if not routes:
        print("    (no routes published yet)")
