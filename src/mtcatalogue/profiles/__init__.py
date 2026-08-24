"""Portal profiles. MTCAT declares what a portal holds; it does not declare URL layouts for
per-station documents. Anything layout-shaped lives in a profile, labelled as that portal's
convention. No profile means pure-spec mode: only declared fields resolve."""
from __future__ import annotations

from importlib import metadata


class Profile:
    name = "pure-spec"

    def station_detail_url(self, catalog_url: str, station_row: dict):
        return None


def load(name):
    """A Profile instance: None -> pure-spec; a Profile -> itself; a string -> the
    installed entry point of that name (group `mtcatalogue.profiles`)."""
    if name is None:
        return Profile()
    if isinstance(name, Profile):
        return name
    for ep in metadata.entry_points(group="mtcatalogue.profiles"):
        if ep.name == name:
            return ep.load()()
    if name == "ausmt":
        from .ausmt import AusmtProfile
        return AusmtProfile()
    raise ValueError(f"no installed profile named {name!r}")
