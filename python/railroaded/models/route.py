from enum import Enum
from typing import Optional

import seared as s

from .stop_continuity import StopContinuity


class TransitType(Enum):
    '''
    An `Enum` describing the transit type of a route.
    '''
    LIGHT_RAIL = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    CABLE_CAR = 6
    FUNICULAR = 7
    TROLLEYBUS = 11
    MONORAIL = 12


@s.seared
class Route(s.Seared):
    '''
    A GTFS dataclass model for records found in `routes.txt`. Identifies a 
    transit route.
    
    Attributes:
        id (str):
            the unique ID of the route
        agency_id (str):
            the unique ID of the agency the route belongs to
        color (str):
            the color associated with the route
        desc (Optional[str]):
            a description of the route
        dropoffs (StopContinuity):
            the continuity of dropoffs along the route
        long_name (Optional[str]):
            the full name of the route
        name (str):
            the name of the route
        network_id (Optional[str]):
            the unique ID of the network the route belongs to
        pickups (StopContinuity):
            the continuity of pickups along the route
        short_name (Optional[str]):
            the short name of the route
        sort_idx (int):
            the sort position index of the route
        text_color (str):
            the color to use for text drawn against `Route.color`
        type (TransitType):
            the `TransitType` of the route
        url (Optional[str]):
            the URL of a webpage about the route
    '''

    ### ATTRIBUTES ###
    # Model ID
    id: str = s.Str(data_key='route_id', required=True)
    '''the unique ID of the route'''
    
    # Foreign IDs
    agency_id: str = s.Str(missing='')
    '''the unique ID of the agency the route belongs to'''
    network_id: Optional[str] = s.Str()
    '''the unique ID of the network the route belongs to'''

    # Required fields
    color: str = s.Str(data_key='route_color', missing='FFFFFF', required=True)
    '''the color associated with the route'''
    dropoffs: StopContinuity = s.Enum(
        enum=StopContinuity, 
        missing=StopContinuity.NONE
    )
    '''the continuity of dropoffs along the route'''
    pickups: StopContinuity = s.Enum(
        enum=StopContinuity, 
        missing=StopContinuity.NONE
    )
    '''the continuity of pickups along the route'''
    sort_idx: int = s.Int(data_key='route_sort_order', missing=0)
    '''the sort position index of the route'''
    text_color: Optional[str] = s.Str(
        data_key='route_text_color', missing='000000'
    )
    '''the color to use for text drawn against `Route.color`'''
    type: TransitType = s.Enum(
        data_key='route_type', enum=TransitType, required=True
    )
    '''the `TransitType` of the route'''

    # Optional fields
    desc: Optional[str] = s.Str(data_key='route_desc')
    '''a description of the route'''
    long_name: Optional[str] = s.Str(data_key='route_long_name')
    '''the full name of the route'''
    short_name: Optional[str] = s.Str(data_key='route_short_name')
    '''the short name of the route'''
    url: Optional[str] = s.Str(data_key='route_url')
    '''the URL of a web page about the route'''


    ### PROPERTIES ###
    @property
    def name (self) -> str:
        '''the name of the route'''
        return self.short_name if self.long_name is None else self.long_name