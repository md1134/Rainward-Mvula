"""Rainfall forecast. Uses Open-Meteo (no API key). Falls back to DEMO_RAIN_MM if set or if the call fails."""
import json
import os
import time
import urllib.parse
import urllib.request

_CACHE = {}
TTL = 30 * 60


def rain_next_24h(lat, lon):
    """Return (mm, source). source is 'forecast', 'demo' or 'unavailable'."""
    demo = os.environ.get("DEMO_RAIN_MM")
    if demo not in (None, ""):
        return float(demo), "demo"
    key = (round(lat, 2), round(lon, 2))
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < TTL:
        return hit[1], "forecast"
    qs = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "hourly": "precipitation",
                                 "forecast_days": 2, "timezone": "Africa/Lusaka"})
    try:
        with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{qs}", timeout=6) as r:
            data = json.load(r)
        mm = round(sum(v or 0 for v in data["hourly"]["precipitation"][:24]), 1)
    except Exception:
        return 0.0, "unavailable"
    _CACHE[key] = (time.time(), mm)
    return mm, "forecast"
