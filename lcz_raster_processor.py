"""
LCZ Raster Processor
Processes LCZ data from KMZ files containing raster images (GroundOverlay)
"""
import zipfile
import os
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, mapping
from shapely.ops import unary_union
import json


class LCZRasterProcessor:
    """Process LCZ KMZ files containing raster images"""

    # LCZ color mapping from QGIS colormap
    LCZ_COLORS = {
        1: (140, 0, 0),      # Compact High-Rise
        2: (209, 0, 0),      # Compact Mid-Rise
        3: (255, 0, 0),      # Compact Low-Rise
        4: (191, 77, 0),     # Open High-Rise
        5: (255, 102, 0),    # Open Mid-Rise
        6: (255, 153, 85),   # Open Low-Rise
        7: (250, 238, 5),    # Lightweight low-rise
        8: (188, 188, 188),  # Large low-rise
        9: (255, 204, 170),  # Sparsely built
        10: (85, 85, 85),    # Heavy industry
        11: (0, 106, 0),     # Dense trees
        12: (0, 170, 0),     # Scattered trees
        13: (100, 133, 37),  # Bush or scrub
        14: (185, 219, 121), # Low plants
        15: (0, 0, 0),       # Bare rock or paved
        16: (251, 247, 174), # Bare soil or sand
        17: (106, 106, 255), # Water
    }

    def __init__(self, kmz_path):
        self.kmz_path = kmz_path
        self.features = []
        self.bounds_coords = None
        self.image = None

    def extract_kmz(self, output_dir='temp_kmz'):
        """Extract KMZ file contents"""
        os.makedirs(output_dir, exist_ok=True)

        with zipfile.ZipFile(self.kmz_path, 'r') as kmz:
            kmz.extractall(output_dir)

        # Find KML and PNG files
        kml_file = None
        png_file = None

        for file in os.listdir(output_dir):
            if file.endswith('.kml'):
                kml_file = os.path.join(output_dir, file)
            elif file.endswith('.png'):
                png_file = os.path.join(output_dir, file)

        return kml_file, png_file

    def parse_kml_bounds(self, kml_path):
        """Parse KML to get geographic bounds"""
        tree = ET.parse(kml_path)
        root = tree.getroot()

        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Find LatLonBox
        latlonbox = root.find('.//kml:LatLonBox', ns)

        if latlonbox is not None:
            north = float(latlonbox.find('kml:north', ns).text)
            south = float(latlonbox.find('kml:south', ns).text)
            east = float(latlonbox.find('kml:east', ns).text)
            west = float(latlonbox.find('kml:west', ns).text)

            self.bounds_coords = {
                'north': north,
                'south': south,
                'east': east,
                'west': west
            }

            return self.bounds_coords

        return None

    def load_image(self, png_path):
        """Load PNG image"""
        self.image = Image.open(png_path).convert('RGB')
        return self.image

    def find_closest_lcz(self, color):
        """Find closest LCZ class for a given RGB color"""
        r, g, b = color
        min_dist = float('inf')
        closest_lcz = None

        for lcz, (lr, lg, lb) in self.LCZ_COLORS.items():
            # Euclidean distance in RGB space
            dist = ((r - lr) ** 2 + (g - lg) ** 2 + (b - lb) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_lcz = lcz

        # Only return if reasonably close (threshold to avoid noise)
        if min_dist < 30:  # Tolerance for color matching
            return closest_lcz
        return None

    def create_grid_features(self, grid_size=20):
        """
        Create grid-based features from raster image

        Args:
            grid_size: Number of grid cells in each dimension (reduces complexity)
        """
        if self.image is None or self.bounds_coords is None:
            return []

        img_array = np.array(self.image)
        height, width = img_array.shape[:2]

        # Calculate cell size in pixels
        cell_height = height // grid_size
        cell_width = width // grid_size

        # Calculate geographic cell size
        lat_range = self.bounds_coords['north'] - self.bounds_coords['south']
        lon_range = self.bounds_coords['east'] - self.bounds_coords['west']

        geo_cell_height = lat_range / grid_size
        geo_cell_width = lon_range / grid_size

        features = []

        for row in range(grid_size):
            for col in range(grid_size):
                # Get pixel region
                y_start = row * cell_height
                y_end = min((row + 1) * cell_height, height)
                x_start = col * cell_width
                x_end = min((col + 1) * cell_width, width)

                # Get most common color in this cell
                cell_pixels = img_array[y_start:y_end, x_start:x_end]
                colors, counts = np.unique(
                    cell_pixels.reshape(-1, 3),
                    axis=0,
                    return_counts=True
                )

                # Get dominant color
                dominant_idx = np.argmax(counts)
                dominant_color = tuple(colors[dominant_idx])

                # Find LCZ class
                lcz_class = self.find_closest_lcz(dominant_color)

                if lcz_class is not None:
                    # Calculate geographic bounds of this cell
                    lat_south = self.bounds_coords['south'] + (row * geo_cell_height)
                    lat_north = lat_south + geo_cell_height
                    lon_west = self.bounds_coords['west'] + (col * geo_cell_width)
                    lon_east = lon_west + geo_cell_width

                    # Create polygon
                    polygon = box(lon_west, lat_south, lon_east, lat_north)

                    features.append({
                        'type': 'Feature',
                        'geometry': mapping(polygon),
                        'properties': {
                            'lcz_class': lcz_class,
                            'name': f'LCZ {lcz_class} - Cell {row},{col}'
                        }
                    })

        self.features = features
        return features

    def process(self, grid_size=50):
        """Main processing method"""
        kml_path, png_path = self.extract_kmz()

        if not kml_path or not png_path:
            print("Error: Could not find KML or PNG in KMZ file")
            return []

        # Parse bounds
        self.parse_kml_bounds(kml_path)

        # Load image
        self.load_image(png_path)

        # Create features
        return self.create_grid_features(grid_size=grid_size)

    def get_bounds(self):
        """Get bounding box [lon_min, lat_min, lon_max, lat_max]"""
        if self.bounds_coords:
            return [
                self.bounds_coords['west'],
                self.bounds_coords['south'],
                self.bounds_coords['east'],
                self.bounds_coords['north']
            ]
        return None

    def get_center(self):
        """Get center point [lat, lon]"""
        if self.bounds_coords:
            center_lat = (self.bounds_coords['north'] + self.bounds_coords['south']) / 2
            center_lon = (self.bounds_coords['east'] + self.bounds_coords['west']) / 2
            return [center_lat, center_lon]
        return None

    def to_geojson(self):
        """Convert features to GeoJSON"""
        if self.features:
            return {
                'type': 'FeatureCollection',
                'features': self.features
            }
        return None
