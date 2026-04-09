from __future__ import annotations

from datetime import date as pydate, datetime, time, timedelta
from typing import Optional

import seared as s

from ..models import StopTime


@s.seared
class Timetable(s.Seared):
    '''
    Serializable dataclass table mapping `str` stop IDs to `StopTime` records.

    Attributes:
        data (dict[str, StopTime]):
            a `dict` mapping `str` stop IDs to `StopTime` records
        end (StopTime)
            the last `StopTime` record in the table chronologically
        start (StopTime)
            the first `StopTime` record in the table chronologically
        stop_ids (list[str]):
            a `list` of all `str` stop IDs in the `Timetable` table
        stops (list[StopTime]):
            a `list` of all `StopTime` records in the `Timetable` table
    '''

    ### ATTRIBUTES ###
    data: dict[str, StopTime] = s.T(
        schema=StopTime.SCHEMA,
        keyed=True,
        required=True
    )
    '''a `dict` mapping `str` stop IDs to `StopTime` records'''


    ### CLASS METHODS ###
    @classmethod
    def from_gtfs (cls, stops: list[StopTime]) -> Timetable:
        '''
        Returns a `Timetable` populated from `stops`.

        Parameters:
            stops (list[StopTime]):
                a `list` of `StopTime` records to put in the `Timetable`

        Returns:
            timetable (Timetable):
                a `Timetable` populated from `stops`
        '''
        return Timetable({ st.stop_id: st for st in stops })


    ### PROPERTIES ###    
    @property
    def end (self) -> StopTime:
        '''the last `StopTime` record in the table chronologically'''
        return self.stops[-1]
    
    @property
    def start (self) -> StopTime:
        '''the first `StopTime` record in the table chronologically'''
        return self.stops[0]
    
    @property
    def stop_ids (self) -> list[str]:
        '''a `list` of all `str` stop IDs in the `Timetable` table'''
        return list(self.data.keys())
     
    @property
    def stops (self) -> list[StopTime]:
        '''an ordered list of all `Stop` records in the table'''
        return sorted(
            list(self.data.values()), 
            key=lambda st: st.index
        )
    

    ### MAGIC METHODS ###
    def __getitem__ (self, id: str) -> Optional[StopTime]:
        '''
        Returns the `StopTime` record associated with the `id` if it exists,
        otherwise returns `None`.
        
        Parameters:
            id (str):
                the `str` id associated with the `StopTime` record to retrieve

        Returns:
            record (Optional[StopTime]):
                the `StopTime` record associated with `id` if it exists, 
                otherwise `None`
        '''
        return self.data.get(id, None)
    

    ### METHODS ###
    def between (self, start: time, end: time) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` contains entries between
        the given `start` and `end` times (time-only, no date context).

        Note: this method does not handle trips that cross midnight correctly.
        Use `between_datetime` when a service date is available.

        Parameters:
            start (time):
                the beginning of the time window
            end (time):
                the end of the time window

        Returns:
            between (bool):
                a flag indicating if the `Timetable` contains entries between
                the given `start` and `end` times
        '''
        return self.start.start_time <= end and self.end.end_time >= start

    def between_datetime (
                self,
                service_date: pydate,
                start: datetime,
                end: datetime
            ) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` contains entries that
        overlap with the given `[start, end]` datetime window, correctly
        accounting for trips that cross midnight.

        Each stop time is anchored to `service_date`: times with hours >= 24
        in the raw GTFS data (flagged by `start_offset` / `end_offset`) are
        placed on `service_date + 1 day`.

        Parameters:
            service_date (date):
                the calendar date on which the trip is scheduled to run
            start (datetime):
                the beginning of the query window
            end (datetime):
                the end of the query window

        Returns:
            between (bool):
                `True` if the trip's real datetime range overlaps `[start, end]`
        '''
        real_start = datetime.combine(service_date, self.start.start_time)
        if self.start.start_offset:
            real_start += timedelta(days=1)

        real_end = datetime.combine(service_date, self.end.end_time)
        if self.end.end_offset:
            real_end += timedelta(days=1)

        return real_start <= end and real_end >= start

    def connects (self, stop_a_id: str, stop_b_id: str) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` contains chronologically
        ordered entries for both `stop_a_id` and `stop_b_id`.

        Parameters:
            stop_a_id (str):
                the unique ID associated with the first stop
            stop_b_id (str):
                the unique ID associated with the second stop

        Returns:
            connects (bool):
                a flag indicating if the `Timetable` contains chronologically
                ordered entries for both `stop_a_id` and `stop_b_id`
        '''
        return self.through(stop_a_id) and self.through(stop_b_id) and \
            self[stop_a_id].index < self[stop_b_id].index
    
    def through (self, stop_id: str) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` contains an entry for 
        the `stop_id`.

        Parameters:
            stop_id (str):
                the unique ID associated with the stop

        Returns:
            through (bool):
                a flag indicating if the `Timetable` contains an entry for
                the 'stop_id`
        '''
        return stop_id in self.data