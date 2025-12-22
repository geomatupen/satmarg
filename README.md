# SatMarg - Satellite Overpass Predictor

**SatMarg** = Satellite + Marg (Sanskrit for "path" or "orbit")  
Predict satellite overpass times for any location easily and precisely.

## About SatMarg

SatMarg is an open source Python package designed to calculate satellite overpass predictions for specific locations and time periods. It uses real-time Two-Line Element (TLE) data to provide precise estimates of when satellites such as SENTINEL-2A, SENTINEL-2B, LANDSAT 8, and others will pass closest to a given latitude and longitude. SatMarg is built to be fast, simple, and customizable, allowing users to adjust processing speed and proximity angle according to their needs. It is ideal for applications such as satellite image planning, ground station scheduling, and general orbital analysis.

## Features

- Fetches real-time TLE data automatically from Celestrak.
- Predicts precise satellite overpass dates and times for a given latitude and longitude.
- Supports Sentinel-2A, Sentinel-2B, Sentinel-2C, Landsat 8/9, ISS, and more with TLE data available on Celestrak https://celestrak.org/NORAD/elements/resource.txt, https://celestrak.org/NORAD/elements/stations.txt
- Allows control of processing speed (slow, medium, fast) to balance between precision and performance.
- Allows customization of proximity angle detection (default is 0.5 degrees).
- Lightweight, fast, and easy to use.

## Installation

```bash
pip install satmarg
```

## Usage

```python
from satmarg.core import get_precise_overpasses

# Basic usage
df = get_precise_overpasses(
    lat=27.7172,   # Kathmandu
    lon=85.3240
)
print(df)

# Advanced usage
df = get_precise_overpasses(
    lat=27.7172,
    lon=85.3240,
    start_date="2025-04-26", 
    end_date="2025-05-27", 
    timezone="Asia/Kathmandu",  #default: "UTC"
    satellites="SENTINEL-2A, SENTINEL-2B, SENTINEL-3A, LANDSAT 8", 
    max_angle_deg="0.7", # one angle for all satellite or custom angles for each eg. "0.7, 0.7, 0.5, 0.7",
    step_seconds=10,   # custom processing speed, default is 1. 
    output_format='json', 
)
print(df)
```

## Parameters

| Parameter       | Description                                                                                         | Default          |
|-----------------|-----------------------------------------------------------------------------------------------------|-----------------|
| `lat`           | Latitude in degrees.                                                                                | Required         |
| `lon`           | Longitude in degrees.                                                                               | Required         |
| `start_date`    | Start date in 'YYYY-MM-DD' format.  Timezone is specified on the parameter below. If not specified, default: UTC                                                               | Today     |
| `end_date`      | End date in 'YYYY-MM-DD' format.  Timezone is specified on the parameter below. default: UTC                                                                 | 30 days later    |
| `timezone`      | Optional timezone for local time conversion in IANA format (e.g., "Europe/Vienna"). If invalid, defaults to UTC with a warning. Local Time column is included in output only if timezone ≠ UTC. Check Supported Timezones section below. | "UTC"           |
| `satellites`    | Comma-separated list of satellites (example: "SENTINEL-2A, SENTINEL-2B") - limit 7 satellites. Check supported satellites section below. | SENTINEL-2A, SENTINEL-2B |
| `max_angle_deg` | Maximum distance (in degrees) from overhead to detect an overpass.                                  | "0.7" or comma separated values for each satellite (example: "0.5, 0.7, 0.6") |
| `step_seconds`  | Step interval for orbit simulation in seconds. Higher = faster but less precise.                    | 1               |
| `output_format` | Format of the returned overpass results. Options: `"json"` (default, returns JSON string), `"table"` (pandas DataFrame), or `"csv"` (saves results to CSV). | "json"          |

Notes:  
- `step_seconds = 1` for slow (high precision) and requires more processing power reduce it to lower values if it is taking too long,  
- `step_seconds = 2` for medium,  
- `step_seconds = 5` for fast (less precision). Or it can be custom steps like 3 or 7
- `Timezone`: When timezone is set, all the input and output dates are in user-defined time zone. "

## Output
You can control the output format using the output_format parameter. Available options are:

'json' (default): Returns the overpass results as a JSON string.

'table': Returns the results as a pandas DataFrame.

'csv': Saves the results directly to a CSV file (you can also specify a csv_filename).

## Example Output (json)
```
json [
  {
    "Date":"2026-01-02T22:16:24+05:45",
    "Timezone":"Asia\/Kathmandu",
    "Satellite":"SENTINEL-2B",
    "Lat (DEG)":27.6861089603,
    "Lon (DEG)":85.1511018967,
    "Sat. Azi. (deg)":263.7250417017,
    "Sat. Elev. (deg)":88.7969902437,
    "Range (km)":791.8631112307
  },
  {
    "Date":"2026-01-12T22:16:27+05:45",
    "Timezone":"Asia\/Kathmandu",
    "Satellite":"SENTINEL-2B",
    "Lat (DEG)":27.6401258516,
    "Lon (DEG)":85.1484809155,
    "Sat. Azi. (deg)":245.8365823306,
    "Sat. Elev. (deg)":88.665605964,
    "Range (km)":791.7747502366
  }
]
```

## Example Output (Table)

| Date               | Timezone        | Satellite    | Lat (DEG)   | Lon (DEG)   | Sat. Azi. (deg) | Sat. Elev. (deg) | Range (km) |
|--------------------------|----------------|--------------|------------|------------|-----------------|-----------------|------------|
| 2026-01-02T22:16:24+05:45 | Asia/Kathmandu | SENTINEL-2B  | 27.686109  | 85.151102  | 263.725042      | 88.796990       | 791.863111 |


## Supported Satellites

- LANDSAT 8
- LANDSAT 9
- SENTINEL-2A
- SENTINEL-2B
- SENTINEL-2C
- SENTINEL-3A
- SENTINEL-3B
- ISS (ZARYA)
- and more available on https://celestrak.org/NORAD/elements/resource.txt, https://celestrak.org/NORAD/elements/stations.txt

## Supported Timezones
- These are the valid timezones: https://raw.githubusercontent.com/geomatupen/satmarg/refs/heads/upen/Example/valid_timezones/valid_timezones.csv

## License

GNU GENERAL PUBLIC LICENSE

## Acknowledgements

- Skyfield: Precise astronomical computation library.
- Celestrak: Satellite TLE data provider.
- Special thanks to Termatics, Austria for providing the opportunity and support to develop this project.

