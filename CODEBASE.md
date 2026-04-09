# Railroaded — Codebase Overview

> Last updated: 2026-04-08 | Branch: version/0.2.1 | Current version: **0.2.1**

---

## What This Project Does

`railroaded` is a dual-language (Python + TypeScript) library for fetching, parsing, and querying **GTFS (General Transit Feed Specification)** data. It converts verbose GTFS CSV datasets into a minified **mGTFS JSON** format for efficient local querying of transit information: agencies, routes, stops, trips, and schedules.

**Primary use case:** Download a GTFS ZIP (or load a local file), parse it into structured models, then query it — e.g., "what trips run on this route today?" or "what stops connect route A to route B?"

---

## Tech Stack

| Language | Key Dependencies | Build Tool |
|----------|-----------------|------------|
| Python 3.11+ | `pandas ^2.2.3`, `seared` (git dep, marshmallow-based) | Poetry |
| TypeScript 5.9.3 | `@zip.js/zip.js ^2.8.19`, `csv-parser ^3.2.0` | tsc |

**Dev dependencies:** `pytest ^8.0` (Python)

---

## Architecture

Both implementations mirror each other and follow a three-layer design:

```
GTFS (entry point facade)
    └── Tables (collections of models, dict-based O(1) lookup)
            └── Models (individual GTFS entities with serialization)
                    └── Utils (CSV parsing, ZIP extraction, date/time helpers)
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
| `Timetable` | (derived) | Ordered stop→StopTime map for a trip |
| `Schedule` | (derived) | Date-range + day-of-week service calendar |
| `DateRange` | `calendar.txt` | Service active date ranges |
| `Calendar` | `calendar.txt` | Recurring day-of-week schedules |
| `CalendarDate` | `calendar_dates.txt` | One-off schedule additions/exceptions |

### Tables

| Table | Stores | Key Methods |
|-------|--------|-------------|
| `Agencies` | `Agency[]` | By ID |
| `Routes` | `Route[]` | By ID |
| `Stops` | `Stop[]` | By ID |
| `Trips` | `Trip[]` | By ID; filter by route, stop, date, time window |
| `Schedules` | `Schedule[]` | By service ID; filter by date |

### Entry Point: `GTFS` class

Methods:
- `read(name, gtfs_path, gtfs_sub, gtfs_uri, mgtfs_path)` — download/extract/parse GTFS or load mGTFS JSON
- `save(gtfs, mgtfs_path)` — write mGTFS JSON to disk
- `between(start: datetime, end: datetime)` — filter trips with timetables overlapping the window (time component used; date ignored)
- `connecting(stop_a_id, stop_b_id)` — find trips that pass through both stops in order
- `on_date(date)` — filter trips active on a given date
- `on_route(route_id)` — filter trips on a route
- `through(stop_id)` — filter trips through a stop
- `today()` — shorthand for `on_date(date.today())`

---

## File Structure

```
railroaded/
├── python/
│   └── railroaded/
│       ├── __init__.py          # Package init, version string
│       ├── gtfs.py              # GTFS facade class
│       ├── models/
│       │   ├── agency.py
│       │   ├── calendar.py      # Calendar + weekday schedule list
│       │   ├── calendar_date.py # CalendarDate + ExceptionType enum
│       │   ├── date_range.py    # DateRange model
│       │   ├── feed.py          # Feed (optional feed_info.txt)
│       │   ├── route.py
│       │   ├── schedule.py      # Schedule: active() + date range aggregation
│       │   ├── stop.py
│       │   ├── stop_time.py     # StopTime + time parsing
│       │   ├── timetable.py     # Timetable (ordered stop→StopTime)
│       │   └── trip.py
│       ├── tables/
│       │   ├── agencies.py
│       │   ├── routes.py
│       │   ├── schedules.py     # Handles missing calendar.txt / calendar_dates.txt
│       │   ├── stops.py
│       │   └── trips.py
│       └── util.py              # CSV loading, type helpers, file-existence checks
│   └── tests/
│       ├── conftest.py          # Session-scoped SEPTA fixture (downloads + caches)
│       └── test_gtfs.py         # Integration tests (26 tests)
├── typescript/
│   └── src/
│       ├── gtfs.ts              # GTFS facade class
│       ├── index.ts
│       ├── models/
│       │   ├── agency.ts
│       │   ├── calendar.ts      # (TS equivalent)
│       │   ├── dateRange.ts
│       │   ├── feed.ts
│       │   ├── route.ts
│       │   ├── schedule.ts      # active() with corrected weekday formula
│       │   ├── stop.ts
│       │   ├── stopTime.ts      # StopTime with null-safe time parsing
│       │   ├── timetable.ts     # fromGTFS skips stops with null stop_id
│       │   └── trip.ts
│       ├── tables/
│       │   └── ...
│       ├── types/
│       │   └── ...
│       └── util/
│           ├── csv.ts
│           ├── date.ts
│           ├── parse.ts
│           ├── unique.ts        # O(1) Set-based deduplication
│           └── unzip.ts
├── pyproject.toml               # Python 3.11+, version 0.2.1
├── package.json                 # version 0.2.1
└── tsconfig.json
```

---

## `between()` — datetime vs time resolution

The `GTFS.between()` facade method accepts **`datetime` objects** (combining date + time). The underlying tables (`Trips`, `Trip`, `Timetable`) work with Python `time` objects. The conflict is resolved in `gtfs.py` by extracting the time component before delegating:

```python
def between(self, start: datetime, end: datetime) -> GTFS:
    return self._ref(self.trips.between(start.time(), end.time()))
```

This means `between()` ignores the date part of the arguments. To restrict to a specific day, chain with `on_date()`:

```python
gtfs.on_date(date(2025, 1, 6)).between(
    datetime(2025, 1, 6, 8, 0),
    datetime(2025, 1, 6, 9, 0)
)
```

---

## Testing

Tests live in `python/tests/` and use SEPTA regional rail GTFS data.

```sh
cd python
poetry run pytest tests/ -v
```

The session-scoped `septa` fixture downloads the GTFS feed on the first run and writes a cache file (`tests/septa_cache.json`) so subsequent runs skip the network download.

**Test classes:**

| Class | Coverage |
|-------|----------|
| `TestLoad` | Feed loads, tables populated, version string |
| `TestTimetable` | First-stop regression, ordering, time parsing |
| `TestOnDate` | Date filtering, `today()` |
| `TestOnRoute` | Route filtering, unknown route |
| `TestThrough` | Stop filtering, unknown stop |
| `TestConnecting` | README example, directional correctness |
| `TestBetween` | `datetime` acceptance, window narrowing, date-independence |

---

## Issues Resolved in 0.2.1

All issues from the initial code review have been fixed:

### Critical (were blockers)

1. **[Python] `trips.py:62` — first stop of each trip silently dropped**
   - `stop_times[stop.trip_id] = []` → `= [stop]`

2. **[Python] `stop_time.py` — `seconds=` kwarg + wrong hour formula**
   - `seconds=` → `second=` (Python `time()` constructor parameter name)
   - `(int(t[:2]) >= 24) % 24` → `int(t[:2]) % 24`

3. **[Python] `timetable.py:115` — `between()` compared `StopTime` objects to `time`**
   - `self.start <= end` → `self.start.start_time <= end`
   - `self.end >= start` → `self.end.end_time >= start`

4. **[TypeScript] `stopTime.ts:106-107` — unsafe `!` assertions on nullable time fields**
   - Added explicit null check; throws descriptive error if both time fields are absent

5. **[TypeScript] `schedule.ts:91` — wrong weekday index formula**
   - `(date.getDay() - 1) % 7` → `(date.getDay() + 6) % 7`
   - Maps JS Sunday=0 correctly to GTFS Mon-first index 6

### High

6. **[Python] `trips.py:71` — `KeyError` for trips with no stop times**
   - `stop_times[trip.id]` → `stop_times.get(trip.id, [])`

7. **[Python] `feed.py` — crash if `feed_info.txt` absent or empty**
   - `Feed.from_gtfs()` now returns `Optional[Feed]`, handles missing file gracefully

8. **[Python] `schedules.py` — crash if `calendar.txt` or `calendar_dates.txt` absent**
   - Both files now loaded with `required=False`

9. **[Python] `schedule.py:94,99` — `min()`/`max()` crash on empty ranges list**
   - Guard added: returns `None` if `self.ranges` is empty

10. **[Python] `gtfs.py` — `between()` typed as `date` but passed to `time`-typed tables**
    - Signature changed to `datetime`; delegates `start.time()` / `end.time()` downstream

### Medium / Low

11. **[Python] `timetable.py:52` — loop variable `s` shadowed `seared as s` import**
    - Renamed to `st`

12. **[Python/TS] Date format `%Y-%m-%d` didn't match GTFS `YYYYMMDD` format**
    - Fixed in `calendar.py`, `calendar_date.py`, `feed.py` → `format='%Y%m%d'`

13. **[TypeScript] `timetable.ts:41` — unsafe `stop_id!` assertion**
    - Null `stop_id` stops are now skipped during `fromGTFS()`

14. **[TypeScript] `unique.ts` — O(n²) `indexOf` deduplication**
    - Replaced with `[...new Set(data)]`

15. **Version mismatch** — `__init__.py` said `0.1.5`, pyproject.toml/package.json said `0.2.0`
    - All three now read `0.2.1`

16. **`pyproject.toml`** — Python constraint updated `^3.9` → `^3.11` to match `seared` requirement; dev dependency section modernised to `[tool.poetry.group.dev.dependencies]`

---

## Remaining Known Limitations

- No ZIP-slip protection when extracting remote GTFS archives (`gtfs.py:121-130`)
- `urlretrieve()` has no timeout or file-size limit
- TypeScript has no test suite
- Some non-null assertions (`!`) remain in TypeScript tables/util (low risk — data validated upstream)
