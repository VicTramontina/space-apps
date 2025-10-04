"""
Flask Application for LCZ Temperature Analysis and Visualization
"""
from flask import Flask, render_template, jsonify, request
import folium
from folium import plugins
import json
import os
from lcz_raster_processor_minimal import LCZRasterProcessor as LCZProcessor
from temperature_calculator import TemperatureCalculator
from config import (
    FLASK_PORT, FLASK_DEBUG, KMZ_FILE_PATH,
    LCZ_CLASSES, OUTPUT_DIR, METEOMATICS_USERNAME, METEOMATICS_PASSWORD
)

# Use Mock API if credentials not configured
if METEOMATICS_USERNAME and METEOMATICS_PASSWORD:
    from meteomatics_api import MeteomaticsAPI
    print("✓ Using real Meteomatics API")
else:
    from meteomatics_api_mock import MeteomaticsAPI
    print("⚠️  Using MOCK API - configure .env for real data")

app = Flask(__name__)

# Global instances
lcz_processor = None
meteomatics = MeteomaticsAPI()
temp_calculator = TemperatureCalculator()


def initialize_lcz_data():
    """Initialize LCZ data from KMZ file"""
    global lcz_processor

    if not os.path.exists(KMZ_FILE_PATH):
        print(f"Error: KMZ file not found at {KMZ_FILE_PATH}")
        return None

    lcz_processor = LCZProcessor(KMZ_FILE_PATH)
    gdf = lcz_processor.process()

    if gdf is None or len(gdf) == 0:
        print("Error: No LCZ data found in KMZ file")
        return None

    print(f"Loaded {len(gdf)} LCZ zones")
    return gdf


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/lcz-data')
def get_lcz_data():
    """Get LCZ GeoJSON data"""
    if lcz_processor is None:
        initialize_lcz_data()

    if lcz_processor and lcz_processor.features:
        geojson = lcz_processor.to_geojson()
        center = lcz_processor.get_center()
        bounds = lcz_processor.get_bounds()

        return jsonify({
            'success': True,
            'geojson': geojson,
            'center': center,
            'bounds': bounds
        })

    return jsonify({'success': False, 'error': 'No LCZ data available'})


@app.route('/api/temperature')
def get_temperature():
    """Get temperature data for a point or area"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({'success': False, 'error': 'Missing coordinates'})

    temperature = meteomatics.get_temperature_point(lat, lon)

    if temperature is not None:
        return jsonify({
            'success': True,
            'temperature': temperature,
            'lat': lat,
            'lon': lon
        })

    return jsonify({
        'success': False,
        'error': 'Unable to fetch temperature data. Check API credentials.'
    })


@app.route('/api/temperature-grid')
def get_temperature_grid():
    """Get temperature grid for the entire area"""
    if lcz_processor is None:
        initialize_lcz_data()

    if lcz_processor is None or not lcz_processor.features:
        return jsonify({'success': False, 'error': 'LCZ data not loaded'})

    bounds = lcz_processor.get_bounds()
    if bounds is None:
        return jsonify({'success': False, 'error': 'Unable to determine area bounds'})

    lon_min, lat_min, lon_max, lat_max = bounds[0], bounds[1], bounds[2], bounds[3]

    # Get temperature grid
    temp_data = meteomatics.get_temperature_grid(
        lat_min, lat_max, lon_min, lon_max, resolution=0.005
    )

    if temp_data:
        return jsonify({
            'success': True,
            'data': temp_data
        })

    return jsonify({
        'success': False,
        'error': 'Unable to fetch temperature grid. Check API credentials.'
    })


@app.route('/api/calculate-scenario', methods=['POST'])
def calculate_scenario():
    """Calculate temperature changes for LCZ scenario modifications"""
    data = request.get_json()

    zone_id = data.get('zone_id')
    from_lcz = data.get('from_lcz')
    to_lcz = data.get('to_lcz')
    base_temperature = data.get('base_temperature')

    if None in [zone_id, from_lcz, to_lcz, base_temperature]:
        return jsonify({'success': False, 'error': 'Missing required parameters'})

    result = temp_calculator.calculate_temperature_delta(
        from_lcz, to_lcz, base_temperature
    )

    if result:
        return jsonify({
            'success': True,
            'result': result
        })

    return jsonify({'success': False, 'error': 'Invalid LCZ classes'})


@app.route('/api/lcz-properties')
def get_lcz_properties():
    """Get thermal properties for all LCZ classes"""
    properties = temp_calculator.get_all_thermal_properties()
    return jsonify({
        'success': True,
        'properties': properties
    })


@app.route('/api/lcz-classes')
def get_lcz_classes():
    """Get LCZ class definitions"""
    return jsonify({
        'success': True,
        'classes': LCZ_CLASSES
    })


@app.route('/generate-map')
def generate_static_map():
    """Generate a static Folium map"""
    if lcz_processor is None:
        initialize_lcz_data()

    if lcz_processor is None:
        return "Error: Unable to load LCZ data"

    center = lcz_processor.get_center()
    m = folium.Map(location=center, zoom_start=13)

    # Add LCZ layers
    geojson = lcz_processor.to_geojson()

    def style_function(feature):
        lcz_class = feature['properties'].get('lcz_class')
        if lcz_class and lcz_class in LCZ_CLASSES:
            return {
                'fillColor': LCZ_CLASSES[lcz_class]['color'],
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            }
        return {'fillColor': 'gray', 'color': 'black', 'weight': 1, 'fillOpacity': 0.5}

    folium.GeoJson(
        geojson,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['lcz_class', 'name'])
    ).add_to(m)

    # Save map
    map_path = os.path.join(OUTPUT_DIR, 'lcz_map.html')
    m.save(map_path)

    return f"Map generated at: {map_path}"


if __name__ == '__main__':
    # Initialize data on startup
    print("Initializing LCZ data...")
    initialize_lcz_data()

    print(f"Starting Flask app on port {FLASK_PORT}")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
