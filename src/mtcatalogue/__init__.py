"""Python client for MTCAT-conformant magnetotelluric data portals."""
from .catalog import Catalog
from .rows import Row, StationDetail, StationRow, Survey

__version__ = "0.0.1"
__all__ = ["Catalog", "Row", "StationDetail", "StationRow", "Survey"]
