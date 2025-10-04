"""
LCZ KMZ File Processor (Simplified - no GeoPandas dependency)
Handles extraction and processing of Local Climate Zone data from KMZ files
"""
import zipfile
import os
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon, Point, mapping, shape
import json


class LCZProcessor:
    """Process LCZ KMZ files and extract zone geometries"""

    def __init__(self, kmz_path):
        self.kmz_path = kmz_path
        self.features = []

    def extract_kmz(self, output_dir='temp_kmz'):
        """Extract KMZ file contents"""
        os.makedirs(output_dir, exist_ok=True)

        with zipfile.ZipFile(self.kmz_path, 'r') as kmz:
            kmz.extractall(output_dir)

        # Find the KML file
        kml_file = None
        for file in os.listdir(output_dir):
            if file.endswith('.kml'):
                kml_file = os.path.join(output_dir, file)
                break

        return kml_file

    def parse_kml(self, kml_path):
        """Parse KML file and extract LCZ polygons"""
        tree = ET.parse(kml_path)
        root = tree.getroot()

        # KML namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        self.features = []

        # Find all Placemarks
        for placemark in root.findall('.//kml:Placemark', ns):
            # Extract name (if available)
            name_elem = placemark.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else 'Unknown'

            # Extract LCZ class from name or description
            lcz_class = self._extract_lcz_class(name)

            # Extract polygon coordinates
            polygon_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
            multigeom_elem = placemark.find('.//kml:MultiGeometry', ns)

            geometry = None

            if polygon_elem is not None:
                coords = self._parse_coordinates(polygon_elem.text)
                if coords:
                    geometry = Polygon(coords)

            elif multigeom_elem is not None:
                polygons = []
                for poly in multigeom_elem.findall('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns):
                    coords = self._parse_coordinates(poly.text)
                    if coords:
                        polygons.append(Polygon(coords))
                if polygons:
                    geometry = MultiPolygon(polygons) if len(polygons) > 1 else polygons[0]

            if geometry:
                self.features.append({
                    'type': 'Feature',
                    'geometry': mapping(geometry),
                    'properties': {
                        'lcz_class': lcz_class,
                        'name': name
                    }
                })

        return self.features

    def _parse_coordinates(self, coord_string):
        """Parse KML coordinate string to list of tuples"""
        coords = []
        for coord in coord_string.strip().split():
            parts = coord.split(',')
            if len(parts) >= 2:
                lon, lat = float(parts[0]), float(parts[1])
                coords.append((lon, lat))
        return coords

    def _extract_lcz_class(self, name):
        """Extract LCZ class number from name"""
        # Try to find a number in the name
        import re
        match = re.search(r'(\d+)', name)
        if match:
            return int(match.group(1))
        return None

    def process(self):
        """Main processing method"""
        kml_path = self.extract_kmz()
        if kml_path:
            self.parse_kml(kml_path)
        return self.features

    def get_bounds(self):
        """Get bounding box of all LCZ zones"""
        if not self.features:
            return None

        all_coords = []
        for feature in self.features:
            geom = shape(feature['geometry'])
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            all_coords.append(bounds)

        if not all_coords:
            return None

        min_lon = min(b[0] for b in all_coords)
        min_lat = min(b[1] for b in all_coords)
        max_lon = max(b[2] for b in all_coords)
        max_lat = max(b[3] for b in all_coords)

        return [min_lon, min_lat, max_lon, max_lat]

    def get_center(self):
        """Get center point of all zones"""
        bounds = self.get_bounds()
        if bounds is not None:
            center_lon = (bounds[0] + bounds[2]) / 2
            center_lat = (bounds[1] + bounds[3]) / 2
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
