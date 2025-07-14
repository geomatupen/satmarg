# SatMarg - Satellite Overpass Predictor

**SatMarg** = Satellite + Marg (Sanskrit for "path" or "orbit")  
Predict satellite overpass times for any location easily and precisely.

## About SatMarg

SatMarg is an open source Python package designed to calculate satellite overpass predictions for specific locations and time periods. It uses real-time Two-Line Element (TLE) data to provide precise estimates of when satellites such as SENTINEL-2A, SENTINEL-2B, LANDSAT 8, and others will pass closest to a given latitude and longitude. SatMarg is built to be fast, simple, and customizable, allowing users to adjust processing speed and proximity angle according to their needs. It is ideal for applications such as satellite image planning, ground station scheduling, and general orbital analysis.

## Features

- Fetches real-time TLE data automatically from Celestrak.
- Predicts precise satellite overpass dates and times for a given latitude and longitude.
- Supports Sentinel-2A, Sentinel-2B, Sentinel-2C, Landsat 8/9, ISS, and more.
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
    satellites="SENTINEL-2A, SENTINEL-2B, SENTINEL-2C",
    step_seconds=10,   # custom processing speed
    max_angle_deg=1.0  # custom angle
    output_format='json', 
)
print(df)
```

## Parameters

| Parameter         | Description                                                                 | Default          |
| ----------------- | --------------------------------------------------------------------------- | ---------------- |
| `lat`             | Latitude in degrees.                                                        | Required         |
| `lon`             | Longitude in degrees.                                                       | Required         |
| `start_date`      | Start date in 'YYYY-MM-DD' format.                                           | Today (UTC)      |
| `end_date`        | End date in 'YYYY-MM-DD' format.                                             | 30 days later    |
| `satellites`      | Comma-separated list of satellites (example: "SENTINEL-2A, SENTINEL-2B").    | SENTINEL-2A, SENTINEL-2B |
| `step_seconds`    | Step interval for orbit simulation in seconds. Higher = faster but less precise. | 1               |
| `max_angle_deg`   | Maximum distance (in degrees) from overhead to detect an overpass.           | 0.5              |

Notes:  
- `step_seconds = 1` for slow (high precision) and requires more processing power reduce it to lower values if it is taking too long,  
- `step_seconds = 10` for medium,  
- `step_seconds = 20` for fast (less precision).

## Output
You can control the output format using the output_format parameter. Available options are:

'json' (default): Returns the overpass results as a JSON string.

'table': Returns the results as a pandas DataFrame.

'csv': Saves the results directly to a CSV file (you can also specify a csv_filename).

## Example Output (json)
```
json [
  {
    "date":"2025-05-04 16:31:35",
    "Satellite":"SENTINEL-2A",
    "Lat (DEG)":27.6669294714,
    "Lon (DEG)":85.1651872363,
    "Sat. Azi. (deg)":250.4505871228,
    "Sat. Elev. (deg)":88.6478414389,
    "Range (km)":792.0432268716
  },
  {
    "date":"2025-05-14 16:31:30",
    "Satellite":"SENTINEL-2A",
    "Lat (DEG)":27.6775444246,
    "Lon (DEG)":85.1847272958,
    "Sat. Azi. (deg)":252.283651294,
    "Sat. Elev. (deg)":88.82670104,
    "Range (km)":791.7672395546
  },
  {
    "date":"2025-05-24 16:31:21",
    "Satellite":"SENTINEL-2A",
    "Lat (DEG)":27.6959514525,
    "Lon (DEG)":85.2195412997,
    "Sat. Azi. (deg)":257.1430638378,
    "Sat. Elev. (deg)":89.1402328607,
    "Range (km)":791.6648527357
  }
]
```

## Example Output (Table)

| date                | Satellite    | Lat (DEG) | Lon (DEG) | Sat. Azi. (deg) | Sat. Elev. (deg) | Range (km) |
|---------------------|--------------|-----------|-----------|-----------------|-----------------|------------|
| 2025-04-27 05:14:11  | SENTINEL-2A  | 27.72     | 85.32     | 199.3           | 82.1             | 702.8      |

## Supported Satellites

- LANDSAT 8
- LANDSAT 9
- SENTINEL-2A
- SENTINEL-2B
- SENTINEL-2C
- SENTINEL-3A
- SENTINEL-3B
- ISS (ZARYA)

## License

GNU GENERAL PUBLIC LICENSE

## Acknowledgements

- Skyfield: Precise astronomical computation library.
- Celestrak: Satellite TLE data provider.
- Special thanks to Termatics, Austria for providing the opportunity and support to develop this project.

