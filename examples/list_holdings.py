"""List every survey a portal holds, with station counts and time-series verification.

    python examples/list_holdings.py [catalogue-url-or-path]
"""
import sys

from mtcatalogue import Catalog

source = sys.argv[1] if len(sys.argv) > 1 else "https://ausmt.auscope.org.au/data/mtcat.json"
cat = Catalog(source)
print(f"{cat.portal.portal_name} (MTCAT {cat.portal.version})")
for sv in cat.surveys():
    n_ts = sv.get("n_stations_time_series_verified")
    ts = f", {n_ts} with verified time series" if n_ts else ""
    print(f"  {sv.survey_id}: {sv.get('n_stations', '?')} stations{ts}")
