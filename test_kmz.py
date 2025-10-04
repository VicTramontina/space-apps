"""
Test script to debug KMZ processing
"""
from lcz_processor_simple import LCZProcessor
import os
import traceback

print("=" * 50)
print("Testing KMZ Processing")
print("=" * 50)

kmz_path = 'lajeado-result/21025c4c602c6ebc89232bf384a56fac185220af.kmz'

print(f"\n1. Checking if KMZ exists: {kmz_path}")
print(f"   Exists: {os.path.exists(kmz_path)}")
print(f"   Size: {os.path.getsize(kmz_path) if os.path.exists(kmz_path) else 'N/A'} bytes")

try:
    print("\n2. Creating LCZProcessor...")
    processor = LCZProcessor(kmz_path)
    print("   ✓ LCZProcessor created")

    print("\n3. Extracting KMZ...")
    kml_file = processor.extract_kmz()
    print(f"   KML file: {kml_file}")
    print(f"   KML exists: {os.path.exists(kml_file) if kml_file else False}")

    if kml_file and os.path.exists(kml_file):
        print(f"   KML size: {os.path.getsize(kml_file)} bytes")

        # Read first 500 chars of KML
        with open(kml_file, 'r', encoding='utf-8') as f:
            content = f.read(500)
            print(f"\n   First 500 chars of KML:")
            print(f"   {content[:200]}...")

    print("\n4. Parsing KML...")
    features = processor.parse_kml(kml_file)
    print(f"   Number of features: {len(features)}")

    if features:
        print(f"\n5. Sample feature:")
        sample = features[0]
        print(f"   LCZ Class: {sample['properties'].get('lcz_class')}")
        print(f"   Name: {sample['properties'].get('name')}")
        print(f"   Geometry type: {sample['geometry']['type']}")

        print(f"\n6. All LCZ classes found:")
        lcz_classes = set()
        for f in features:
            lcz = f['properties'].get('lcz_class')
            if lcz:
                lcz_classes.add(lcz)
        print(f"   {sorted(lcz_classes)}")

        print(f"\n7. Testing other methods...")
        center = processor.get_center()
        print(f"   Center: {center}")
        bounds = processor.get_bounds()
        print(f"   Bounds: {bounds}")
        geojson = processor.to_geojson()
        print(f"   GeoJSON features: {len(geojson['features']) if geojson else 0}")

        print("\n✓ SUCCESS! All tests passed!")
    else:
        print("\n✗ ERROR: No features found!")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 50)
