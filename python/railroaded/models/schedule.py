from __future__ import annotations

from datetime import date as pydate

import seared as s

from ..util import split

from .calendar import Calendar
from .calendar_date import CalendarDate, ExceptionType as ExType
from .date_range import DateRange


@s.seared
class Schedule(s.Seared):
    '''
    A dataclass model that defines a schedule for a transit service.

    Attributes:
        service_id (str):
            the unique ID of the service associated with the schedule
        additions (list[date]): 
            a list of dates on which additional service is offered
        end (date):
            the end date of the transit schedule
        exceptions (list[date]): 
            a list of dates on which service is suspended
        ranges (list[DateRange]):
            a `list` `DateRange` records associated with the schedule
        start (date):
            the start date of the transit schedule
    '''

    ### ATTRIBUTES ###
    # Foreign IDs
    service_id: str = s.Str(required=True)
    '''the unique ID of the service associated with the schedule'''

    # Required fields
    additions: list[pydate] = s.Date(many=True, required=True)
    '''a list of dates on which additional service is offered'''
    exceptions: list[pydate] = s.Date(many=True, required=True)
    '''a list of dates on which service is suspended'''
    ranges: list[DateRange] = s.T(
        schema=DateRange.SCHEMA, many=True, required=True
    )
    '''a `list` `DateRange` records associated with the schedule'''


    ### CLASS METHODS ###
    @classmethod
    def from_gtfs (
                cls,
                service_id: str,
                calendars: list[Calendar],
                dates: list[CalendarDate]
            ) -> Schedule:
        '''
        Returns a `Schedule` created from the given `Calendar` and 
        `CalendarDate` records.

        All `Calendar` and `CalendarDate` values should be for the same 
        transit service.

        Parameters:
            service_id (str):
                the unique ID of the service associated with the schedule
            calendars (list[Calendar]):
                a list of `Calendar` records associated with a transit service
            dates (list[CalendarDate]):
                a list of `CalendarDate` records associated with a transit \
                service

        Returns:
            schedule (Schedule):
                a dataclass model that defines a schedule for a transit service
        '''
        adds, excepts = split(dates, lambda d: d.exception == ExType.ADD)
        return Schedule(
            service_id=service_id, 
            additions=[a.date for a in adds], 
            exceptions=[e.date for e in excepts], 
            ranges=[
                DateRange(cal.end, cal.schedule, cal.start)
                for cal in calendars
            ]
        )


    ### PROPERTIES ###
    @property
    def end (self) -> pydate:
        '''the end date of the transit schedule'''
        return max([r.end for r in self.ranges])
    
    @property
    def start (self) -> pydate:
        '''the start date of the transit schedule'''
        return min([r.start for r in self.ranges])


    ### METHODS ###
    def active (self, date: pydate) -> bool:
        '''
        Returns a `bool` indicating if the service is active on `date`.

        Returns `False` if `date` is outside of the GTFS dataset's 
        `feed_start_date` and `feed_end_date`.

        Parameters:
            date (date):
                the date to check for active service

        Returns:
            active (bool):
                a `bool` indicating if the service is active on `date`
        '''
        if date in self.additions: return True
        if date in self.exceptions: return False
        for r in self.ranges:
            if r.start <= date and date <= r.end:
                return r.schedule[date.weekday()]
        return False