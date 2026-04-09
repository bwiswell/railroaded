from __future__ import annotations

from typing import Optional

import seared as s


@s.seared
class ShapePoint(s.Seared):
    '''
    A GTFS dataclass model for records found in ``shapes.txt``. Identifies a
    single point in the polyline geometry of a trip shape.

    Attributes:
        shape_id (str):
            the unique ID of the shape this point belongs to
        lat (float):
            the latitude of the shape point
        lon (float):
            the longitude of the shape point
        sequence (int):
            the sequence order of this point within its shape
        dist_traveled (Optional[float]):
            the distance traveled along the shape from its first point
    '''

    ### ATTRIBUTES ###
    shape_id: str = s.Str(required=True)
    '''the unique ID of the shape this point belongs to'''
    lat: float = s.Float(data_key='shape_pt_lat', required=True)
    '''the latitude of the shape point'''
    lon: float = s.Float(data_key='shape_pt_lon', required=True)
    '''the longitude of the shape point'''
    sequence: int = s.Int(data_key='shape_pt_sequence', required=True)
    '''the sequence order of this point within its shape'''
    dist_traveled: Optional[float] = s.Float(data_key='shape_dist_traveled')
    '''the distance traveled along the shape from its first point'''
