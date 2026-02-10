from datetime import time
from enum import Enum
from typing import Optional

import seared as s

from .accessibility import Accessibility
from .timetable import Timetable


class BikesAllowed(Enum):
    '''
    An `Enum` indicating if bikes are allowed on a trip.
    '''
    UNKNOWN = 0
    ALLOWED = 1
    DISALLOWED = 2


@s.seared
class Trip(s.Seared):
    '''
    A GTFS dataclass model for records found in `routes.txt`. Identifies a 
    transit route.
    
    Attributes:
        id (str):
            the unique ID of the trip
        block_id (Optional[str]):
            the unique ID of the block the trip belongs to
        route_id (str):
            the unique ID of the route the trip belongs to
        service_id (str):
            the unique ID of the service the trip belongs to
        shape_id (Optional[str]):
            the unique ID of the shape for the trip
        accessibility (Accessibility):
            the `Accessibility` of the trip
        bikes (BikesAllowed):
            the `BikesAllowed` of the trip
        direction (Optional[bool]):
            the direction of the trip
        headsign (Optional[str]):
            the headsign to display for the trip
        short_name (Optional[str]):
            a short name for the trip
        timetable (Timetable):
            the `Timetable` associated with the trip
    '''

    ### ATTRIBUTES ###
    # Model ID
    id: str = s.Str(data_key='trip_id', required=True)
    '''the unique ID of the trip'''

    # Foreign IDs
    block_id: Optional[str] = s.Str()
    '''the unique ID of the block the trip belongs to'''
    route_id: str = s.Str(required=True)
    '''the unique ID of the route the trip belongs to'''
    service_id: str = s.Str(required=True)
    '''the unique ID of the service the trip belongs to'''
    shape_id: Optional[str] = s.Str()
    '''the unique ID of the shape for the trip'''

    # Required fields
    accessibility: Accessibility = s.Enum(
        data_key='wheelchair_accessible', 
        enum=Accessibility, 
        missing=Accessibility.UNKNOWN
    )
    '''the `Accessibility` of the trip'''
    bikes: BikesAllowed = s.Enum(
        data_key='bikes_allowed', 
        enum=BikesAllowed, 
        missing=BikesAllowed.UNKNOWN
    )
    '''the `BikesAllowed` of the trip'''
    timetable: Timetable = s.T(schema=Timetable.SCHEMA)
    '''the `Timetable` associated with the trip'''

    # Optional fields
    direction: Optional[bool] = s.Str(data_key='direction_id')
    '''the direction of the trip'''
    headsign: Optional[str] = s.Str(data_key='trip_headsign')
    '''the headsign to display for the trip'''
    short_name: Optional[str] = s.Str(data_key='trip_short_name')
    '''a short name for the trip'''


    ### METHODS ###
    def between (self, start: time, end: time) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` for the `Trip` record
        contains entries between the given `start` and `end` times.

        Parameters:
            start (time):
                the beginning of the time window
            end (time):
                the end of the time window

        Returns:
            between (bool):
                a flag indicating if the `Timetable` for the `Trip` record
                contains entries between the given `start` and `end` times.
        '''
        return self.timetable.between(start, end)

    def connects (self, stop_a_id: str, stop_b_id: str) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` for the `Trip` record
        contains chronologically ordered entries for both `stop_a_id` and 
        `stop_b_id`.

        Parameters:
            stop_a_id (str):
                the unique ID associated with the first stop
            stop_b_id (str):
                the unique ID associated with the second stop

        Returns:
            connects (bool):
                a flag indicating if the `Timetable` for the `Trip` record
                contains chronologically ordered entries for both `stop_a_id`
                and `stop_b_id`
        '''
        return self.timetable.connects(stop_a_id, stop_b_id)
    
    def through (self, stop_id: str) -> bool:
        '''
        Returns a `bool` indicating if the `Timetable` for the `Trip` record
        contains an entry for the `stop_id`.

        Parameters:
            stop_id (str):
                the unique ID associated with the stop
        
        Returns:
            through (bool):
                a flag indicating if the `Timetable` for the `Trip` record
                contains an entry for the `stop_id`.
        '''
        return self.timetable.through(stop_id)