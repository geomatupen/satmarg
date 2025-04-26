# %load core.py
# satoverpass/core.py

from skyfield.api import load, EarthSatellite, Topos
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests

# satmarg/core.py

import requests

# Simple cache: stores URL -> TLE text
_fetched_cache = {}

import requests

# Simple cache: stores URL -> TLE text
_fetched_cache = {}

def fetch_tle_text(name, url):
    """Fetches TLE data from a given URL and returns the TLE lines for the given satellite name.
    Avoids re-fetching if URL content hasn't changed."""

    if url in _fetched_cache:
        all_tle_text = _fetched_cache[url]
    else:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            all_tle_text = response.text

            # Only add to cache after successful fetch
            _fetched_cache[url] = all_tle_text

        except requests.RequestException as e:
            print(f"Error fetching TLE data from {url}: {e}")
            return ""

    tle_lines = all_tle_text.splitlines()
    for i in range(len(tle_lines) - 2):
        if name in tle_lines[i]:  # Look for the satellite name
            return [tle_lines[i+1], tle_lines[i+2]]

    print(f"Satellite name '{name}' not found in TLE data from {url}")
    return ""



# Define TLE sources
satellites_tle_source = 'https://celestrak.org/NORAD/elements/resource.txt'
stations_tle_source = 'https://celestrak.org/NORAD/elements/stations.txt'
# Manually provided TLE for SENTINEL-2C
sentinel_2c_tle = [  
    "1 60989U 24157A   25090.79518797  .00000292  00000-0  12798-3 0  9993",
    "2 60989  98.5659 167.0180 0001050  95.0731 265.0572 14.30814009 29727"
]

tle_sources = {
    # name: fetch_tle_text(name, common_tle_source) for name in ['LANDSAT 8'],
    'LANDSAT 8': fetch_tle_text('LANDSAT 8', satellites_tle_source),
    'LANDSAT 9': fetch_tle_text('LANDSAT 9', satellites_tle_source),
    'SENTINEL-2A': fetch_tle_text('SENTINEL-2A', satellites_tle_source),  
    'SENTINEL-2B': fetch_tle_text('SENTINEL-2B', satellites_tle_source),
    'SENTINEL-2C': sentinel_2c_tle, # Manually provided TLE as it was not available on the link
    'SENTINEL-3A': fetch_tle_text('SENTINEL-3A', satellites_tle_source),
    'SENTINEL-3B': fetch_tle_text('SENTINEL-3B', satellites_tle_source),  
    'ISS (ZARYA)': fetch_tle_text('ISS (ZARYA)', stations_tle_source),
}

ts = load.timescale()


def load_satellites():
    sats = {}
    for name, tle in tle_sources.items():
        line1, line2 = tle
        sats[name] = EarthSatellite(line1, line2, name, ts)
        # print(f"Loaded TLE data for {name}")
    print("Loaded TLE data")
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
        t = ts.utc(dt.year, dt.month, dt.day, 0, 0, np.arange(0, 86400, step_seconds)) #default 1 second
        subpoint = sat.at(t).subpoint()
        latitudes = subpoint.latitude.degrees
        longitudes = subpoint.longitude.degrees
        distances = np.sqrt((latitudes - lat)**2 + (longitudes - lon)**2)
        min_index = np.argmin(distances)
        closest_time = t[min_index].utc_datetime()

        topocentric = (sat - observer).at(t[min_index])
        alt, az, distance = topocentric.altaz()

        if distances[min_index] < max_angle_deg: #default 0.5
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


from datetime import datetime, timedelta

def get_precise_overpasses(
    lat,
    lon,
    start_date=None,
    end_date=None,
    satellites=None,
    step_seconds=1, 
    max_angle_deg=0.5
):
    all_satellites = load_satellites()
    all_overpasses = []

    # Set default dates if not provided
    if start_date is None:
        today = datetime.utcnow().date()
        start_date = today.strftime('%Y-%m-%d')
    if end_date is None:
        one_month_later = datetime.utcnow().date() + timedelta(days=30)
        end_date = one_month_later.strftime('%Y-%m-%d')

    #if latitude and longitude is not provided return message
    if lat is None or lon is None:
        raise ValueError("Latitude ('lat') and Longitude ('lon') parameters must be provided.")


    # Set default satellites if not provided
    if satellites is None:
        satellites = ["SENTINEL-2A", "SENTINEL-2B"]
    else:
        satellites = [s.strip() for s in satellites.split(',')]

    for sat in satellites:
        if sat in all_satellites:
            overpasses = find_overpasses(lat, lon, start_date, end_date, sat, all_satellites, step_seconds, max_angle_deg)
            all_overpasses.extend(overpasses)
        else:
            print(f"Satellite '{sat}' not found in loaded satellites.")

    return pd.DataFrame(all_overpasses)




def test_get_precise_overpasses():
    df = get_precise_overpasses(
        lat=27.7172,   # Kathmandu
        lon=85.3240,
        start_date="2025-04-26",
        end_date="2025-05-27",
        satellites = "SENTINEL-2A, SENTINEL-2B, SENTINEL-2C"
    )
    print(df)

# test_get_precise_overpasses()
