"""
Smoke test for PATCO (Speedline) GTFS data via railroaded.

Downloads the PATCO static GTFS feed, parses it, and validates that the
key structures are populated and queryable.  A local mGTFS JSON cache is
written so subsequent runs skip the network download.
"""
from __future__ import annotations

import os
from datetime import date, datetime, time, timedelta
from typing import Optional

import pytest
import railroaded as rr


PATCO_URI   = 'https://rapid.nationalrtap.org/GTFSFileManagement/UserUploadFiles/13562/PATCO_GTFS.zip'
MGTFS_CACHE = os.path.join(os.path.dirname(__file__), 'patco_cache.json')


@pytest.fixture(scope='session')
def patco() -> rr.GTFS:
    return rr.GTFS.read(
        name       = 'PATCO',
        gtfs_uri   = PATCO_URI,
        mgtfs_path = MGTFS_CACHE,
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _first_active_date(gtfs: rr.GTFS) -> Optional[date]:
    """Return the earliest date on which any schedule is active."""
    for schedule in gtfs.schedules.schedules:
        if schedule.start:
            d = schedule.start
            end = schedule.end or (d + timedelta(days=30))
            while d <= end:
                if schedule.active(d):
                    return d
                d += timedelta(days=1)
    return None


# ===========================================================================
# Structure
# ===========================================================================

class TestPatcoLoad:
    def test_has_agencies(self, patco: rr.GTFS) -> None:
        assert len(patco.agencies.ids) > 0

    def test_has_routes(self, patco: rr.GTFS) -> None:
        assert len(patco.routes.ids) > 0

    def test_has_stops(self, patco: rr.GTFS) -> None:
        assert len(patco.stops.ids) > 0

    def test_has_trips(self, patco: rr.GTFS) -> None:
        assert len(patco.trips.ids) > 0

    def test_has_schedules(self, patco: rr.GTFS) -> None:
        assert len(patco.schedules.service_ids) > 0

    def test_agency_name(self, patco: rr.GTFS) -> None:
        names = [a.name for a in patco.agencies.agencies]
        print(f'\nAgencies: {names}')
        assert any('PATCO' in n or 'Port Authority' in n for n in names)

    def test_single_route(self, patco: rr.GTFS) -> None:
        """PATCO operates exactly one route (the Speedline)."""
        print(f'\nRoutes: {[(r.id, r.name) for r in patco.routes.routes]}')
        assert len(patco.routes.ids) == 1

    def test_fourteen_stops(self, patco: rr.GTFS) -> None:
        """PATCO Speedline has 13 stations (sometimes listed as 13 or 14 stops)."""
        n = len(patco.stops.ids)
        print(f'\nStop count: {n}')
        print(f'Stops: {[(s.id, s.name) for s in patco.stops.stops]}')
        assert 13 <= n <= 15


# ===========================================================================
# Timetable correctness
# ===========================================================================

class TestPatcoTimetable:
    def test_all_trips_have_timetable(self, patco: rr.GTFS) -> None:
        for trip in patco.trips.trips:
            assert trip.timetable is not None, f'Trip {trip.id} missing timetable'

    def test_timetable_has_stops(self, patco: rr.GTFS) -> None:
        for trip in patco.trips.trips:
            assert len(trip.timetable.stops) > 0, f'Trip {trip.id} empty timetable'

    def test_stop_times_valid(self, patco: rr.GTFS) -> None:
        for trip in patco.trips.trips:
            for st in trip.timetable.stops:
                if st.start_time is not None:
                    assert 0 <= st.start_time.hour <= 23
                    assert 0 <= st.start_time.minute <= 59


# ===========================================================================
# Filtering
# ===========================================================================

class TestPatcoFiltering:
    def test_on_date_returns_trips(self, patco: rr.GTFS) -> None:
        d = _first_active_date(patco)
        if d is None:
            pytest.skip('No active date found in feed')
        result = patco.on_date(d)
        assert len(result.trips.ids) > 0, f'on_date({d}) returned no trips'

    def test_on_route_works(self, patco: rr.GTFS) -> None:
        route_id = patco.routes.ids[0]
        result = patco.on_route(route_id)
        assert len(result.trips.ids) > 0
        for trip in result.trips.trips:
            assert trip.route_id == route_id

    def test_today_returns_gtfs(self, patco: rr.GTFS) -> None:
        result = patco.today()
        assert isinstance(result, rr.GTFS)

    def test_between_valid_window(self, patco: rr.GTFS) -> None:
        d = _first_active_date(patco)
        if d is None:
            pytest.skip('No active date found in feed')
        start = datetime.combine(d, time(8, 0))
        end   = datetime.combine(d, time(9, 0))
        result = patco.between(start, end)
        assert isinstance(result, rr.GTFS)
        print(f'\nbetween({d} 08-09): {len(result.trips.ids)} trips')

    def test_connecting_terminal_stops(self, patco: rr.GTFS) -> None:
        """Trips should run between the two terminals of the Speedline."""
        stops = patco.stops.stops
        if len(stops) < 2:
            pytest.skip('Not enough stops')
        # Use first and last stop in the list
        stop_ids = [s.id for s in stops]
        print(f'\nTesting connecting({stop_ids[0]}, {stop_ids[-1]})')
        result = patco.connecting(stop_ids[0], stop_ids[-1])
        print(f'Trips connecting terminals: {len(result.trips.ids)}')
        # At least some direction should work
        reverse = patco.connecting(stop_ids[-1], stop_ids[0])
        assert len(result.trips.ids) > 0 or len(reverse.trips.ids) > 0, \
            'No trips found connecting the two terminal stops in either direction'
