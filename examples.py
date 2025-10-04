#!/usr/bin/env python3
"""
Exemplos de uso das funcionalidades do MVP
"""

import pandas as pd
from lcz_processor import LCZProcessor
from meteomatics_api import MeteomaticsAPI
from visualizer import Visualizer
from scenario_simulator import ScenarioSimulator
from datetime import datetime


def example_1_load_and_analyze_lcz():
    """Exemplo 1: Carregar e analisar dados LCZ"""
    print("="*60)
    print("EXEMPLO 1: Carregar e Analisar Dados LCZ")
    print("="*60)

    # Carregar arquivo KML
    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"
    processor = LCZProcessor(kml_path)

    # Mostrar informações básicas
    print(f"\nTotal de zonas: {len(processor.gdf)}")
    print(f"Classes presentes: {sorted(processor.gdf['lcz_class'].unique())}")

    # Estatísticas por classe
    area_por_classe = processor.gdf.groupby('lcz_class')['area_km2'].sum()
    print("\nÁrea por classe LCZ (km²):")
    print(area_por_classe.sort_values(ascending=False))

    # Zona com maior área
    maior_zona = processor.gdf.loc[processor.gdf['area_km2'].idxmax()]
    print(f"\nMaior zona: LCZ {maior_zona['lcz_class']} com {maior_zona['area_km2']:.3f} km²")


def example_2_temperature_analysis():
    """Exemplo 2: Análise de temperatura com dados simulados"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Análise de Temperatura")
    print("="*60)

    # Carregar LCZ
    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"
    processor = LCZProcessor(kml_path)

    # Gerar dados sintéticos (substitua por dados reais da API)
    import numpy as np

    records = []
    base_temp = 28.0

    for idx, row in processor.gdf.iterrows():
        lcz_class = row['lcz_class']
        delta = row['temp_delta_expected']

        for _ in range(5):
            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'] + np.random.normal(0, 0.001),
                'lon': row['centroid_lon'] + np.random.normal(0, 0.001),
                'temperature': round(temp, 1)
            })

    df_temp = pd.DataFrame(records)

    # Associar LCZ
    df_temp = processor.assign_lcz_to_points(df_temp)

    # Calcular estatísticas
    stats = processor.calculate_lcz_statistics(df_temp)

    print("\nTemperatura média por classe:")
    print(stats[['lcz_class', 'description', 'mean_temp']].to_string(index=False))

    # Identificar ilha de calor
    hottest = stats.iloc[0]
    coldest = stats.iloc[-1]

    print(f"\n🔥 Ilha de calor: LCZ {hottest['lcz_class']} ({hottest['description']})")
    print(f"   Temperatura: {hottest['mean_temp']:.1f}°C")

    print(f"\n❄️  Zona mais fria: LCZ {coldest['lcz_class']} ({coldest['description']})")
    print(f"   Temperatura: {coldest['mean_temp']:.1f}°C")

    print(f"\n📊 Diferença: {hottest['mean_temp'] - coldest['mean_temp']:.1f}°C")


def example_3_scenario_simulation():
    """Exemplo 3: Simulação de cenários"""
    print("\n" + "="*60)
    print("EXEMPLO 3: Simulação de Cenários")
    print("="*60)

    # Setup
    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"
    processor = LCZProcessor(kml_path)

    # Gerar dados sintéticos
    import numpy as np
    records = []
    base_temp = 28.0

    for idx, row in processor.gdf.iterrows():
        lcz_class = row['lcz_class']
        delta = row['temp_delta_expected']
        for _ in range(5):
            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'] + np.random.normal(0, 0.001),
                'lon': row['centroid_lon'] + np.random.normal(0, 0.001),
                'temperature': round(temp, 1)
            })

    df_temp = pd.DataFrame(records)
    df_temp = processor.assign_lcz_to_points(df_temp)
    stats = processor.calculate_lcz_statistics(df_temp)

    # Criar simulador
    simulator = ScenarioSimulator(processor, stats)

    # Cenário 1: Urbanização
    print("\n🏗️  CENÁRIO 1: Urbanização de Área Verde")
    try:
        scenario1 = simulator.simulate_urbanization_scenario(
            vegetation_classes=['A', 'B', 'D'],
            target_class='2',  # Compact midrise
            conversion_rate=0.5
        )
        print(f"  Converter 50% de LCZ A/B/D → LCZ 2")
        print(f"  Área afetada: {scenario1['total_area_converted_km2']:.2f} km²")
        print(f"  Impacto térmico: {scenario1['expected_temp_increase']:+.1f}°C")
    except ValueError as e:
        print(f"  Erro: {e}")

    # Cenário 2: Revegetação
    print("\n🌳 CENÁRIO 2: Revegetação de Área Urbana")
    try:
        scenario2 = simulator.simulate_greening_scenario(
            urban_classes=['2', '3', '6'],
            target_class='A',  # Dense trees
            conversion_rate=0.3
        )
        print(f"  Converter 30% de LCZ 2/3/6 → LCZ A")
        print(f"  Área afetada: {scenario2['total_area_converted_km2']:.2f} km²")
        print(f"  Impacto térmico: {scenario2['expected_temp_decrease']:+.1f}°C")
    except ValueError as e:
        print(f"  Erro: {e}")

    # Comparar cenários
    print("\n📊 Comparação de Cenários:")
    scenarios = []
    try:
        scenarios = [scenario1, scenario2]
        comparison = simulator.compare_scenarios(scenarios)
        print(comparison.to_string(index=False))
    except:
        print("  Dados insuficientes para comparação")


def example_4_custom_scenario():
    """Exemplo 4: Cenário personalizado"""
    print("\n" + "="*60)
    print("EXEMPLO 4: Cenário Personalizado")
    print("="*60)

    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"
    processor = LCZProcessor(kml_path)

    # Simular mudança de uma classe para outra
    from_class = '6'  # Open low-rise
    to_class = 'A'    # Dense trees

    print(f"\n🔄 Simulando: LCZ {from_class} → LCZ {to_class}")

    # Gerar dados sintéticos
    import numpy as np
    records = []
    base_temp = 28.0

    for idx, row in processor.gdf.iterrows():
        lcz_class = row['lcz_class']
        delta = row['temp_delta_expected']
        for _ in range(5):
            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'] + np.random.normal(0, 0.001),
                'lon': row['centroid_lon'] + np.random.normal(0, 0.001),
                'temperature': round(temp, 1)
            })

    df_temp = pd.DataFrame(records)
    df_temp = processor.assign_lcz_to_points(df_temp)
    stats = processor.calculate_lcz_statistics(df_temp)

    # Usar método do processador
    result = processor.simulate_lcz_change(stats, from_class, to_class, area_fraction=1.0)

    print(f"\nDe: {result['from_description']}")
    print(f"Para: {result['to_description']}")
    print(f"Mudança observada: {result['observed_change']:+.1f}°C")
    print(f"Mudança esperada: {result['expected_change']:+.1f}°C")
    print(f"Interpretação: {result['interpretation']}")


def example_5_create_visualizations():
    """Exemplo 5: Criar visualizações"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Criar Visualizações")
    print("="*60)

    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"
    processor = LCZProcessor(kml_path)

    # Gerar dados sintéticos
    import numpy as np
    records = []
    base_temp = 28.0

    for idx, row in processor.gdf.iterrows():
        lcz_class = row['lcz_class']
        delta = row['temp_delta_expected']
        for _ in range(5):
            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'] + np.random.normal(0, 0.001),
                'lon': row['centroid_lon'] + np.random.normal(0, 0.001),
                'temperature': round(temp, 1)
            })

    df_temp = pd.DataFrame(records)
    df_temp = processor.assign_lcz_to_points(df_temp)
    stats = processor.calculate_lcz_statistics(df_temp)

    # Criar visualizações
    viz = Visualizer()

    print("\nGerando visualizações...")

    # Gráfico de temperatura
    viz.plot_temperature_by_lcz(stats, 'examples_temp_by_lcz.png')
    print("✓ examples_temp_by_lcz.png")

    # Gráfico de delta
    viz.plot_temperature_delta(stats, 'examples_temp_delta.png')
    print("✓ examples_temp_delta.png")

    # Mapa interativo
    viz.create_interactive_map(processor.gdf, stats, 'examples_map.html')
    print("✓ examples_map.html")

    print("\nVisualizações criadas com sucesso!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXEMPLOS DE USO DO MVP")
    print("="*60)

    # Executar todos os exemplos
    example_1_load_and_analyze_lcz()
    example_2_temperature_analysis()
    example_3_scenario_simulation()
    example_4_custom_scenario()
    example_5_create_visualizations()

    print("\n" + "="*60)
    print("EXEMPLOS CONCLUÍDOS!")
    print("="*60)
    print("\nPróximos passos:")
    print("1. Execute: python main.py --skip-api")
    print("2. Explore os arquivos gerados em output/")
    print("3. Customize os cenários em scenario_simulator.py")
    print("4. Adicione seus próprios dados LCZ")
