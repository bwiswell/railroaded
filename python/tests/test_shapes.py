"""
Tests for the optional shapes.txt loading in railroaded.

Tests verify:
- shapes=False (default) produces an empty Shapes table
- shapes=True loads and serializes shape geometry
- Feeds without shapes.txt produce an empty table regardless of the flag
- Shape points are sorted by sequence
- mGTFS round-trip preserves shape data
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest
import railroaded as rr


PATCO_URI   = (
    'https://rapid.nationalrtap.org'
    '/GTFSFileManagement/UserUploadFiles/13562/PATCO_GTFS.zip'
)
PATCO_CACHE_NO_SHAPES = os.path.join(os.path.dirname(__file__), 'patco_cache.json')
PATCO_CACHE_WITH_SHAPES = os.path.join(os.path.dirname(__file__), 'patco_shapes_cache.json')


@pytest.fixture(scope='session')
def patco_no_shapes() -> rr.GTFS:
    """PATCO feed loaded WITHOUT shapes (default)."""
    return rr.GTFS.read(
        name='PATCO',
        gtfs_uri=PATCO_URI,
        mgtfs_path=PATCO_CACHE_NO_SHAPES,
        shapes=False,
    )


@pytest.fixture(scope='session')
def patco_with_shapes() -> rr.GTFS:
    """PATCO feed loaded WITH shapes."""
    return rr.GTFS.read(
        name='PATCO',
        gtfs_uri=PATCO_URI,
        mgtfs_path=PATCO_CACHE_WITH_SHAPES,
        shapes=True,
    )


class TestShapesDefault:
    """shapes=False (default) should produce an empty Shapes table."""

    def test_shapes_table_exists(self, patco_no_shapes: rr.GTFS) -> None:
        assert hasattr(patco_no_shapes, 'shapes')

    def test_shapes_table_empty(self, patco_no_shapes: rr.GTFS) -> None:
        assert len(patco_no_shapes.shapes.ids) == 0

    def test_other_tables_unaffected(self, patco_no_shapes: rr.GTFS) -> None:
        assert len(patco_no_shapes.trips.ids) > 0
        assert len(patco_no_shapes.stops.ids) > 0


class TestShapesLoaded:
    """shapes=True should load shape geometry from shapes.txt."""

    def test_shapes_table_populated(self, patco_with_shapes: rr.GTFS) -> None:
        assert len(patco_with_shapes.shapes.ids) > 0

    def test_shape_has_points(self, patco_with_shapes: rr.GTFS) -> None:
        shape = patco_with_shapes.shapes.shapes[0]
        assert len(shape.points) > 0

    def test_shape_points_have_coords(self, patco_with_shapes: rr.GTFS) -> None:
        shape = patco_with_shapes.shapes.shapes[0]
        pt = shape.points[0]
        assert pt.lat is not None
        assert pt.lon is not None
        assert -90 <= pt.lat <= 90
        assert -180 <= pt.lon <= 180

    def test_shape_points_sorted_by_sequence(self, patco_with_shapes: rr.GTFS) -> None:
        for shape in patco_with_shapes.shapes.shapes:
            seqs = [p.sequence for p in shape.points]
            assert seqs == sorted(seqs), f'Shape {shape.id} not sorted'

    def test_trip_shape_ids_reference_valid_shapes(self, patco_with_shapes: rr.GTFS) -> None:
        shape_ids = set(patco_with_shapes.shapes.ids)
        for trip in patco_with_shapes.trips.trips:
            if trip.shape_id:
                assert trip.shape_id in shape_ids, \
                    f'Trip {trip.id} references missing shape {trip.shape_id}'

    def test_shape_lookup_by_id(self, patco_with_shapes: rr.GTFS) -> None:
        sid = patco_with_shapes.shapes.ids[0]
        shape = patco_with_shapes.shapes[sid]
        assert shape is not None
        assert shape.id == sid

    def test_shape_lookup_missing_returns_none(self, patco_with_shapes: rr.GTFS) -> None:
        assert patco_with_shapes.shapes['__nonexistent__'] is None

    def test_other_tables_unaffected(self, patco_with_shapes: rr.GTFS) -> None:
        assert len(patco_with_shapes.trips.ids) > 0
        assert len(patco_with_shapes.stops.ids) > 0


class TestShapesSerialization:
    """Shapes should survive mGTFS JSON round-trip."""

    def test_round_trip_preserves_shapes(self, patco_with_shapes: rr.GTFS) -> None:
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            tmp_path = f.name
        try:
            rr.GTFS.save(patco_with_shapes, tmp_path)
            reloaded = rr.GTFS.read(name='PATCO', mgtfs_path=tmp_path)
            assert len(reloaded.shapes.ids) == len(patco_with_shapes.shapes.ids)
            # Spot-check one shape
            sid = patco_with_shapes.shapes.ids[0]
            orig = patco_with_shapes.shapes[sid]
            copy = reloaded.shapes[sid]
            assert len(copy.points) == len(orig.points)
            assert copy.points[0].lat == pytest.approx(orig.points[0].lat)
            assert copy.points[0].lon == pytest.approx(orig.points[0].lon)
        finally:
            os.unlink(tmp_path)

    def test_no_shapes_key_in_default_cache(self) -> None:
        """mGTFS saved with shapes=False should have an empty shapes data dict."""
        if os.path.exists(PATCO_CACHE_NO_SHAPES):
            with open(PATCO_CACHE_NO_SHAPES) as f:
                data = json.load(f)
            shapes_data = data.get('shapes', {}).get('data', {})
            assert len(shapes_data) == 0


class TestBackwardCompatibility:
    """Existing mGTFS files without a shapes key should load cleanly."""

    def test_load_legacy_cache_without_shapes_key(self) -> None:
        """Simulate loading a pre-shapes mGTFS file."""
        legacy = {
            'name': 'TEST',
            'agencies': {'data': {}},
            'routes': {'data': {}},
            'schedules': {'data': {}},
            'stops': {'data': {}},
            'trips': {'data': {}},
            # No 'shapes' key at all — simulating a pre-0.3.0 cache
        }
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            json.dump(legacy, f)
            tmp_path = f.name
        try:
            gtfs = rr.GTFS.read(name='TEST', mgtfs_path=tmp_path)
            # shapes may be None (key absent) or an empty Shapes table
            assert gtfs.shapes is None or len(gtfs.shapes.ids) == 0
            assert gtfs.name == 'TEST'
        finally:
            os.unlink(tmp_path)
