from __future__ import annotations

from datetime import time
import os
from typing import Optional

import seared as s

from ..models import StopTime, Timetable, Trip
from ..util import load_list


@s.seared
class Trips(s.Seared):
    '''
    Serializable dataclass table mapping `str` IDs to `Trip` records.

    Attributes:
        data (dict[str, Trip]):
            a `dict` mapping `str` IDs to `Trip` records
        ids (list[str]):
            a `list` of all `str` IDs in the `Trips` table
        trips (list[Trip]):
            a `list` of all `Trip` records in the `Trips` table
    '''

    ### ATTRIBUTES ###
    data: dict[str, Trip] = s.T(
        schema=Trip.SCHEMA,
        keyed=True,
        required=True
    )
    '''a `dict` mapping `str` IDs to `Trip` records'''


    ### CLASS METHODS ###
    @classmethod
    def from_gtfs (cls, path: str) -> Trips:
        '''
        Returns an `Trips` table populated from the GTFS data at `path`.

        Parameters:
            path (str):
                the path to the GTFS dataset

        Returns:
            trips (Trips):
                an `Trips` table populated from the GTFS data at `path`
        '''
        stop_times: dict[str, list[StopTime]] = {}

        stops: list[StopTime] = load_list(
            os.path.join(path, 'stop_times.txt'), 
            StopTime.SCHEMA,
            int_cols=['drop_off_type', 'pickup_type', 'timepoint']
        )

        for stop in stops:
            if stop.trip_id in stop_times:
                stop_times[stop.trip_id].append(stop)
            else:
                stop_times[stop.trip_id] = []

        trips: list[Trip] = load_list(
            path = os.path.join(path, 'trips.txt'),
            schema = Trip.SCHEMA,
            int_cols=['bikes_allowed', 'wheelchair_accessible']
        )

        for trip in trips:
            trip.timetable = Timetable.from_gtfs(stop_times[trip.id])

        return Trips({ t.id: t for t in trips })


    ### PROPERTIES ###
    @property
    def ids (self) -> list[str]:
        '''a `list` of all `str` IDs in the `Trips` table'''
        return list(self.data.keys())
    
    @property
    def service_ids (self) -> list[str]:
        '''a `list` of all `str` service IDs in the `Trips` table'''
        return list(set([t.service_id for t in self.trips]))
    
    @property
    def trips (self) -> list[Trip]:
        '''a `list` of all `Trip` records in the `Trips` table'''
        return list(self.data.values())    
    

    ### MAGIC METHODS ###
    def __getitem__ (self, id: str) -> Optional[Trip]:
        '''
        Returns the `Trip` record associated with the `id` if it exists,
        otherwise returns `None`.
        
        Parameters:
            id (str):
                the `str` id associated with the `Trip` record to retrieve

        Returns:
            record (Optional[Trip]):
                the `Trip` record associated with `id` if it exists, otherwise 
                `None`
        '''
        return self.data.get(id, None)
    

    ### METHODS ###    
    def between (self, start: time, end: time) -> Trips:
        '''
        Returns a `Trips` table containing only the `Trip` records with
        `Timetable`s that have entries between the given `start` and `end`
        times.

        Parameters:
            start (time):
                the beginning of the time window
            end (time):
                the end of the time window

        Returns:
            trips (Trips):
                a `Trips` table containing only the `Trip` records with
                `Timetable`s that have entries between the given `start` and 
                `end` times
        '''
        return Trips({
            t.id: t for t in self.trips
            if t.between(start, end)
        })
    
    def connecting (self, stop_a_id: str, stop_b_id: str) -> Trips:
        '''
        Returns a `Trips` table containing only the `Trip` records with
        `Timetable`s that contain chronologically ordered entries for both
        `stop_a_id` and `stop_b_id`.

        Parameters:
            stop_a_id (str):
                the unique ID associated with the first stop
            stop_b_id (str):
                the unique ID associated with the second stop

        Returns:
            trips (Trips):
                a `Trips` table containing only the `Trip` records with
                `Timetable`s that contain chronologically ordered entries for
                both `stop_a_id` and `stop_b_id`
        '''
        return Trips({
            t.id: t for t in self.trips
            if t.connects(stop_a_id, stop_b_id)
        })
    
    def on_date (self, service_ids: list[str]) -> Trips:
        '''
        Helper function to be used with `Schedules.on_date` that returns a
        `Trips` table containing only the `Trip` records associated with the
        given `service_ids`.

        Parameters:
            service_ids (list[str]):
                a `list` of `str` service IDs to search for

        Returns:
            trips (Trips):
                a `Trips` table containing only the `Trip` records associated
                with the given `service_ids`
        '''
        return Trips({
            t.id: t for t in self.trips
            if t.service_id in service_ids
        })
    
    def on_route (self, route_id: str) -> Trips:
        '''
        Returns a `Trips` table containing only the `Trip` records that belong
        to the route specified by `route_id`.

        Parameters:
            route_id (str):
                the unique ID corresponding to the route

        Returns:
            trips (Trips):
                a `Trips` table containing only the `Trip` records that belong
                to the route specified by `route_id`
        '''
        return Trips({
            t.id: t for t in self.trips
            if t.route_id == route_id
        })
    
    def through (self, stop_id: str) -> Trips:
        '''
        Returns a `Trips` table containing only the `Trip` records that go
        through the stop specified by `stop_id`.

        Parameters:
            stop_id (str):
                the unique ID corresponding to the stop

        Returns:
            trips (Trips):
                a `Trips` table containing only the `Trip` records that go
                through the stop specified by `stop_id`
        '''
        return Trips({
            t.id: t for t in self.trips
            if t.through(stop_id)
        })