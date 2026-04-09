from __future__ import annotations

import os
from typing import Optional

import seared as s

from ..models import Shape, ShapePoint
from ..util import load_list


@s.seared
class Shapes(s.Seared):
    '''
    Serializable dataclass table mapping ``str`` IDs to ``Shape`` records.

    Each ``Shape`` contains an ordered polyline of ``ShapePoint`` records
    representing the geographic path of a trip.

    Attributes:
        data (dict[str, Shape]):
            a ``dict`` mapping ``str`` shape IDs to ``Shape`` records
        ids (list[str]):
            a ``list`` of all ``str`` shape IDs
        shapes (list[Shape]):
            a ``list`` of all ``Shape`` records
    '''

    ### ATTRIBUTES ###
    data: dict[str, Shape] = s.T(
        schema=Shape.SCHEMA,
        keyed=True,
        required=True,
    )
    '''a ``dict`` mapping ``str`` shape IDs to ``Shape`` records'''


    ### CLASS METHODS ###
    @classmethod
    def from_gtfs(cls, path: str) -> Shapes:
        '''
        Returns a ``Shapes`` table populated from the GTFS data at ``path``.

        Reads ``shapes.txt``, groups points by ``shape_id``, sorts each group
        by ``shape_pt_sequence``, and wraps them in ``Shape`` objects.

        If ``shapes.txt`` is absent, returns an empty table.

        Parameters:
            path (str):
                the path to the GTFS dataset

        Returns:
            shapes (Shapes):
                a ``Shapes`` table populated from the GTFS data at ``path``
        '''
        points: list[ShapePoint] = load_list(
            os.path.join(path, 'shapes.txt'),
            ShapePoint.SCHEMA,
            int_cols=['shape_pt_sequence'],
            float_cols=['shape_pt_lat', 'shape_pt_lon', 'shape_dist_traveled'],
            required=False,
        )

        by_id: dict[str, list[ShapePoint]] = {}
        for pt in points:
            by_id.setdefault(pt.shape_id, []).append(pt)

        return Shapes({
            sid: Shape(
                id=sid,
                points=sorted(pts, key=lambda p: p.sequence),
            )
            for sid, pts in by_id.items()
        })


    ### PROPERTIES ###
    @property
    def ids(self) -> list[str]:
        '''a ``list`` of all ``str`` shape IDs in the ``Shapes`` table'''
        return list(self.data.keys())

    @property
    def shapes(self) -> list[Shape]:
        '''a ``list`` of all ``Shape`` records in the ``Shapes`` table'''
        return list(self.data.values())


    ### MAGIC METHODS ###
    def __getitem__(self, id: str) -> Optional[Shape]:
        '''
        Returns the ``Shape`` record associated with ``id`` if it exists,
        otherwise returns ``None``.

        Parameters:
            id (str):
                the ``str`` id associated with the ``Shape`` record

        Returns:
            record (Optional[Shape]):
                the ``Shape`` record associated with ``id`` if it exists,
                otherwise ``None``
        '''
        return self.data.get(id, None)
