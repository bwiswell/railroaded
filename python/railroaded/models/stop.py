from enum import Enum
from typing import Optional

import seared as s

from .accessibility import Accessibility


class LocationType(Enum):
    '''
    An `Enum` describing the nature of a transit location.
    '''
    STOP_OR_PLATFORM = 0
    STATION = 1
    ENTRANCE_OR_EXIT = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4


@s.seared
class Stop(s.Seared):
    '''
    A GTFS dataclass model for records found in `stops.txt`. Identifies a 
    transit location: a stop/platform, station, entrance/exit, generic node or 
    boarding area (see `LocationType`).

    Attributes:
        id (str):
            the unique ID of the transit location
        level_id (Optional[str]):
            the unique ID of the level of the transit location
        parent_id (Optional[str]):
            the unique ID of the transit location's parent
        zone_id (Optional[str]):
            the unique ID of the fare zone ID of the transit location
        accessibility (Accessibility):
            the `Accessibility` of the transit location for wheelchair \
            boardings
        code (Optional[str]):
            a short text/number identifying the transit location for riders
        desc (Optional[str]):
            a description of the transit location
        lat (Optional[float]):
            the latitude of the transit location
        lon (Optional[float]):
            the longitude of the transit location
        name (str):
            the name of the transit location
        platform_code (Optional[str]):
            the unique ID of the platform to stop at
        timezone (Optional[str]):
            the timezone of the transit location
        tts_name (Optional[str]):
            a text-to-speech readable version of the stop name
        type (LocationType):
            the `LocationType` of the transit location
        url (Optional[str]):
            the URL of a web page about the transit location
    '''
    
    ### ATTRIBUTES ###
    # Model ID
    id: str = s.Str(data_key='stop_id', required=True)
    '''the unique ID of the transit location'''

    # Foreign IDs
    level_id: Optional[str] = s.Str()
    '''the unique ID of the level of the transit location'''
    parent_id: Optional[str] = s.Str()
    '''the unique ID of the transit location's parent'''
    zone_id: Optional[str] = s.Str()
    '''the unique ID of the fare zone of the transit location'''

    # Required fields
    accessibility: Accessibility = s.Enum(
        data_key='wheelchair_boarding',
        enum=Accessibility,
        missing=Accessibility.UNKNOWN
    )
    '''the `Accessibility` of the transit location for wheelchair boardings'''
    name: str = s.Str(data_key='stop_name', missing='unnamed')
    '''the name of the transit location'''
    type: LocationType = s.Enum(
        data_key='location_type', 
        enum=LocationType, 
        missing=LocationType.STOP_OR_PLATFORM
    )
    '''the `LocationType` of the transit location'''

    # Optional fields
    code: Optional[str] = s.Str(data_key='stop_code')
    '''a short text/number identifying the transit location for riders'''
    desc: Optional[str] = s.Str(data_key='stop_desc')
    '''a description of the transit location'''
    lat: Optional[float] = s.Float(data_key='stop_lat')
    '''the latitude of the transit location'''
    lon: Optional[float] = s.Float(data_key='stop_lon')
    '''the longitude of the transit location'''
    platform_code: Optional[str] = s.Str()
    '''the unique ID of the platform to stop at'''
    timezone: Optional[str] = s.Str(data_key='stop_timezone')
    '''the timezone of the transit location'''
    tts_name: Optional[str] = s.Str(data_key='tts_stop_name')
    '''a text-to-speech readable version of the stop name'''
    url: Optional[str] = s.Str(data_key='stop_url')
    '''the URL of a web page about the transit location'''