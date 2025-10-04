"""
Test script for raster-based LCZ processing
"""
from lcz_raster_processor import LCZRasterProcessor
import os

print("=" * 60)
print("Testing Raster-based LCZ Processing")
print("=" * 60)

kmz_path = 'lajeado-result/21025c4c602c6ebc89232bf384a56fac185220af.kmz'

print(f"\n1. KMZ file: {kmz_path}")
print(f"   Exists: {os.path.exists(kmz_path)}")

try:
    print("\n2. Creating processor...")
    processor = LCZRasterProcessor(kmz_path)

    print("\n3. Processing KMZ (this may take a moment)...")
    features = processor.process(grid_size=50)

    print(f"\n4. Results:")
    print(f"   Features created: {len(features)}")

    if features:
        # Count by LCZ class
        lcz_counts = {}
        for f in features:
            lcz = f['properties']['lcz_class']
            lcz_counts[lcz] = lcz_counts.get(lcz, 0) + 1

        print(f"\n5. LCZ distribution:")
        for lcz in sorted(lcz_counts.keys()):
            print(f"   LCZ {lcz:2d}: {lcz_counts[lcz]:4d} cells")

        print(f"\n6. Geographic info:")
        center = processor.get_center()
        print(f"   Center: {center}")
        bounds = processor.get_bounds()
        print(f"   Bounds: {bounds}")

        print(f"\n7. Sample feature:")
        sample = features[0]
        print(f"   LCZ: {sample['properties']['lcz_class']}")
        print(f"   Name: {sample['properties']['name']}")

        print("\n✓ SUCCESS!")
    else:
        print("\n✗ No features created")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
