# mt-catalogue

Python client for MTCAT-conformant magnetotelluric data portals.

MTCAT is a small discovery format for MT survey and station holdings. This client reads any
portal serving it; portal-specific URL conventions live in profile plugins, never in the core.

```python
from mtcatalogue import Catalog

cat = Catalog("https://ausmt.auscope.org.au/data/mtcat.json", profile="ausmt")
cat.surveys(country="Australia")
st = cat.station("au.newer-volcanic-province-2019.C4")
doc = st.detail()                          # station.json, schema 0.1
doc.resources(kind="transfer_function")
doc.routes()                               # download URLs from declared fields
```

- Specification and first live implementation: https://ausmt.auscope.org.au/
- Depends on `requests` and `jsonschema` only; analysis belongs to
  [mtpy-v2](https://github.com/MTgeophysics/mtpy-v2), packaging to
  [mth5](https://github.com/IAGA-DVI-DataStandards/mth5).
- Validation is advisory and documents from newer minor versions load unchanged.

```
pip install mt-catalogue
```
