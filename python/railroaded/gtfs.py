from __future__ import annotations

from datetime import date as pydate, datetime, timedelta
import json
import os
import shutil
from typing import Optional
from urllib import request
import zipfile

import seared as s

from .models import Feed
from .tables import (
    Agencies,
    Routes,
    Schedules,
    Shapes,
    Stops,
    Trips
)


TMP = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'tmp')


@s.seared
class GTFS(s.Seared):
    '''
    Base dataclass database for reading and managing GTFS datasets.
    
    Attributes:
        name (str):
            the name of the GTFS dataset
        feed (Feed):
            the `Feed` of the GTFS dataset
        agencies (Agencies):
            an `Agencies` table mapping `str` IDs to `Agency` records
        routes (Routes):
            a `Routes` table mapping `str` IDs to `Route` records
        schedules (Schedules):
            a `Schedules` table mapping `str` service IDs to `Schedule` records
        stops (Stops):
            a `Stops` table mapping `str` IDs to `Stop` records
        trips (Trips):
            a `Trips` table mapping `str` IDs to `Trip` records
    '''

    ### ATTRIBUTES ###
    # Metadata
    name: str = s.Str(required=True)
    '''the name of the GTFS dataset'''
    feed: Feed = s.T(schema=Feed.SCHEMA)
    '''a `Feed` record describing the GTFS dataset'''

    # Tables
    agencies: Agencies = s.T(schema=Agencies.SCHEMA)
    '''an `Agencies` table mapping `str` IDs to `Agency` records'''
    routes: Routes = s.T(schema=Routes.SCHEMA)
    '''a `Routes` table mapping `str` IDs to `Route` records'''
    schedules: Schedules = s.T(schema=Schedules.SCHEMA)
    '''a `Schedules` table mapping `str` service IDs to `Schedule` records'''
    stops: Stops = s.T(schema=Stops.SCHEMA)
    '''a `Stops` table mapping `str` IDs to `Stop` records'''
    trips: Trips = s.T(schema=Trips.SCHEMA)
    '''a `Trips` table mapping `str` IDs to `Trip` records'''
    shapes: Shapes = s.T(schema=Shapes.SCHEMA)
    '''a `Shapes` table mapping `str` IDs to `Shape` records (opt-in via shapes=True)'''


    ### CLASS METHODS ###
    @classmethod
    def read (
                cls,
                name: str,
                gtfs_path: Optional[str] = None,
                gtfs_sub: Optional[str] = None,
                gtfs_uri: Optional[str] = None,
                mgtfs_path: Optional[str] = None,
                shapes: bool = False
            ) -> GTFS:
        '''
        Returns a `GTFS` object containing minified GTFS data read from local
        files or fetched from a remote source.

        If provided, `mgtfs_path` is checked first for a mGTFS dataset. If it
        exists, the `GTFS` object is created from it and returned; otherwise,
        `read` falls back to one of the following:

        - reading a unzipped local GTFS dataset at `gtfs_path`
        - fetching a zipped remote GTFS dataset at `gtfs_uri` with an optional \
            `gtfs_sub` for nested GTFS datasets

        If `mgtfs_path` was specified but `read` fell back to a different
        method, the newly parsed mGTFS will be written to `mgtfs_path` to
        improve performance on subsequent reads.

        Parameters:
            name (str):
                the name of the GTFS dataset
            gtfs_path (Optional[str]):
                the path to a local GTFS dataset
            gtfs_sub (Optional[str]):
                the subdirectory to use when fetching a remote GTFS dataset
            gtfs_uri (Optional[str]):
                the URI to use when fetching a remote GTFS dataset
            mgtfs_path (Optional[str]):
                the path to a local mGTFS dataset
            shapes (bool):
                if `True`, load `shapes.txt` polyline geometry; if `False`
                (default), the `shapes` table is left empty to reduce memory
                and cache size

        Returns:
            gtfs (GTFS):
                a `GTFS` object containing the minified GTFS dataset
        '''
        if mgtfs_path and os.path.exists(mgtfs_path):
            data = {}
            with open(mgtfs_path, 'r') as file:
                data = json.load(file)
            return GTFS.SCHEMA.load(data)
        
        if not gtfs_path:
            if os.path.exists(TMP): shutil.rmtree(TMP)
            os.mkdir(TMP)
            zip_path = os.path.join(TMP, f'{name}.zip')
            request.urlretrieve(gtfs_uri, zip_path)
            with zipfile.ZipFile(zip_path) as zip:
                zip.extractall(TMP)
            os.remove(zip_path)
            if gtfs_sub:
                zip_name = f'{gtfs_sub}.zip'
                zip_path = os.path.join(TMP, zip_name)
                for entry in os.scandir(TMP):
                    if entry.name != zip_name:
                        os.remove(entry.path)            
                with zipfile.ZipFile(zip_path) as zip:
                    zip.extractall(TMP)
                os.remove(zip_path)
            path = TMP
        else:
            path = gtfs_path

        g = GTFS(
            name=name,
            feed=Feed.from_gtfs(path),
            agencies=Agencies.from_gtfs(path),
            routes=Routes.from_gtfs(path),
            schedules=Schedules.from_gtfs(path),
            stops=Stops.from_gtfs(path),
            trips=Trips.from_gtfs(path),
            shapes=Shapes.from_gtfs(path) if shapes else Shapes({}),
        )

        if not gtfs_path: shutil.rmtree(TMP)
        if mgtfs_path: GTFS.save(g, mgtfs_path)

        return g


    @classmethod
    def save (cls, gtfs: GTFS, mgtfs_path: str):
        '''
        Writes a `GTFS` object to a `.json` file at `mgtfs_path`.

        Parameters:
            gtfs (GTFS):
                the `GTFS` to dump to file
            mgtfs_path (str):
                the `.json` file to dump the `GTFS` object to
        '''
        data = GTFS.dump(gtfs)
        with open(mgtfs_path, 'w') as file:
            json.dump(data, file)


    ### METHODS ###
    def _ref (self, trips: Trips) -> GTFS:
        return GTFS(
            self.name,
            self.feed,
            self.agencies,
            self.routes,
            self.schedules,
            self.stops,
            trips,
            self.shapes,
        )
    
    def between (self, start: datetime, end: datetime) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips whose real datetime
        range overlaps with the `[start, end]` window.

        Both the date and time components of `start` and `end` are respected:

        - Only trips active on a service date that falls within (or one day
          before) the query window are considered, so trips scheduled on the
          wrong day are excluded.
        - Trips that cross midnight are handled correctly: a trip whose raw
          GTFS times run from 23:00 to 25:30 (i.e. 01:30 the following
          calendar day) is captured by a window such as
          `[Jan 6 23:00, Jan 7 01:00]`.

        Implementation note: the previous calendar day is always included as a
        candidate service date so that overnight trips whose service date is the
        day before the window's start can still be captured.

        Parameters:
            start (datetime):
                the beginning of the query window (date + time)
            end (datetime):
                the end of the query window (date + time)

        Returns:
            gtfs (GTFS):
                a `GTFS` object containing only the matching trips
        '''
        # Collect candidate service dates.  Always include the day before the
        # window start so overnight trips that began on the prior calendar date
        # but extend into the window are not missed.
        candidate_dates: list[pydate] = []
        d = start.date() - timedelta(days=1)
        while d <= end.date():
            candidate_dates.append(d)
            d += timedelta(days=1)

        # Map each service_id to the subset of candidate dates it is active on.
        service_date_map: dict[str, list[pydate]] = {}
        for d in candidate_dates:
            for sid in self.schedules.on_date(d):
                if sid not in service_date_map:
                    service_date_map[sid] = []
                service_date_map[sid].append(d)

        # For each trip, check whether any of its active service dates produce
        # a real datetime window that overlaps [start, end].
        matching: dict[str, object] = {}
        for trip in self.trips.trips:
            service_dates = service_date_map.get(trip.service_id, [])
            for service_date in service_dates:
                if trip.between_datetime(service_date, start, end):
                    matching[trip.id] = trip
                    break

        return self._ref(Trips(matching))
    
    def connecting (self, stop_a_id: str, stop_b_id: str) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips connecting the stops
        corresponding to `stop_a_id` and `stop_b_id`.

        Parameters:
            stop_a_id (str):
                the unique ID corresponding to the starting stop
            stop_b_id (str):
                the unique ID corresponding to the ending stop

        Returns:
            gtfs (GTFS)
                a `GTFS` object containing only the trips connecting the stops
                corresponding to `stop_a_id` and `stop_b_id`
        '''
        return self._ref(self.trips.connecting(stop_a_id, stop_b_id))
    
    def on_date (self, date: pydate) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips occuring on `date`.

        Parameters:
            date (date):
                the date to find trips occuring on

        Returns:
            gtfs (GTFS):
                a `GTFS` object containing only the trips occuring on `date`
        '''
        return self._ref(self.trips.on_date(self.schedules.on_date(date)))
    
    def on_route (self, route_id: str) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips that belong to the
        route specified by `route_id`.

        Parameters:
            route_id (str):
                the unique ID corresponding to the route

        Returns:
            gtfs (GTFS):
                a `GTFS` object containing only the trips that belong to the
                route specified by `route_id`
        '''
        return self._ref(self.trips.on_route(route_id))
    
    def through (self, stop_id: str) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips that go through the
        stop specified by `stop_id`.

        Parameters:
            stop_id (str):
                the unique ID corresponding to the stop

        Returns:
            gtfs (GTFS):
                a `GTFS` object containing only the trips that go through the
                stop specified by `stop_id`
        '''
        return self._ref(self.trips.through(stop_id))

    def today (self) -> GTFS:
        '''
        Returns a `GTFS` object containing only the trips occuring on the
        current date.
        
        Returns:
            gtfs (GTFS):
                a `GTFS` object containing only the trips occuring on the
                current date
        '''
        return self.on_date(pydate.today())