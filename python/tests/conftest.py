"""
Pytest fixtures for railroaded tests.

Downloads and caches the SEPTA regional rail GTFS feed so the full suite
only hits the network once per machine.

Note: the mGTFS JSON save/load feature (GTFS.save / GTFS.read with
mgtfs_path) relies on seared's Schema.dump(), which has a known bug with
keyed=True dict fields — it serialises the parent object instead of
individual values, producing empty dicts.  The pickle cache used here
bypasses that issue entirely.  The mGTFS bug is tracked in CODEBASE.md.
"""
from __future__ import annotations

import os
import pickle

import pytest
import railroaded as rr


SEPTA_URI    = 'https://www3.septa.org/developer/gtfs_public.zip'
SEPTA_SUB    = 'google_rail'
PICKLE_CACHE = os.path.join(os.path.dirname(__file__), 'septa_cache.pkl')


@pytest.fixture(scope='session')
def septa() -> rr.GTFS:
    """
    Session-scoped GTFS fixture.  Downloads SEPTA rail GTFS on the first run
    and writes a pickle cache so subsequent runs skip the network download.
    """
    if os.path.exists(PICKLE_CACHE):
        with open(PICKLE_CACHE, 'rb') as f:
            return pickle.load(f)

    g = rr.GTFS.read(
        name     = 'SEPTA',
        gtfs_uri = SEPTA_URI,
        gtfs_sub = SEPTA_SUB,
    )
    with open(PICKLE_CACHE, 'wb') as f:
        pickle.dump(g, f)
    return g
