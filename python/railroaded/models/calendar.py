from datetime import date

import seared as s


@s.seared
class Calendar(s.Seared):
    '''
    A GTFS dataclass model for records found in `calendar.txt`. Defines a \
    default schedule for a transit service.

    Attributes:
        service_id (str):
            the unique ID of the transit service the schedule is defined for
        end (date):
            the end date of the service schedule
        friday (bool):
            a `bool` indicating if the service is active on Fridays
        monday (bool):
            a `bool` indicating if the service is active on Mondays
        saturday (bool):
            a `bool` indicating if the service is active on Saturdays
        start (date):
            the start date of the service schedule
        sunday (bool):
            a `bool` indicating if the service is active on Sundays
        thursday (bool):
            a `bool` indicating if the service is active on Thursdays
        saturday (bool):
            a `bool` indicating if the service is active on Saturdays
        schedule (list[bool]):
            a list of `bool` indicating if service is available on a given day \
            when indexed by weekday
        sunday (bool):
            a `bool` indicating if the service is active on Sundays
    '''
    
    ### ATTRIBUTES ###
    # Foreign IDs
    service_id: str = s.Str(required=True)
    '''the unique ID of the transit service the schedule is defined for'''

    # Required fields
    end: date = s.Date(data_key='end_date', format='%Y%m%d', required=True)
    '''the end date of the service schedule'''
    friday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Fridays'''
    monday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Mondays'''
    saturday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Saturdays'''
    start: date = s.Date(data_key='start_date', format='%Y%m%d', required=True)
    '''the start date of the service schedule'''
    sunday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Sundays'''
    thursday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Thursdays'''
    tuesday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Tuesdays'''
    wednesday: bool = s.Bool(required=True)
    '''a `bool` indicating if the service is active on Wednesdays'''

    @property
    def schedule (self) -> list[bool]:
        '''
        a list of `bool` indicating if service is available on a given day \
        when indexed by weekday
        '''
        return [
            self.monday,
            self.tuesday,
            self.wednesday,
            self.thursday,
            self.friday,
            self.saturday,
            self.sunday
        ]