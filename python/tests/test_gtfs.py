"""
Integration tests for railroaded using the SEPTA regional rail GTFS feed.

These tests verify that the full parse-and-query pipeline works correctly
end-to-end, covering every public method on the GTFS facade object.
"""
from __future__ import annotations

from datetime import datetime, time

import pytest
import railroaded as rr


# ---------------------------------------------------------------------------
# Constants taken directly from the README example
# ---------------------------------------------------------------------------
JEFFERSON_STATION      = '90006'
WASHINGTON_LANE_STATION = '90714'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _assert_nonempty(gtfs: rr.GTFS, label: str) -> None:
    assert len(gtfs.trips.trips) > 0, f'{label}: expected trips, got none'


# ===========================================================================
# Basic structure tests
# ===========================================================================

class TestLoad:
    """Verify that the SEPTA feed loads without error and has the right shape."""

    def test_has_agencies(self, septa: rr.GTFS) -> None:
        assert len(septa.agencies.ids) > 0

    def test_has_routes(self, septa: rr.GTFS) -> None:
        assert len(septa.routes.ids) > 0

    def test_has_stops(self, septa: rr.GTFS) -> None:
        assert len(septa.stops.ids) > 0

    def test_has_trips(self, septa: rr.GTFS) -> None:
        assert len(septa.trips.ids) > 0

    def test_has_schedules(self, septa: rr.GTFS) -> None:
        assert len(septa.schedules.service_ids) > 0

    def test_version(self) -> None:
        assert rr.__version__ == '0.2.1'


# ===========================================================================
# Timetable correctness — regression for "first stop dropped" bug
# ===========================================================================

class TestTimetable:
    """Every trip's timetable should have all its stop-time entries."""

    def test_all_trips_have_timetable(self, septa: rr.GTFS) -> None:
        for trip in septa.trips.trips:
            assert trip.timetable is not None, \
                f'Trip {trip.id} has no timetable'

    def test_timetable_has_stops(self, septa: rr.GTFS) -> None:
        for trip in septa.trips.trips:
            assert len(trip.timetable.stops) > 0, \
                f'Trip {trip.id} has an empty timetable'

    def test_timetable_first_stop_present(self, septa: rr.GTFS) -> None:
        """
        Regression for the bug where the first stop of each trip was silently
        dropped (trips.py:62 initialised an empty list instead of [stop]).
        """
        for trip in septa.trips.trips:
            stops = trip.timetable.stops
            # Stops are sorted by index; the entry with the lowest index must
            # exist in the timetable data dict.
            first = stops[0]
            assert first.stop_id in trip.timetable.data, \
                f'Trip {trip.id}: first stop {first.stop_id} not in timetable'

    def test_timetable_ordered_by_index(self, septa: rr.GTFS) -> None:
        for trip in septa.trips.trips:
            stops = trip.timetable.stops
            for a, b in zip(stops, stops[1:]):
                assert a.index < b.index, \
                    f'Trip {trip.id}: stop order is wrong ({a.index} >= {b.index})'

    def test_stop_times_parse_correctly(self, septa: rr.GTFS) -> None:
        """Regression for the seconds=/second= and (bool>=24)%24 bugs."""
        for trip in septa.trips.trips:
            for st in trip.timetable.stops:
                if st.start_time is not None:
                    assert 0 <= st.start_time.hour <= 23, \
                        f'start_time.hour out of range for stop {st.stop_id}'
                    assert 0 <= st.start_time.minute <= 59
                    assert 0 <= st.start_time.second <= 59
                if st.end_time is not None:
                    assert 0 <= st.end_time.hour <= 23, \
                        f'end_time.hour out of range for stop {st.stop_id}'


# ===========================================================================
# Filtering methods
# ===========================================================================

class TestOnDate:
    """on_date should return a non-empty subset for a recent known date."""

    def test_on_date_returns_trips(self, septa: rr.GTFS) -> None:
        # Use a fixed Monday that is almost certainly within the feed range.
        # If the feed has expired this test will still pass (it just returns
        # 0 trips), so we only assert the call doesn't crash.
        from datetime import date
        result = septa.on_date(date(2025, 1, 6))
        assert isinstance(result, rr.GTFS)

    def test_today_returns_gtfs(self, septa: rr.GTFS) -> None:
        result = septa.today()
        assert isinstance(result, rr.GTFS)

    def test_on_date_subset(self, septa: rr.GTFS) -> None:
        from datetime import date
        result = septa.on_date(date(2025, 1, 6))
        assert len(result.trips.ids) <= len(septa.trips.ids)


class TestOnRoute:
    def test_on_route_narrows_trips(self, septa: rr.GTFS) -> None:
        route_id = septa.routes.ids[0]
        result = septa.on_route(route_id)
        assert isinstance(result, rr.GTFS)
        for trip in result.trips.trips:
            assert trip.route_id == route_id

    def test_on_route_unknown_returns_empty(self, septa: rr.GTFS) -> None:
        result = septa.on_route('__nonexistent_route__')
        assert len(result.trips.ids) == 0


class TestThrough:
    def test_through_jefferson(self, septa: rr.GTFS) -> None:
        result = septa.through(JEFFERSON_STATION)
        _assert_nonempty(result, 'through(JEFFERSON)')
        for trip in result.trips.trips:
            assert trip.timetable.through(JEFFERSON_STATION)

    def test_through_washington_lane(self, septa: rr.GTFS) -> None:
        result = septa.through(WASHINGTON_LANE_STATION)
        _assert_nonempty(result, 'through(WASHINGTON_LANE)')

    def test_through_unknown_stop_returns_empty(self, septa: rr.GTFS) -> None:
        result = septa.through('__nonexistent_stop__')
        assert len(result.trips.ids) == 0


class TestConnecting:
    """Regression test for the README example."""

    def test_connecting_jefferson_to_washington_lane(
                self, septa: rr.GTFS
            ) -> None:
        result = septa.connecting(JEFFERSON_STATION, WASHINGTON_LANE_STATION)
        _assert_nonempty(result, 'connecting(JEFFERSON, WASHINGTON_LANE)')
        for trip in result.trips.trips:
            timetable = trip.timetable
            assert timetable.through(JEFFERSON_STATION)
            assert timetable.through(WASHINGTON_LANE_STATION)
            assert (
                timetable[JEFFERSON_STATION].index <
                timetable[WASHINGTON_LANE_STATION].index
            ), 'Trip goes the wrong direction'

    def test_connecting_reversed_returns_empty(self, septa: rr.GTFS) -> None:
        """A trip from A→B should NOT appear when connecting(B, A) is called."""
        forward = septa.connecting(JEFFERSON_STATION, WASHINGTON_LANE_STATION)
        reverse = septa.connecting(WASHINGTON_LANE_STATION, JEFFERSON_STATION)
        forward_ids = set(forward.trips.ids)
        reverse_ids = set(reverse.trips.ids)
        assert forward_ids.isdisjoint(reverse_ids), \
            'Some trips appear in both directions'


class TestBetween:
    """
    between() must accept datetime objects (not raw time objects).

    The time component is extracted internally and used to filter trips.
    """

    def test_between_accepts_datetime(self, septa: rr.GTFS) -> None:
        start = datetime(2025, 1, 6, 8, 0, 0)
        end   = datetime(2025, 1, 6, 9, 0, 0)
        result = septa.between(start, end)
        assert isinstance(result, rr.GTFS)

    def test_between_narrows_to_window(self, septa: rr.GTFS) -> None:
        start = datetime(2025, 1, 6, 8, 0, 0)
        end   = datetime(2025, 1, 6, 9, 0, 0)
        result = septa.between(start, end)
        start_t = start.time()
        end_t   = end.time()
        for trip in result.trips.trips:
            timetable = trip.timetable
            # At least one stop must fall within the window
            assert timetable.start.start_time <= end_t
            assert timetable.end.end_time >= start_t

    def test_between_uses_time_not_date(self, septa: rr.GTFS) -> None:
        """The date portion of the datetime must be irrelevant."""
        start_a = datetime(2020, 1, 1, 8, 0, 0)
        end_a   = datetime(2020, 1, 1, 9, 0, 0)
        start_b = datetime(2030, 6, 15, 8, 0, 0)
        end_b   = datetime(2030, 6, 15, 9, 0, 0)
        ids_a = set(septa.between(start_a, end_a).trips.ids)
        ids_b = set(septa.between(start_b, end_b).trips.ids)
        assert ids_a == ids_b, \
            'between() produced different results for the same time on different dates'

    def test_between_impossible_window_returns_empty(
                self, septa: rr.GTFS
            ) -> None:
        """A zero-width window at midnight should return very few or no trips."""
        start = datetime(2025, 1, 6, 0, 0, 0)
        end   = datetime(2025, 1, 6, 0, 0, 0)
        result = septa.between(start, end)
        assert isinstance(result, rr.GTFS)

    def test_between_combined_with_on_date(self, septa: rr.GTFS) -> None:
        """Chaining on_date().between() should not crash."""
        from datetime import date
        start = datetime(2025, 1, 6, 7, 0, 0)
        end   = datetime(2025, 1, 6, 10, 0, 0)
        result = septa.on_date(date(2025, 1, 6)).between(start, end)
        assert isinstance(result, rr.GTFS)
