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

# hard coded values based on the swath. They are the tentative reduced values, but can be changed based on the need. 
SAFE_NADIR_DEG = {
    "LANDSAT 8": 0.7,     #half-swath: ~0.83° #reduced for test: 0.7
    "LANDSAT 9": 0.7,     #half-swath: ~0.83° #0.7
    "SENTINEL-2A": 0.5,   #half-swath: ~1.30° #0.8
    "SENTINEL-2B": 0.5,   #half-swath: ~1.30° #0.8
    "SENTINEL-3A": 0.5,   #half-swath: ~5.7–6.3° #2.0
    "SENTINEL-3B": 0.5,   #half-swath: ~5.7–6.3° #2.0
}

def get_precise_overpasses(
    lat,
    lon,
    start_date=None,
    end_date=None,
    satellites=None,
    step_seconds=1,
    max_angle_deg=None,
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
        if max_angle_deg is None:
            try:
                final_max_angle_deg = SAFE_NADIR_DEG.get(sat.upper(), 0.5); #if angle not passed use default degrees available
                # print(f"satellite: {sat} and using max angle: {final_max_angle_deg}")
            except Exception:
                pass
        else:
            if "," in max_angle_deg:
                final_max_angle_list = [float(d.strip()) for d in max_angle_deg.split(',')]
                # print(sat)
                sat_index = satellite_names.index(sat)
                # print(sat_index)
                if len(final_max_angle_list) != len(satellite_names):
                    print("Sizes of max_angle_deg should match with size of satellites eg. 5 satellites should have 5 max_angle_deg - comma separated")
                    pass
                final_max_angle_deg = final_max_angle_list[sat_index]
            else:
                final_max_angle_deg = float(max_angle_deg.strip())

        # print(final_max_angle_deg)
        overpasses = find_overpasses(lat, lon, start_date, end_date, sat, all_satellites, step_seconds, final_max_angle_deg)
        all_overpasses.extend(overpasses)

    df = pd.DataFrame(all_overpasses)
    return format_output(df, output_format)



def test_get_precise_overpasses():
    df = get_precise_overpasses(
        lat= 47.899167,
        lon= 17.007472,
        # lat = 27.700769,
        # lon = 85.300140,
        start_date="2025-09-22",
        end_date="2025-11-22",
        satellites = "SENTINEL-3A, SENTINEL-3B, LANDSAT 8, LANDSAT 9, ISS (ZARYA)", #single or multiple
        max_angle_deg = "0.5", #"0.5, 0.5, 0.7, 0.7, 0.5",  #single or multiple but count should match with satellites
        output_format='csv',    
    )
    print(df)

# test_get_precise_overpasses() 

