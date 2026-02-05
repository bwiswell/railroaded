from datetime import date as pydate
from enum import Enum

import seared as s


class ExceptionType(Enum):
    ADD = 1
    REMOVE = 2


@s.seared
class CalendarDate(s.Seared):
    '''
    A GTFS dataclass model for records found in `calendar_dates.txt`. 
    Defines an exception to the service patterns defined in `calendar.txt`.

    Attributes:
        service_id (str):
            the ID of the service the calendar date modifies
        date (date):
            the date when the service exception occurs
        exception (ExceptionType):
            the type of service exception specified
    '''

    ### ATTRIBUTES ###
    # Foreign IDs
    service_id: str = s.Str(required=True)
    '''the ID of the service the calendar date modifies'''
    
    # Required fields
    date: pydate = s.Date(format='%Y%m%d', required=True)
    '''the date when the service exception occurs'''
    exception: ExceptionType = s.Enum(
        data_key='exception_type', enum=ExceptionType, required=True
    )
    '''the type of service exception specified'''