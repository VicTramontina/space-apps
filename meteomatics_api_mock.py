"""
Mock Meteomatics API for testing/demo purposes
Generates realistic temperature data without requiring API credentials
"""
import numpy as np
from datetime import datetime


class MeteomaticsAPI:
    """Mock interface for Meteomatics Weather API - for testing only"""

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        print("⚠️  Using MOCK Meteomatics API (no real data)")
        print("    For real data, configure credentials in .env")

    def _generate_mock_temperature(self, lat, lon):
        """Generate a realistic mock temperature based on location"""
        # Base temperature for Lajeado region (subtropical)
        base_temp = 22.0

        # Add some variation based on coordinates
        # (simulating urban heat island and natural variation)
        lat_factor = (lat + 29.45) * 30  # Latitude variation
        lon_factor = (lon + 52.0) * 20   # Longitude variation

        # Add some randomness
        noise = np.random.normal(0, 1.5)

        temp = base_temp + lat_factor + lon_factor + noise

        # Clamp to reasonable range
        return max(15.0, min(35.0, temp))

    def get_temperature_grid(self, lat_min, lat_max, lon_min, lon_max, resolution=0.01, datetime_str=None):
        """Generate mock temperature grid"""
        lats = np.arange(lat_min, lat_max, resolution)
        lons = np.arange(lon_min, lon_max, resolution)

        # Sample fewer points for performance
        lat_step = max(1, len(lats) // 10)
        lon_step = max(1, len(lons) // 10)
        lats = lats[::lat_step]
        lons = lons[::lon_step]

        result = {
            'coordinates': [],
            'values': []
        }

        for lat in lats[:10]:  # Limit to 10x10 grid
            for lon in lons[:10]:
                temp = self._generate_mock_temperature(lat, lon)
                result['coordinates'].append({'lat': float(lat), 'lon': float(lon)})
                result['values'].append(temp)

        return result

    def get_temperature_point(self, lat, lon, datetime_str=None):
        """Generate mock temperature for a specific point"""
        return self._generate_mock_temperature(lat, lon)

    def get_temperature_time_series(self, lat, lon, start_date, end_date, interval='PT1H'):
        """Generate mock time series"""
        # Simple mock - return constant temperature
        base_temp = self._generate_mock_temperature(lat, lon)

        return [
            {'date': start_date, 'value': base_temp},
            {'date': end_date, 'value': base_temp + 2.0}
        ]
