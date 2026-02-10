from typing import Any, Callable, Optional, TypeVar

from marshmallow import Schema
import pandas as pd


def load_list (
                path: str, 
                schema: Schema,
                int_cols: Optional[list[str]] = [],
                float_cols: Optional[list[str]] = []
            ) -> list:
        '''
        Reads a CSV file and returns a list of deserialized records.

        Parameters:
            path (str):
                the path of the CSV file to load data from
            schema (marshmallow.Schema):
                the Schema for the records in the CSV file

        Returns:
            records (list[T]):
                a list of deserialized records
        '''
        delim = ','
        with open(path, 'r') as file:
            header = file.readline()
            two = header.split(',')[1]
            if two.startswith(' '): delim = ', '

        df = pd.read_csv(
            path, 
            dtype=str, 
            delimiter=delim, 
            engine='python' if len(delim) > 0 else None
        )

        for col in float_cols:
            if not col in df.columns: continue
            df[col] = pd.to_numeric(
                df[col], errors='coerce', downcast='float'
            )
        for col in int_cols:
            if not col in df.columns: continue
            df[col] = pd.to_numeric(
                df[col], errors='coerce', downcast='integer'
            )

        df = df.fillna('').replace([''], [None])

        json = df.to_dict(orient='records')

        return schema.load(
            [
                {
                    k: v 
                    for k, v in j.items() 
                    if v != None
                }
                for j in json
            ],
            many=True
        )


T = TypeVar('T', Any, object)

def split (
            elements: list[T], 
            filter: Callable[[T], bool]
        ) -> tuple[list[T], list[T]]:
    '''
    Splits a `list` of `T` into two `list` of `T` containing all values in
    `elements` for which `filter` returns `True` in the first `list` and all
    values in `elements` for which `filter` returns `False` in the second.

    Parameters:
        elements (list[T]):
            the `list` of `T` elements to split
        filter (Callable[[T], bool]):
            a function that takes a single element as a parameter and returns a
            `bool` indicating which output `list` to sort the element into

    Returns:
        splits (tuple[list[T], list[T]]):
            a `tuple` of two `list` of `T` containing all values in `elements`
            for which `filter` returns `True` in the first `list` and all
            values in `elements` for which `filter` returns `False` in the
            second
    '''
    truthy: list[T] = []
    falsy: list[T] = []
    for el in elements:
        truthy.append(el) if filter(el) else falsy.append(el)
    return truthy, falsy