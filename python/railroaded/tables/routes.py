from __future__ import annotations

import os
from typing import Optional

import seared as s

from ..models import Route
from ..util import load_list


@s.seared
class Routes(s.Seared):
    '''
    Serializable dataclass table mapping `str` IDs to `Route` records.

    Attributes:
        data (dict[str, Route]):
            a `dict` mapping `str` IDs to `Route` records
        ids (list[str]):
            a `list` of all `str` IDs in the `Routes` table
        names (list[str]):
            a `list` of all `Route.name` values in the `Routes` table
        routes (list[Route]):
            a `list` of all `Route` records in the `Routes` table
    '''

    ### ATTRIBUTES ###
    # Required
    data: dict[str, Route] = s.T(
        schema=Route.SCHEMA,
        keyed=True,
        required=True
    )
    '''a `dict` mapping `str` IDs to `Route` records'''


    ### CLASS METHODS ###
    @classmethod
    def from_gtfs (cls, path: str) -> Routes:
        '''
        Returns an `Routes` table populated from the GTFS data at `path`.

        Parameters:
            path (str):
                the path to the GTFS dataset

        Returns:
            agencies (Routes):
                an `Routes` table populated from the GTFS data at `path`
        '''
        routes: list[Route] = load_list(
            path = os.path.join(path, 'routes.txt'),
            schema = Route.SCHEMA,
            int_cols=['route_type']
        )
        return Routes({ r.id: r for r in routes })


    ### PROPERTIES ###    
    @property
    def ids (self) -> list[str]:
        '''a `list` of all `str` IDs in the `Routes` table'''
        return list(self.data.keys())
    
    @property
    def names (self) -> list[str]:
        '''a `list` of all `Route.name` values in the `Routes` table'''
        return [r.name for r in self.routes]
    
    @property
    def routes (self) -> list[Route]:
        '''a `list` of all `Route` records in the `Routes` table'''
        return list(self.data.values())
    

    ### MAGIC METHODS ###
    def __getitem__ (self, id: str) -> Optional[Route]:
        '''
        Returns the `Route` record associated with the `id` if it exists,
        otherwise returns `None`.
        
        Parameters:
            id (str):
                the `str` id associated with the `Route` record to retrieve

        Returns:
            record (Optional[Route]):
                the `Route` record associated with `id` if it exists, otherwise 
                `None`
        '''
        return self.data.get(id, None)