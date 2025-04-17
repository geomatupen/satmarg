# satoverpass/core.py

from skyfield.api import load, EarthSatellite, Topos
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests

# TLE sources
TLE_SOURCES = {
    'LANDSAT 8': 'https://celestrak.org/NORAD/elements/resource.txt',
    'LANDSAT 9': 'https://celestrak.org/NORAD/elements/resource.txt',
    'SENTINEL-2A': 'https://celestrak.org/NORAD/elements/resource.txt',
    'SENTINEL-2B': 'https://celestrak.org/NORAD/elements/resource.txt',
    'SENTINEL-2C': None
}

SENTINEL_2C_TLE = [
    "1 60989U 24157A   25090.79518797  .00000292  00000-0  12798-3 0  9993",
    "2 60989  98.5659 167.0180 0001050  95.0731 265.0572 14.30814009 29727"
]

ts = load.timescale()


def fetch_tle_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return ""


def load_satellites():
    sats = {}
    for name, url in TLE_SOURCES.items():
        if name == 'SENTINEL-2C':
            line1, line2 = SENTINEL_2C_TLE
            sats[name] = EarthSatellite(line1, line2, name, ts)
        else:
            tle_text = fetch_tle_text(url)
            tle_lines = tle_text.splitlines()
            for i in range(len(tle_lines) - 2):
                if name in tle_lines[i]:
                    line1, line2 = tle_lines[i+1], tle_lines[i+2]
                    sats[name] = EarthSatellite(line1, line2, name, ts)
                    break
    return sats


def find_overpasses(lat, lon, start_date, end_date, satellite, satellites):
    if satellite not in satellites:
        return []

    sat = satellites[satellite]
    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    results = []
    dt = start_dt

    while dt <= end_dt:
        t = ts.utc(dt.year, dt.month, dt.day, 0, 0, np.arange(0, 86400, 1))
        subpoint = sat.at(t).subpoint()
        latitudes = subpoint.latitude.degrees
        longitudes = subpoint.longitude.degrees
        distances = np.sqrt((latitudes - lat)**2 + (longitudes - lon)**2)
        min_index = np.argmin(distances)
        closest_time = t[min_index].utc_datetime()

        topocentric = (sat - observer).at(t[min_index])
        alt, az, distance = topocentric.altaz()

        if distances[min_index] < 0.5:
            results.append({
                'date': closest_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Satellite': satellite,
                'Lat (DEG)': latitudes[min_index],
                'Lon (DEG)': longitudes[min_index],
                'Sat. Azi. (deg)': az.degrees,
                'Sat. Elev. (deg)': alt.degrees,
                'Range (km)': distance.km
            })

        dt += timedelta(days=1)

    return results


def get_precise_overpasses(lat, lon, start_date, end_date):
    satellites = load_satellites()
    all_overpasses = []
    for name in satellites:
        overpasses = find_overpasses(lat, lon, start_date, end_date, name, satellites)
        all_overpasses.extend(overpasses)

    return pd.DataFrame(all_overpasses)
