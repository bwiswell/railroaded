from __future__ import annotations

import seared as s

from .shape_point import ShapePoint


@s.seared
class Shape(s.Seared):
    '''
    A GTFS dataclass model grouping all ``ShapePoint`` records for a single
    shape into an ordered polyline.

    Attributes:
        id (str):
            the unique ID of the shape
        points (list[ShapePoint]):
            the ordered list of shape points (sorted by sequence)
    '''

    ### ATTRIBUTES ###
    id: str = s.Str(data_key='shape_id', required=True)
    '''the unique ID of the shape'''
    points: list[ShapePoint] = s.T(
        schema=ShapePoint.SCHEMA,
        many=True,
        required=True,
    )
    '''the ordered list of shape points (sorted by sequence)'''
