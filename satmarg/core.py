# %load core.py
# satoverpass/core.py

from skyfield.api import load, EarthSatellite, Topos
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import os
import json

# Constants and global cache
_fetched_cache = {}
ts = load.timescale()
TLE_CACHE_FILE = "tle_cache.json"

# TLE data sources
satellites_tle_source = 'https://celestrak.org/NORAD/elements/resource.txt'
stations_tle_source = 'https://celestrak.org/NORAD/elements/stations.txt'

# Custom/manual TLE for missing satellites
custom_tle_sources = {
    "SENTINEL-2C": [
        "1 60989U 24157A   25090.79518797  .00000292  00000-0  12798-3 0  9993",
        "2 60989  98.5659 167.0180 0001050  95.0731 265.0572 14.30814009 29727"
    ]
}

def load_tle_cache():
    if os.path.exists(TLE_CACHE_FILE):
        with open(TLE_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tle_cache(cache):
    with open(TLE_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

tle_cache = load_tle_cache()

def fetch_tle_text(name, url):
    if url not in _fetched_cache:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            _fetched_cache[url] = response.text
        except requests.RequestException as e:
            print(f"Error fetching TLE from {url}: {e}")
            return ""

    tle_lines = _fetched_cache[url].splitlines()
    for i in range(len(tle_lines) - 2):
        if name.strip().upper() == tle_lines[i].strip().upper():
            return [tle_lines[i+1], tle_lines[i+2]]
    return ""

def load_satellites(satellite_names):
    sats = {}

    if len(satellite_names) > 5:
        print(f" Too many satellites requested ({len(satellite_names)}). Limiting to first 5.")
        satellite_names = satellite_names[:5]

    for name in satellite_names:
        tle = None

        if name in tle_cache:
            tle = tle_cache[name]
        else:
            tle = fetch_tle_text(name, satellites_tle_source)
            if not tle:
                tle = fetch_tle_text(name, stations_tle_source)
            if not tle and name in custom_tle_sources:
                tle = custom_tle_sources[name]
            if tle:
                tle_cache[name] = tle

        if tle:
            try:
                line1, line2 = tle
                sats[name] = EarthSatellite(line1, line2, name, ts)
            except Exception as e:
                print(f"Could not load TLE for {name}: {e}")
        else:
            print(f"No TLE found for satellite: {name}")

    save_tle_cache(tle_cache)
    return sats

def find_overpasses(lat, lon, start_date, end_date, satellite, satellites, step_seconds, max_angle_deg):
    if satellite not in satellites:
        return []

    sat = satellites[satellite]
    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    results = []
    dt = start_dt

    while dt <= end_dt:
        t = ts.utc(dt.year, dt.month, dt.day, 0, 0, np.arange(0, 86400, step_seconds))
        subpoint = sat.at(t).subpoint()
        latitudes = subpoint.latitude.degrees
        longitudes = subpoint.longitude.degrees
        distances = np.sqrt((latitudes - lat)**2 + (longitudes - lon)**2)
        min_index = np.argmin(distances)
        closest_time = t[min_index].utc_datetime()

        topocentric = (sat - observer).at(t[min_index])
        alt, az, distance = topocentric.altaz()

        if distances[min_index] < max_angle_deg:
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

def format_output(df, output_format, csv_filename=None):
    output_format = output_format.lower()
    if output_format == 'table':
        return df
    elif output_format == 'json':
        return df.to_json(orient='records', indent=2)
    elif output_format == 'csv':
        if csv_filename is None:
            csv_filename = 'overpasses.csv'
        df.to_csv(csv_filename, index=False)
        print(f"CSV file saved as: {csv_filename}")
        return csv_filename
    else:
        raise ValueError("Invalid output_format. Choose 'table', 'json', or 'csv'.")

def get_precise_overpasses(
    lat,
    lon,
    start_date=None,
    end_date=None,
    satellites=None,
    step_seconds=1,
    max_angle_deg=0.5,
    output_format='json'
):
    if start_date is None:
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
    if end_date is None:
        end_date = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')

    if lat is None or lon is None:
        raise ValueError("Latitude and Longitude must be provided.")

    if satellites is None:
        satellite_names = ["SENTINEL-2A", "SENTINEL-2B", "LANDSAT 8", "LANDSAT 9"]
    else:
        satellite_names = [s.strip() for s in satellites.split(',')]

    all_satellites = load_satellites(satellite_names)
    all_overpasses = []

    for sat in all_satellites:
        overpasses = find_overpasses(lat, lon, start_date, end_date, sat, all_satellites, step_seconds, max_angle_deg)
        all_overpasses.extend(overpasses)

    df = pd.DataFrame(all_overpasses)
    return format_output(df, output_format)



def test_get_precise_overpasses():
    df = get_precise_overpasses(
        lat=27.7172,   # Kathmandu
        lon=85.3240,
        start_date="2025-04-26",
        end_date="2025-05-27",
        satellites = "SENTINEL-2A",
        output_format='json',    
    )
    print(df)

# test_get_precise_overpasses() 

