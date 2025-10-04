"""
Configuration module for LCZ temperature analysis application
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Meteomatics API Configuration
METEOMATICS_USERNAME = os.getenv('METEOMATICS_USERNAME', '')
METEOMATICS_PASSWORD = os.getenv('METEOMATICS_PASSWORD', '')
METEOMATICS_API_BASE = 'https://api.meteomatics.com'

# Flask Configuration
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# LCZ Configuration
LCZ_CLASSES = {
    1: {'name': 'Compact High-Rise', 'color': '#8C0000', 'thermal_offset': 2.5},
    2: {'name': 'Compact Mid-Rise', 'color': '#D10000', 'thermal_offset': 2.8},
    3: {'name': 'Compact Low-Rise', 'color': '#FF0000', 'thermal_offset': 2.3},
    4: {'name': 'Open High-Rise', 'color': '#BF4D00', 'thermal_offset': 1.8},
    5: {'name': 'Open Mid-Rise', 'color': '#FF6600', 'thermal_offset': 2.0},
    6: {'name': 'Open Low-Rise', 'color': '#FF9955', 'thermal_offset': 1.5},
    7: {'name': 'Lightweight Low-Rise', 'color': '#FAEE05', 'thermal_offset': 1.2},
    8: {'name': 'Large Low-Rise', 'color': '#BCBCBC', 'thermal_offset': 2.2},
    9: {'name': 'Sparsely Built', 'color': '#FFCCAA', 'thermal_offset': 0.5},
    10: {'name': 'Heavy Industry', 'color': '#555555', 'thermal_offset': 2.6},
    11: {'name': 'Dense Trees', 'color': '#006A00', 'thermal_offset': -1.5},
    12: {'name': 'Scattered Trees', 'color': '#00AA00', 'thermal_offset': -0.8},
    13: {'name': 'Bush or Scrub', 'color': '#648525', 'thermal_offset': -0.3},
    14: {'name': 'Low Plants', 'color': '#B9DB79', 'thermal_offset': 0.0},  # Baseline
    15: {'name': 'Bare Rock or Paved', 'color': '#000000', 'thermal_offset': 2.0},
    16: {'name': 'Bare Soil or Sand', 'color': '#FBF7AE', 'thermal_offset': 1.0},
    17: {'name': 'Water', 'color': '#6A6AFF', 'thermal_offset': -2.0},
}

# Data Paths
KMZ_FILE_PATH = 'lajeado-result/21025c4c602c6ebc89232bf384a56fac185220af.kmz'
OUTPUT_DIR = 'output'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
