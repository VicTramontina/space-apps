"""
Temperature Difference Calculator for LCZ Scenario Changes
Based on scientific literature on urban heat island effects
"""
from config import LCZ_CLASSES


class TemperatureCalculator:
    """
    Calculate temperature changes when LCZ types are modified

    Methodology based on:
    - Stewart, I. D., & Oke, T. R. (2012). Local climate zones for urban temperature studies.
      Bulletin of the American Meteorological Society, 93(12), 1879-1900.
    - Urban heat island research showing temperature differences between LCZ types
    """

    def __init__(self):
        self.lcz_classes = LCZ_CLASSES

    def calculate_temperature_delta(self, from_lcz, to_lcz, base_temperature):
        """
        Calculate temperature change when converting from one LCZ to another

        Args:
            from_lcz: Original LCZ class number
            to_lcz: Target LCZ class number
            base_temperature: Current temperature in Celsius

        Returns:
            dict: {
                'new_temperature': float,
                'delta': float,
                'explanation': str
            }

        Methodology:
        The temperature offset for each LCZ represents the typical temperature
        difference from LCZ 14 (Low Plants) which serves as the baseline (0°C offset).

        These values are derived from empirical studies showing:
        - Compact urban forms (LCZ 1-3): +2.3 to +2.8°C
        - Open urban forms (LCZ 4-6): +1.5 to +2.0°C
        - Lightweight/scattered (LCZ 7, 9): +0.5 to +1.2°C
        - Industrial (LCZ 8, 10): +2.2 to +2.6°C
        - Vegetation (LCZ 11-13): -1.5 to -0.3°C
        - Water (LCZ 17): -2.0°C

        References:
        - Stewart & Oke (2012): LCZ framework and thermal properties
        - Systematic reviews showing LCZ 2 (Compact Mid-Rise) as hottest (+2.8°C)
        - Studies showing vegetation reduces temperature by 0.3-1.5°C
        - Water bodies showing -2.0°C cooling effect
        """

        if from_lcz not in self.lcz_classes or to_lcz not in self.lcz_classes:
            return None

        from_offset = self.lcz_classes[from_lcz]['thermal_offset']
        to_offset = self.lcz_classes[to_lcz]['thermal_offset']

        # Calculate the temperature change
        delta = to_offset - from_offset

        # Calculate new temperature
        new_temperature = base_temperature + delta

        # Generate explanation
        from_name = self.lcz_classes[from_lcz]['name']
        to_name = self.lcz_classes[to_lcz]['name']

        if delta > 0:
            direction = "increase"
            effect = "warming"
        elif delta < 0:
            direction = "decrease"
            effect = "cooling"
        else:
            direction = "remain the same"
            effect = "no change"

        explanation = (
            f"Converting from LCZ {from_lcz} ({from_name}) to LCZ {to_lcz} ({to_name}) "
            f"will {direction} the temperature by {abs(delta):.2f}°C, "
            f"resulting in a {effect} effect. "
            f"This is based on the thermal offset difference between the two LCZ types."
        )

        return {
            'new_temperature': round(new_temperature, 2),
            'delta': round(delta, 2),
            'from_lcz': from_lcz,
            'to_lcz': to_lcz,
            'from_name': from_name,
            'to_name': to_name,
            'base_temperature': round(base_temperature, 2),
            'explanation': explanation
        }

    def calculate_bulk_temperature_change(self, zone_changes, temperature_data):
        """
        Calculate temperature changes for multiple zone modifications

        Args:
            zone_changes: List of dicts with 'zone_id', 'from_lcz', 'to_lcz'
            temperature_data: Dict mapping zone_id to current temperature

        Returns:
            dict: Modified temperature data with changes applied
        """
        modified_temps = temperature_data.copy()

        for change in zone_changes:
            zone_id = change['zone_id']
            from_lcz = change['from_lcz']
            to_lcz = change['to_lcz']

            if zone_id in temperature_data:
                base_temp = temperature_data[zone_id]
                result = self.calculate_temperature_delta(from_lcz, to_lcz, base_temp)

                if result:
                    modified_temps[zone_id] = result['new_temperature']

        return modified_temps

    def get_lcz_thermal_properties(self, lcz_class):
        """Get thermal properties for a specific LCZ class"""
        if lcz_class in self.lcz_classes:
            return {
                'lcz_class': lcz_class,
                'name': self.lcz_classes[lcz_class]['name'],
                'thermal_offset': self.lcz_classes[lcz_class]['thermal_offset'],
                'color': self.lcz_classes[lcz_class]['color']
            }
        return None

    def get_all_thermal_properties(self):
        """Get thermal properties for all LCZ classes"""
        return {
            lcz: self.get_lcz_thermal_properties(lcz)
            for lcz in self.lcz_classes.keys()
        }
