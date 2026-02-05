from enum import Enum


class StopContinuity(Enum):
    '''
    An `Enum` describing the stop continuity of a route.
    '''
    CONTINUOUS = 0
    NONE = 1
    VIA_PHONE = 2
    VIA_DRIVER = 3