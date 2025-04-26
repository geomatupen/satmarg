# SatMarg - Satellite Overpass Predictor

**SatMarg** = Satellite + Mārga (Sanskrit for "path" or "orbit")  
Predict satellite overpass times for any location easily and precisely.

## About SatMarg

SatMarg is a lightweight Python package designed to calculate satellite overpass predictions for specific locations and time periods. It uses real-time Two-Line Element (TLE) data to provide precise estimates of when satellites such as SENTINEL-2A, SENTINEL-2B, LANDSAT 8, and others will pass closest to a given latitude and longitude. SatMarg is built to be fast, simple, and customizable, allowing users to adjust processing speed and proximity angle according to their needs. It is ideal for applications such as satellite image planning, ground station scheduling, and general orbital analysis.

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
- `step_seconds = 1` for slow (high precision),  
- `step_seconds = 10` for medium,  
- `step_seconds = 20` for fast (less precision).

## Example Output

| date                | Satellite    | Lat (DEG) | Lon (DEG) | Sat. Azi. (deg) | Sat. Elev. (deg) | Range (km) |
|---------------------|--------------|-----------|-----------|-----------------|-----------------|------------|
| 2025-04-27 05:14:11  | SENTINEL-2A  | 27.72     | 85.32     | 199.3           | 82.1             | 702.8      |

## Supported Satellites

- LANDSAT 8
- LANDSAT 9
- SENTINEL-2A
- SENTINEL-2B
- SENTINEL-2C (manual TLE)
- SENTINEL-3A
- SENTINEL-3B
- ISS (ZARYA)

## License

MIT License

## Acknowledgements

- Skyfield: Precise astronomical computation library.
- Celestrak: Satellite TLE data provider.
- Special thanks to Termatics, Austria for providing the opportunity and support to develop this project.

