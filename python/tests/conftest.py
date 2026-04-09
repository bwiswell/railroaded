"""
Pytest fixtures for railroaded tests.

Downloads and caches the SEPTA regional rail GTFS feed so the full suite
only hits the network once per machine.
"""
from __future__ import annotations

import os
import pytest
import railroaded as rr


SEPTA_URI    = 'https://www3.septa.org/developer/gtfs_public.zip'
SEPTA_SUB    = 'google_rail'
MGTFS_CACHE  = os.path.join(os.path.dirname(__file__), 'septa_cache.json')


@pytest.fixture(scope='session')
def septa() -> rr.GTFS:
    """
    Session-scoped GTFS fixture.  Downloads SEPTA rail GTFS on the first run
    and writes a local mGTFS cache file so subsequent runs skip the download.
    """
    return rr.GTFS.read(
        name       = 'SEPTA',
        gtfs_uri   = SEPTA_URI,
        gtfs_sub   = SEPTA_SUB,
        mgtfs_path = MGTFS_CACHE,
    )
