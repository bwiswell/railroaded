# railroaded — Codebase Reference

> Last updated: 2026-04-09 | Branch: version/0.3.0 | Version: **0.3.0**

---

## What This Project Does

`railroaded` is a dual-language (Python + TypeScript) library for fetching, parsing, and querying **GTFS (General Transit Feed Specification)** data. It converts verbose GTFS CSV datasets into a minified **mGTFS JSON** format for efficient local querying of transit information: agencies, routes, stops, trips, schedules, and (optionally) shape polyline geometry.

**Primary use case:** Download a GTFS ZIP (or load a local file), parse it into structured models, then query it — e.g., "what trips run on this route today?" or "what stops connect route A to route B?"

---

## Tech Stack

| Language | Key Dependencies | Build Tool |
|----------|-----------------|------------|
| Python 3.11+ | `pandas ^2.2.3`, `seared` (local path dep, `../../seared`) | Poetry |
| TypeScript 5.9.3 | `@zip.js/zip.js ^2.8.19`, `csv-parser ^3.2.0` | tsc |

**Dev dependencies:** `pytest ^8.0` (Python)

---

## Architecture

Both implementations mirror each other and follow a three-layer design:

```
GTFS (entry-point facade)
    └── Tables (collections of models, dict-based O(1) lookup by ID)
            └── Models (individual GTFS entities with seared serialisation)
                    └── Utils (CSV/ZIP loading, split helper)
```

### Models

| Model | GTFS Source File | Notes |
|-------|-----------------|-------|
| `Agency` | `agency.txt` | Transit agency metadata |
| `Feed` | `feed_info.txt` | Feed-level metadata; optional in GTFS spec |
| `Route` | `routes.txt` | Transit route definition |
| `Stop` | `stops.txt` | Physical stop/station |
| `Trip` | `trips.txt` | A single trip on a route |
| `StopTime` | `stop_times.txt` | Arrival/departure times per stop per trip |
| `Timetable` | (derived) | Ordered `stop_id → StopTime` map for a trip |
| `Schedule` | (derived) | Date-range + day-of-week service calendar |
| `DateRange` | `calendar.txt` | One weekly-schedule entry with inclusive date bounds |
| `Calendar` | `calendar.txt` | Recurring day-of-week record (parsed into `DateRange`) |
| `CalendarDate` | `calendar_dates.txt` | One-off schedule additions/exceptions |
| `ShapePoint` | `shapes.txt` | One point in a shape polyline (lat, lon, sequence) |
| `Shape` | `shapes.txt` | Ordered polyline of `ShapePoint` records for a single shape_id |

### Tables

| Table | Stores | Key methods |
|-------|--------|-------------|
| `Agencies` | `dict[str, Agency]` | `ids`, `agencies`, `__getitem__` |
| `Routes` | `dict[str, Route]` | `ids`, `routes`, `__getitem__` |
| `Stops` | `dict[str, Stop]` | `ids`, `stops`, `__getitem__` |
| `Trips` | `dict[str, Trip]` | `ids`, `trips`, filter by route/stop/date/time |
| `Schedules` | `dict[str, Schedule]` | `service_ids`, `on_date()`, `__getitem__` |
| `Shapes` | `dict[str, Shape]` | `ids`, `shapes`, `__getitem__`; opt-in via `shapes=True` on `GTFS.read()` |

### Entry Point: `GTFS` class

| Method | Signature | Purpose |
|--------|-----------|---------|
| `read` | `(name, gtfs_path?, gtfs_sub?, gtfs_uri?, mgtfs_path?, shapes=False)` | Download/extract/parse GTFS or load mGTFS JSON cache; `shapes=True` loads shapes.txt polyline geometry |
| `save` | `(gtfs, mgtfs_path)` | Serialise to mGTFS JSON file |
| `on_date` | `(date)` | Filter trips active on a given calendar date |
| `today` | `()` | Shorthand for `on_date(date.today())` |
| `on_route` | `(route_id)` | Filter trips on a route |
| `through` | `(stop_id)` | Filter trips through a stop |
| `connecting` | `(stop_a_id, stop_b_id)` | Filter trips passing both stops in order |
| `between` | `(start: datetime, end: datetime)` | Filter trips whose real datetime range overlaps the window |

---

## File Structure

```
railroaded/
├── CODEBASE.md
├── python/
│   ├── pyproject.toml               # Python 3.11+, version 0.2.1
│   ├── poetry.lock
│   ├── railroaded/
│   │   ├── __init__.py              # Package init, version string
│   │   ├── gtfs.py                  # GTFS facade class
│   │   ├── util.py                  # load_list() (CSV→schema.load), split()
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── accessibility.py     # Accessibility enum
│   │   │   ├── agency.py            # Agency model
│   │   │   ├── calendar.py          # Calendar + weekday schedule list
│   │   │   ├── calendar_date.py     # CalendarDate + ExceptionType enum
│   │   │   ├── date_range.py        # DateRange model
│   │   │   ├── feed.py              # Feed (optional feed_info.txt)
│   │   │   ├── route.py             # Route + TransitType enum
│   │   │   ├── schedule.py          # Schedule: active() + date-range aggregation
│   │   │   ├── shape.py             # Shape: ordered polyline of ShapePoints
│   │   │   ├── shape_point.py       # ShapePoint: one lat/lon/sequence point
│   │   │   ├── stop.py              # Stop + LocationType enum
│   │   │   ├── stop_continuity.py   # StopContinuity enum
│   │   │   ├── stop_time.py         # StopTime + GTFS time parsing (hours >= 24)
│   │   │   ├── timetable.py         # Timetable: ordered stop->StopTime map
│   │   │   └── trip.py              # Trip + BikesAllowed enum
│   │   └── tables/
│   │       ├── __init__.py
│   │       ├── agencies.py
│   │       ├── routes.py
│   │       ├── schedules.py         # Handles missing calendar.txt / calendar_dates.txt
│   │       ├── shapes.py            # Shapes: groups ShapePoints by shape_id; from_gtfs()
│   │       ├── stops.py
│   │       └── trips.py
│   └── tests/
│       ├── conftest.py              # Session-scoped SEPTA fixture (downloads + mGTFS cache)
│       ├── septa_cache.json         # mGTFS cache (gitignored, generated on first run)
│       ├── test_gtfs.py             # 31 integration tests
│       ├── test_patco.py            # 16 PATCO integration tests
│       └── test_shapes.py           # 14 shapes.txt tests (opt-in, serialisation, backward compat)
├── typescript/
│   └── src/
│       ├── gtfs.ts                  # GTFS facade class
│       ├── index.ts
│       ├── models/                  # TS equivalents of Python models
│       ├── tables/
│       ├── types/
│       └── util/
│           ├── csv.ts
│           ├── date.ts
│           ├── parse.ts
│           ├── unique.ts            # O(1) Set-based deduplication
│           └── unzip.ts
├── package.json                     # version 0.2.1
└── tsconfig.json
```

---

## Opt-in shapes.txt support

`GTFS.read(..., shapes=True)` loads `shapes.txt` (polyline geometry for each trip's geographic path) into a `Shapes` table. When `shapes=False` (default), the table is empty, keeping memory and mGTFS cache size minimal.

```python
# Without shapes (default — lightweight)
gtfs = rr.GTFS.read(name='SEPTA', gtfs_uri=uri, mgtfs_path=cache)

# With shapes (for map rendering)
gtfs = rr.GTFS.read(name='SEPTA', gtfs_uri=uri, mgtfs_path=cache, shapes=True)

# Access shape geometry for a trip
shape = gtfs.shapes[trip.shape_id]
if shape:
    for pt in shape.points:
        print(pt.lat, pt.lon, pt.sequence)
```

The mGTFS cache includes shapes data only when originally saved with shapes loaded. Existing caches without a `shapes` key load with an empty table (backward compatible). Feeds that lack `shapes.txt` also produce an empty table regardless of the flag.

---

## `between()` — date-aware datetime filtering

`GTFS.between(start: datetime, end: datetime)` uses **both** the date and time portions of the arguments.

### Date handling
Only trips whose service schedule is active on a date within (or one day before) the query window are considered. The one-day look-back captures overnight trips whose service date is the calendar day before the window starts but whose real running time extends into the window.

### Overnight trip handling
GTFS encodes times past midnight as hours ≥ 24 (e.g. `25:30` = 01:30 the following day). `StopTime.end_offset` / `start_offset` flag these crossings. `Timetable.between_datetime()` anchors each trip to its `service_date`:

```python
real_end = datetime.combine(service_date, timetable.end.end_time)
if timetable.end.end_offset:
    real_end += timedelta(days=1)
```

Overlap check: `real_start <= end and real_end >= start`.

### Implementation layers
- `Timetable.between_datetime(service_date, start, end)` — computes real datetimes and checks overlap
- `Trip.between_datetime(service_date, start, end)` — delegates to timetable
- `GTFS.between(start, end)` — builds candidate service dates (prev_day … end_date), resolves active service IDs via `schedules.on_date()`, calls `trip.between_datetime()` per match

### Chaining
```python
gtfs.on_date(date(2026, 4, 7)).between(
    datetime(2026, 4, 7, 8, 0),
    datetime(2026, 4, 7, 9, 0)
)
```

---

## Testing

Tests live in `python/tests/` and use SEPTA regional rail GTFS data.

```sh
cd python
poetry run pytest tests/ -v
```

The session-scoped `septa` fixture downloads the GTFS feed on the first run and writes a minified mGTFS JSON cache (`tests/septa_cache.json`, gitignored). Subsequent runs load from the JSON cache via `GTFS.read(mgtfs_path=...)` — no network access required after the first run. No pickle is used.

### Test classes

| Class | Coverage |
|-------|----------|
| `TestLoad` | Feed loads, tables populated, version string |
| `TestTimetable` | First-stop regression, ordering, time parsing |
| `TestOnDate` | Date filtering, `today()` |
| `TestOnRoute` | Route filtering, unknown route |
| `TestThrough` | Stop filtering, unknown stop |
| `TestConnecting` | README example, directional correctness |
| `TestBetween` | `datetime` acceptance, window narrowing, date-awareness, overnight trips |

---

## Bug History

All issues from the initial code review were resolved in 0.2.1. A further seared serialisation issue was resolved in the seared 0.2.0 dependency upgrade.

### Resolved in 0.2.1

| # | Severity | Location | Description |
|---|----------|----------|-------------|
| 1 | Critical | `trips.py:62` | First stop of each trip silently dropped (`= []` → `= [stop]`) |
| 2 | Critical | `stop_time.py` | `seconds=` kwarg typo (`→ second=`) and wrong hour formula (`(>=24)%24` → `int%24`) |
| 3 | Critical | `timetable.py:115` | `between()` compared `StopTime` objects to `time` (`.start_time` / `.end_time` required) |
| 4 | Critical | `stopTime.ts:106-107` | Unsafe `!` assertions on nullable time fields |
| 5 | Critical | `schedule.ts:91` | Wrong weekday index formula for JS Sunday-first mapping |
| 6 | High | `trips.py:71` | `KeyError` for trips with no stop times (`→ .get(id, [])`) |
| 7 | High | `feed.py` | Crash if `feed_info.txt` absent |
| 8 | High | `schedules.py` | Crash if `calendar.txt` or `calendar_dates.txt` absent |
| 9 | High | `schedule.py` | `min()`/`max()` crash on empty ranges list |
| 10 | High | `gtfs.py` | `between()` typed as `date` but used as `datetime` |
| 11 | Medium | `timetable.py` | Loop variable `s` shadowed `seared as s` import |
| 12 | Medium | Multiple | Date format `%Y-%m-%d` didn't match GTFS `YYYYMMDD` |
| 13 | Medium | `timetable.ts` | Unsafe `stop_id!` assertion |
| 14 | Low | `unique.ts` | O(n²) `indexOf` deduplication → `Set` |
| 15 | Low | Multiple | Version mismatch across `__init__.py`, `pyproject.toml`, `package.json` |
| 16 | Low | `pyproject.toml` | Python constraint `^3.9` → `^3.11`; dev-dep section modernised |

### Resolved via seared 0.2.0 upgrade

| # | Description |
|---|-------------|
| S1 | `T(keyed=True)` dump produced empty dicts — `Function` field received parent object instead of individual dict values |
| S2 | `T(many=True)` dump produced `[{}, ...]` — same `Function` issue for list items |
| S3 | `Enum(many=True)` dump raised `AttributeError` |
| S4 | `NDArray(many=True)` dump corrupted on repeated calls (shared counter) |
| S5 | All seared fields used deprecated `missing=` kwarg |
| S6 | Classes with `__getitem__` produced empty dumps — marshmallow used `obj[key]` instead of `getattr(obj, key)`; fixed via `BaseSchema.get_attribute` override |

---

## Known Limitations

- No ZIP-slip protection when extracting remote GTFS archives (`gtfs.py`)
- `urlretrieve()` has no timeout or file-size limit
- TypeScript implementation has no test suite
- Some non-null assertions (`!`) remain in TypeScript tables/util (low risk — data validated upstream)
- `Timetable.between(start: time, end: time)` and `Trip.between(...)` do not handle overnight trips correctly; use `GTFS.between(datetime, datetime)` for all production queries
- Shapes support is Python-only; TypeScript implementation does not yet parse `shapes.txt`
