"""
Integration tests for railroaded using the SEPTA regional rail GTFS feed.

These tests verify that the full parse-and-query pipeline works correctly
end-to-end, covering every public method on the GTFS facade object.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Optional

import pytest
import railroaded as rr


# ---------------------------------------------------------------------------
# Constants taken directly from the README example
# ---------------------------------------------------------------------------
JEFFERSON_STATION      = '90006'
WASHINGTON_LANE_STATION = '90714'


# ---------------------------------------------------------------------------
# Date helpers — feed-range-aware
# ---------------------------------------------------------------------------
def _first_active_date_for_weekday(
            septa: 'rr.GTFS',
            weekday: int
        ) -> 'Optional[date]':
    """
    Return the first date within the feed's schedule ranges where at least one
    schedule is active on `weekday` (0=Monday … 6=Sunday).

    Returns `None` if no such date is found.
    """
    from datetime import date, timedelta
    for schedule in septa.schedules.schedules:
        if schedule.start is None:
            continue
        end = schedule.end or (schedule.start + timedelta(days=60))
        d = schedule.start
        while d <= end:
            if d.weekday() == weekday and schedule.active(d):
                return d
            d += timedelta(days=1)
    return None


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
    """on_date should return a non-empty subset for a date within the feed range."""

    def test_on_date_returns_trips(self, septa: rr.GTFS) -> None:
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        result = septa.on_date(monday)
        _assert_nonempty(result, f'on_date({monday})')

    def test_today_returns_gtfs(self, septa: rr.GTFS) -> None:
        result = septa.today()
        assert isinstance(result, rr.GTFS)

    def test_on_date_subset(self, septa: rr.GTFS) -> None:
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        result = septa.on_date(monday)
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


def _real_start(trip: 'rr.GTFS', service_date) -> datetime:
    """Compute the real start datetime of a trip given its service date."""
    from datetime import timedelta
    st = trip.timetable.start
    dt = datetime.combine(service_date, st.start_time)
    if st.start_offset:
        dt += timedelta(days=1)
    return dt


def _real_end(trip: 'rr.GTFS', service_date) -> datetime:
    """Compute the real end datetime of a trip given its service date."""
    from datetime import timedelta
    st = trip.timetable.end
    dt = datetime.combine(service_date, st.end_time)
    if st.end_offset:
        dt += timedelta(days=1)
    return dt


class TestBetween:
    """
    between() must:
    - Accept datetime objects (not raw time objects)
    - Use the DATE portion to restrict to trips active on the relevant day(s)
    - Use the TIME portion to filter by time window
    - Correctly capture trips that start before midnight and end after it
      (overnight trips encoded with GTFS hours >= 24)
    """

    def test_between_accepts_datetime(self, septa: rr.GTFS) -> None:
        start = datetime(2025, 1, 6, 8, 0, 0)
        end   = datetime(2025, 1, 6, 9, 0, 0)
        result = septa.between(start, end)
        assert isinstance(result, rr.GTFS)

    def test_between_returns_nonempty_for_valid_window(
                self, septa: rr.GTFS
            ) -> None:
        """A busy weekday morning should produce some trips."""
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        start = datetime.combine(monday, time(8, 0, 0))
        end   = datetime.combine(monday, time(9, 0, 0))
        result = septa.between(start, end)
        _assert_nonempty(result, f'between({monday} 08:00, 09:00)')

    def test_between_is_subset_of_all_trips(self, septa: rr.GTFS) -> None:
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        start = datetime.combine(monday, time(8, 0, 0))
        end   = datetime.combine(monday, time(9, 0, 0))
        result = septa.between(start, end)
        assert len(result.trips.ids) <= len(septa.trips.ids)

    def test_between_respects_date(self, septa: rr.GTFS) -> None:
        """
        The date portion of the datetimes must be used to filter by service
        schedule.  SEPTA rail has different Monday vs Saturday service, so the
        same 8–9 am window on those two days should yield different trip sets.
        """
        monday   = _first_active_date_for_weekday(septa, 0)  # Monday
        saturday = _first_active_date_for_weekday(septa, 5)  # Saturday
        if monday is None or saturday is None:
            pytest.skip('Could not find both a Monday and a Saturday in feed')
        mon_ids = set(septa.between(
            datetime.combine(monday, time(8, 0)),
            datetime.combine(monday, time(9, 0))
        ).trips.ids)
        sat_ids = set(septa.between(
            datetime.combine(saturday, time(8, 0)),
            datetime.combine(saturday, time(9, 0))
        ).trips.ids)
        assert mon_ids != sat_ids, \
            f'Monday {monday} and Saturday {saturday} 08–09 should differ'

    def test_between_excludes_inactive_trips(self, septa: rr.GTFS) -> None:
        """
        Trips not active on the queried date must not appear even if their
        stored times fall within the window.
        """
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        active_on_date = set(septa.on_date(monday).trips.ids)
        between_ids = set(septa.between(
            datetime.combine(monday, time(0, 0)),
            datetime.combine(monday, time(23, 59))
        ).trips.ids)
        # All trips returned by between() must be active on that date
        assert between_ids <= active_on_date, \
            'between() returned trips not active on the queried date'

    def test_between_outside_feed_range_returns_empty(
                self, septa: rr.GTFS
            ) -> None:
        """Dates far outside the feed's validity window should return nothing."""
        start = datetime(2000, 1, 3, 8, 0, 0)   # Monday, year 2000
        end   = datetime(2000, 1, 3, 9, 0, 0)
        result = septa.between(start, end)
        assert len(result.trips.ids) == 0, \
            'Expected no trips for a date outside the feed range'

    def test_between_overnight_window_does_not_crash(
                self, septa: rr.GTFS
            ) -> None:
        """A window that spans midnight must not raise an error."""
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        start = datetime.combine(monday, time(23, 0, 0))
        end   = datetime.combine(monday + timedelta(days=1), time(1, 0, 0))
        result = septa.between(start, end)
        assert isinstance(result, rr.GTFS)

    def test_between_overnight_trips_captured(self, septa: rr.GTFS) -> None:
        """
        A trip whose GTFS times cross midnight (raw hours >= 24) must appear
        in a window that overlaps its real datetime range.

        Strategy: find any trip in the feed whose last stop has end_offset=True
        (meaning raw departure hour >= 24, i.e. it runs past midnight).  Then
        build a window that covers 23:00 on its service date through 06:00 the
        following morning and assert the trip is present.
        """
        # Find an overnight trip (end_offset on last stop)
        overnight_trip = next(
            (t for t in septa.trips.trips if t.timetable.end.end_offset),
            None
        )
        if overnight_trip is None:
            import pytest
            pytest.skip('No overnight trips found in this feed')

        # Determine a service date the trip runs on by checking schedules
        service_date: Optional[date] = None
        schedule = septa.schedules[overnight_trip.service_id]
        if schedule and schedule.start:
            d = schedule.start
            while d is not None and d <= schedule.end:
                if schedule.active(d):
                    service_date = d
                    break
                d += timedelta(days=1)

        if service_date is None:
            import pytest
            pytest.skip('Could not determine a service date for overnight trip')

        # Build a window: 23:00 on service_date to 06:00 the following morning
        window_start = datetime.combine(service_date, time(23, 0, 0))
        window_end   = datetime.combine(service_date + timedelta(days=1), time(6, 0, 0))

        result = septa.between(window_start, window_end)
        assert overnight_trip.id in result.trips.ids, (
            f'Overnight trip {overnight_trip.id} (service date {service_date}) '
            f'not found in between({window_start}, {window_end})'
        )

    def test_between_zero_width_window_does_not_crash(
                self, septa: rr.GTFS
            ) -> None:
        """A zero-width window must not raise an error."""
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        instant = datetime.combine(monday, time(8, 0, 0))
        result = septa.between(instant, instant)
        assert isinstance(result, rr.GTFS)

    def test_between_combined_with_on_date(self, septa: rr.GTFS) -> None:
        """
        Chaining on_date().between() must not crash and must only return trips
        that overlap both the date filter and the time window.
        """
        monday = _first_active_date_for_weekday(septa, 0)
        if monday is None:
            pytest.skip('No active Monday found in feed')
        start = datetime.combine(monday, time(7, 0, 0))
        end   = datetime.combine(monday, time(10, 0, 0))
        result = septa.on_date(monday).between(start, end)
        assert isinstance(result, rr.GTFS)
        # Result should be a subset of the on_date result
        on_date_ids = set(septa.on_date(monday).trips.ids)
        for trip in result.trips.trips:
            assert trip.id in on_date_ids
