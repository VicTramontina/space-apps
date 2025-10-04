"""
Módulo para simulação de cenários de mudança de LCZ
"""
import pandas as pd
import geopandas as gpd
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioSimulator:
    """Simulador de cenários de mudança de Local Climate Zones"""

    def __init__(self, lcz_processor, stats: pd.DataFrame):
        """
        Inicializa simulador

        Args:
            lcz_processor: Instância de LCZProcessor
            stats: DataFrame com estatísticas de temperatura por LCZ
        """
        self.lcz_processor = lcz_processor
        self.stats = stats

    def simulate_single_zone_change(
        self,
        zone_id: int,
        new_class: str
    ) -> Dict:
        """
        Simula mudança de uma zona específica

        Args:
            zone_id: ID da zona no GeoDataFrame
            new_class: Nova classe LCZ

        Returns:
            Dicionário com resultados da simulação
        """
        zone = self.lcz_processor.gdf.loc[zone_id]
        old_class = zone['lcz_class']

        # Obter temperaturas das classes
        old_temp = self.stats[self.stats['lcz_class'] == old_class]['mean_temp'].values[0]
        new_temp = self.stats[self.stats['lcz_class'] == new_class]['mean_temp'].values[0]

        # Calcular mudança
        temp_change = new_temp - old_temp

        result = {
            'zone_id': zone_id,
            'old_class': old_class,
            'new_class': new_class,
            'old_temp': old_temp,
            'new_temp': new_temp,
            'temp_change': temp_change,
            'area_km2': zone['area_km2'],
            'centroid_lat': zone['centroid_lat'],
            'centroid_lon': zone['centroid_lon']
        }

        return result

    def simulate_urbanization_scenario(
        self,
        vegetation_classes: List[str] = ['A', 'B', 'D'],
        target_class: str = '2',
        conversion_rate: float = 0.5
    ) -> Dict:
        """
        Simula cenário de urbanização convertendo vegetação em área construída

        Args:
            vegetation_classes: Classes LCZ de vegetação a converter
            target_class: Classe LCZ de destino (urbana)
            conversion_rate: Taxa de conversão (0-1)

        Returns:
            Dicionário com resultados agregados
        """
        gdf = self.lcz_processor.gdf.copy()

        # Filtrar zonas de vegetação
        veg_zones = gdf[gdf['lcz_class'].isin(vegetation_classes)]

        if len(veg_zones) == 0:
            raise ValueError("Nenhuma zona de vegetação encontrada")

        # Calcular área total a ser convertida
        total_area = veg_zones['area_km2'].sum() * conversion_rate

        # Obter temperaturas
        veg_temps = []
        for cls in vegetation_classes:
            temp = self.stats[self.stats['lcz_class'] == cls]['mean_temp'].values
            if len(temp) > 0:
                veg_temps.append(temp[0])

        avg_veg_temp = sum(veg_temps) / len(veg_temps) if veg_temps else None

        target_temp = self.stats[self.stats['lcz_class'] == target_class]['mean_temp'].values
        target_temp = target_temp[0] if len(target_temp) > 0 else None

        if avg_veg_temp is None or target_temp is None:
            raise ValueError("Dados de temperatura insuficientes")

        # Calcular impacto
        temp_increase = (target_temp - avg_veg_temp) * conversion_rate

        result = {
            'scenario_type': 'urbanization',
            'vegetation_classes': vegetation_classes,
            'target_class': target_class,
            'conversion_rate': conversion_rate,
            'total_area_converted_km2': total_area,
            'avg_vegetation_temp': avg_veg_temp,
            'target_urban_temp': target_temp,
            'expected_temp_increase': temp_increase,
            'num_zones_affected': len(veg_zones)
        }

        return result

    def simulate_greening_scenario(
        self,
        urban_classes: List[str] = ['2', '3', '6'],
        target_class: str = 'A',
        conversion_rate: float = 0.3
    ) -> Dict:
        """
        Simula cenário de revegetação convertendo área urbana em verde

        Args:
            urban_classes: Classes LCZ urbanas a converter
            target_class: Classe LCZ de destino (vegetação)
            conversion_rate: Taxa de conversão (0-1)

        Returns:
            Dicionário com resultados agregados
        """
        gdf = self.lcz_processor.gdf.copy()

        # Filtrar zonas urbanas
        urban_zones = gdf[gdf['lcz_class'].isin(urban_classes)]

        if len(urban_zones) == 0:
            raise ValueError("Nenhuma zona urbana encontrada")

        # Calcular área total a ser convertida
        total_area = urban_zones['area_km2'].sum() * conversion_rate

        # Obter temperaturas
        urban_temps = []
        for cls in urban_classes:
            temp = self.stats[self.stats['lcz_class'] == cls]['mean_temp'].values
            if len(temp) > 0:
                urban_temps.append(temp[0])

        avg_urban_temp = sum(urban_temps) / len(urban_temps) if urban_temps else None

        target_temp = self.stats[self.stats['lcz_class'] == target_class]['mean_temp'].values
        target_temp = target_temp[0] if len(target_temp) > 0 else None

        if avg_urban_temp is None or target_temp is None:
            raise ValueError("Dados de temperatura insuficientes")

        # Calcular impacto
        temp_decrease = (target_temp - avg_urban_temp) * conversion_rate

        result = {
            'scenario_type': 'greening',
            'urban_classes': urban_classes,
            'target_class': target_class,
            'conversion_rate': conversion_rate,
            'total_area_converted_km2': total_area,
            'avg_urban_temp': avg_urban_temp,
            'target_vegetation_temp': target_temp,
            'expected_temp_decrease': temp_decrease,
            'num_zones_affected': len(urban_zones)
        }

        return result

    def compare_scenarios(self, scenarios: List[Dict]) -> pd.DataFrame:
        """
        Compara múltiplos cenários

        Args:
            scenarios: Lista de resultados de cenários

        Returns:
            DataFrame comparativo
        """
        comparison_data = []

        for i, scenario in enumerate(scenarios):
            if scenario['scenario_type'] == 'urbanization':
                comparison_data.append({
                    'scenario_id': i + 1,
                    'type': 'Urbanização',
                    'from_classes': ', '.join(scenario['vegetation_classes']),
                    'to_class': scenario['target_class'],
                    'conversion_rate': f"{scenario['conversion_rate']*100:.0f}%",
                    'area_affected_km2': scenario['total_area_converted_km2'],
                    'temp_change': scenario['expected_temp_increase'],
                    'impact': 'Aquecimento' if scenario['expected_temp_increase'] > 0 else 'Resfriamento'
                })
            elif scenario['scenario_type'] == 'greening':
                comparison_data.append({
                    'scenario_id': i + 1,
                    'type': 'Revegetação',
                    'from_classes': ', '.join(scenario['urban_classes']),
                    'to_class': scenario['target_class'],
                    'conversion_rate': f"{scenario['conversion_rate']*100:.0f}%",
                    'area_affected_km2': scenario['total_area_converted_km2'],
                    'temp_change': scenario['expected_temp_decrease'],
                    'impact': 'Aquecimento' if scenario['expected_temp_decrease'] > 0 else 'Resfriamento'
                })

        return pd.DataFrame(comparison_data)

    def create_what_if_scenarios(self) -> List[Dict]:
        """
        Cria cenários pré-definidos para análise

        Returns:
            Lista de cenários simulados
        """
        scenarios = []

        # Cenário 1: Urbanização moderada
        try:
            scenarios.append(
                self.simulate_urbanization_scenario(
                    vegetation_classes=['B', 'D'],
                    target_class='6',  # Open low-rise
                    conversion_rate=0.3
                )
            )
        except ValueError as e:
            logger.warning(f"Cenário 1 não pôde ser criado: {e}")

        # Cenário 2: Urbanização intensa
        try:
            scenarios.append(
                self.simulate_urbanization_scenario(
                    vegetation_classes=['A', 'B', 'D'],
                    target_class='2',  # Compact midrise
                    conversion_rate=0.5
                )
            )
        except ValueError as e:
            logger.warning(f"Cenário 2 não pôde ser criado: {e}")

        # Cenário 3: Revegetação leve
        try:
            scenarios.append(
                self.simulate_greening_scenario(
                    urban_classes=['6', '9'],
                    target_class='B',  # Scattered trees
                    conversion_rate=0.2
                )
            )
        except ValueError as e:
            logger.warning(f"Cenário 3 não pôde ser criado: {e}")

        # Cenário 4: Revegetação intensa
        try:
            scenarios.append(
                self.simulate_greening_scenario(
                    urban_classes=['2', '3', '6'],
                    target_class='A',  # Dense trees
                    conversion_rate=0.4
                )
            )
        except ValueError as e:
            logger.warning(f"Cenário 4 não pôde ser criado: {e}")

        return scenarios


if __name__ == "__main__":
    print("Módulo de simulação de cenários carregado com sucesso!")
    print("\nFuncionalidades disponíveis:")
    print("- Simulação de mudança de zonas individuais")
    print("- Cenários de urbanização")
    print("- Cenários de revegetação")
    print("- Comparação entre cenários")
