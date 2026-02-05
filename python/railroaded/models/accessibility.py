from enum import Enum


class Accessibility(Enum):
    '''
    An `Enum` describing the accessibility of a transit location.
    '''
    UNKNOWN = 0
    ACCESSIBLE = 1
    INACCESSIBLE = 2