# railroaded

`railroaded` is a lightweight Python package designed for fetching, parsing, and stripping down General Transit Feed Specification (GTFS) data to provide speedy Pythonic handling and querying about route, trip, and schedule information in a local context. No more messy and cross-referential GTFS datasets full of `.csv` files or SQL-based ORM libraries - just use `rr.fetch_gtfs` to fetch, parse, and transform your favorite transit agency's GTFS feed into a clean and monolithic `.json`-based mGTFS (Minified General Transit Feed Specification) dataset in seconds.

## Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)

## Overview

### MGTFS
`railroaded` prioritizes I/O and query speed for journey planning via GTFS data, ignoring and discarding GTFS data other than agencies, routes, schedules, stops, and trips.

Typical GTFS data consists of a `.zip` of many `.csv` files, each containing a database table:

```txt
gtfs.zip
    agency.csv
    calendar.csv
    calendar_dates.csv
    ...
```

mGTFS is a minimal representation of the parts of these tables relevant to queries about agency, route, schedule, stop, and trip stored in a single `.json` file.


## Setup
```sh
poetry add git+https://www.github.com/bwiswell/railroaded.git
```

## Usage

`rr.GTFS` is the root object for handling GTFS data. The `rr.GTFS` object can be created from local or remote sources using `rr.GTFS.read`, and automatically handles parsing and converting the GTFS dataset to mGTFS. The resulting `rr.GTFS` object can be written out to a `.json` file using `rr.GTFS.save`.

#### Reading with `rr.GTFS.read`

If using a local mGTFS resource (preferred), `mgtfs_path` must be provided. If `mgtfs_path` is provided and no existing mGTFS dataset is found at the specified location, reading falls back to the options below. If reading is successful using one of those options, the minified version of the retrieved data will be saved to `mgtfs_path` to improve subsequent read times.

If using a local GTFS resource, `gtfs_path` must be provided. The GTFS data should already be unzipped.

If using a remote resource, `gtfs_uri` must be provided. `gtfs_sub` can optionally be provided to specify a subdirectory of the remote resource. `rr.GTFS.read` expects remote resources to be `.zip` files, or a `.zip` file of `.zip` files.

```python
import railroaded as r

gtfs = rr.GTFS.read(
    name = 'your-dataset-name',                         # Name of the GTFS dataset
    gtfs_path = 'path/to/gtfs/data',                    # Optional, local path to the GTFS dataset
    gtfs_sub = 'subdirectory',                          # Optional, for nested GTFS datasets
    gtfs_uri = 'https://www.example.com/gtfs/data.zip', # Optional, URI of the GTFS dataset
    mgtfs_path = 'path/to/minified/gtfs/data'           # Optional, local path to the mGTFS dataset
)
```

## Example
```python
import railroaded as rr

JEFFERSON_STATION = '90006'
WASHINGTON_LANE_STATION = '90714'
URI = 'https://www3.septa.org/developer/gtfs_public.zip'

g = rr.GTFS.read('SEPTA', gtfs_uri=URI, gtfs_sub='google_rail')

g = g.today().connecting(JEFFERSON_STATION, WASHINGTON_LANE_STATION)

for trip in g.trips.trips:
    print(trip.id)
```