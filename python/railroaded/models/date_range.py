from __future__ import annotations

from datetime import date

import seared as s


@s.seared
class DateRange(s.Seared):
    '''
    A dataclass model for storing a weekly schedule for an inclusive date
    range.

    Attributes:
        end (date):
            the end `date` of the range
        schedule (list[bool]):
            a `list` of `bool` indicating if service is active when indexed
            by weekday
        start (date):
            the start `date` of the range
    '''

    ### ATTRIBUTES ###
    # Required fields
    end: date = s.Date(required=True)
    '''the end `date` of the range'''
    schedule: list[bool] = s.Bool(many=True, required=True)
    '''
    a `list` of `bool` indicating if service is active when indexed by weekday
    '''
    start: date = s.Date(required=True)
    '''the start `date` of the range'''