"""
Meteomatics API Integration
Fetches surface temperature data for LCZ analysis
"""
import requests
from datetime import datetime, timedelta
import numpy as np
from config import METEOMATICS_USERNAME, METEOMATICS_PASSWORD, METEOMATICS_API_BASE


class MeteomaticsAPI:
    """Interface for Meteomatics Weather API"""

    def __init__(self, username=None, password=None):
        self.username = username or METEOMATICS_USERNAME
        self.password = password or METEOMATICS_PASSWORD
        self.base_url = METEOMATICS_API_BASE

    def get_temperature_grid(self, lat_min, lat_max, lon_min, lon_max, resolution=0.01, datetime_str=None):
        """
        Get temperature data for a grid area by sampling multiple points

        Args:
            lat_min, lat_max, lon_min, lon_max: Bounding box coordinates
            resolution: Grid resolution in degrees (default 0.01 = ~1km)
            datetime_str: ISO format datetime (default: current time)

        Returns:
            dict: Temperature data with coordinates
        """
        if datetime_str is None:
            datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Use 2m temperature as proxy for surface conditions
        parameter = 't_2m:C'

        # Create grid coordinates
        lats = np.arange(lat_min, lat_max, resolution)
        lons = np.arange(lon_min, lon_max, resolution)

        # Limit number of points to avoid too many requests
        max_points = 100
        total_points = len(lats) * len(lons)

        if total_points > max_points:
            # Sample fewer points
            lat_step = max(1, len(lats) // 10)
            lon_step = max(1, len(lons) // 10)
            lats = lats[::lat_step]
            lons = lons[::lon_step]

        # Create list of coordinate pairs for multi-point query
        coords_list = []
        for lat in lats:
            for lon in lons:
                coords_list.append(f"{lat},{lon}")

        # Meteomatics supports multiple locations separated by '+'
        # Limit to 50 points per request
        locations = '+'.join(coords_list[:50])

        # Build URL
        url = f"{self.base_url}/{datetime_str}/{parameter}/{locations}/json"

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_grid_response(data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching temperature data: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def get_temperature_point(self, lat, lon, datetime_str=None):
        """
        Get temperature at a specific point

        Args:
            lat, lon: Coordinates
            datetime_str: ISO format datetime (default: current time)

        Returns:
            float: Temperature in Celsius
        """
        if datetime_str is None:
            datetime_str = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        parameter = 't_2m:C'
        location = f"{lat},{lon}"

        url = f"{self.base_url}/{datetime_str}/{parameter}/{location}/json"

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            if data and 'data' in data and len(data['data']) > 0:
                coordinates = data['data'][0]['coordinates']
                if len(coordinates) > 0:
                    return coordinates[0]['dates'][0]['value']

        except requests.exceptions.RequestException as e:
            print(f"Error fetching temperature data: {e}")

        return None

    def get_temperature_time_series(self, lat, lon, start_date, end_date, interval='PT1H'):
        """
        Get temperature time series for a location

        Args:
            lat, lon: Coordinates
            start_date, end_date: ISO format datetime strings
            interval: Time interval (default PT1H = 1 hour)

        Returns:
            list: Temperature time series data
        """
        parameter = 't_2m:C'
        location = f"{lat},{lon}"
        time_range = f"{start_date}--{end_date}:{interval}"

        url = f"{self.base_url}/{time_range}/{parameter}/{location}/json"

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_timeseries_response(data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching time series data: {e}")
            return None

    def _parse_grid_response(self, data):
        """Parse grid response from Meteomatics API"""
        if not data or 'data' not in data:
            return None

        result = {
            'coordinates': [],
            'values': []
        }

        for item in data['data']:
            parameter = item.get('parameter', '')
            for coord in item.get('coordinates', []):
                lat = coord.get('lat')
                lon = coord.get('lon')
                dates = coord.get('dates', [])

                if dates and len(dates) > 0:
                    value = dates[0].get('value')
                    result['coordinates'].append({'lat': lat, 'lon': lon})
                    result['values'].append(value)

        return result

    def _parse_timeseries_response(self, data):
        """Parse time series response from Meteomatics API"""
        if not data or 'data' not in data:
            return None

        result = []

        for item in data['data']:
            for coord in item.get('coordinates', []):
                for date_entry in coord.get('dates', []):
                    result.append({
                        'date': date_entry.get('date'),
                        'value': date_entry.get('value')
                    })

        return result
