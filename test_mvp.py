#!/usr/bin/env python3
"""
Testes básicos para verificar funcionamento do MVP
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando imports...")

    try:
        import pandas
        print("  ✓ pandas")
    except ImportError as e:
        print(f"  ✗ pandas: {e}")
        return False

    try:
        import geopandas
        print("  ✓ geopandas")
    except ImportError as e:
        print(f"  ✗ geopandas: {e}")
        return False

    try:
        import matplotlib
        print("  ✓ matplotlib")
    except ImportError as e:
        print(f"  ✗ matplotlib: {e}")
        return False

    try:
        import seaborn
        print("  ✓ seaborn")
    except ImportError as e:
        print(f"  ✗ seaborn: {e}")
        return False

    try:
        import folium
        print("  ✓ folium")
    except ImportError as e:
        print(f"  ✗ folium: {e}")
        return False

    try:
        import shapely
        print("  ✓ shapely")
    except ImportError as e:
        print(f"  ✗ shapely: {e}")
        return False

    try:
        import requests
        print("  ✓ requests")
    except ImportError as e:
        print(f"  ✗ requests: {e}")
        return False

    return True


def test_modules():
    """Testa se os módulos do projeto podem ser importados"""
    print("\nTestando módulos do projeto...")

    try:
        import lcz_processor
        print("  ✓ lcz_processor")
    except ImportError as e:
        print(f"  ✗ lcz_processor: {e}")
        return False

    try:
        import meteomatics_api
        print("  ✓ meteomatics_api")
    except ImportError as e:
        print(f"  ✗ meteomatics_api: {e}")
        return False

    try:
        import visualizer
        print("  ✓ visualizer")
    except ImportError as e:
        print(f"  ✗ visualizer: {e}")
        return False

    try:
        import scenario_simulator
        print("  ✓ scenario_simulator")
    except ImportError as e:
        print(f"  ✗ scenario_simulator: {e}")
        return False

    return True


def test_kml_file():
    """Testa se o arquivo KML existe"""
    print("\nTestando arquivo KML...")

    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"

    if os.path.exists(kml_path):
        print(f"  ✓ Arquivo encontrado: {kml_path}")
        return True
    else:
        print(f"  ✗ Arquivo não encontrado: {kml_path}")
        return False


def test_lcz_processor():
    """Testa funcionalidades básicas do LCZProcessor"""
    print("\nTestando LCZProcessor...")

    try:
        from lcz_processor import LCZProcessor

        kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"

        if not os.path.exists(kml_path):
            print(f"  ⚠ Arquivo KML não encontrado: {kml_path}")
            return False

        processor = LCZProcessor(kml_path)

        # Verificar se carregou dados
        if len(processor.gdf) == 0:
            print("  ✗ Nenhuma zona LCZ carregada")
            return False

        print(f"  ✓ Carregadas {len(processor.gdf)} zonas LCZ")

        # Verificar classes
        classes = processor.gdf['lcz_class'].unique()
        print(f"  ✓ Classes encontradas: {sorted(classes)}")

        # Testar ponto de amostragem
        points = processor.get_sampling_points(points_per_zone=2)
        print(f"  ✓ Gerados {len(points)} pontos de amostragem")

        return True

    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


def test_synthetic_data():
    """Testa geração de dados sintéticos"""
    print("\nTestando geração de dados sintéticos...")

    try:
        from lcz_processor import LCZProcessor
        import pandas as pd
        import numpy as np

        kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"

        if not os.path.exists(kml_path):
            print("  ⚠ Arquivo KML não encontrado")
            return False

        processor = LCZProcessor(kml_path)

        # Gerar dados sintéticos
        records = []
        base_temp = 28.0

        for idx, row in processor.gdf.iterrows():
            lcz_class = row['lcz_class']
            delta = row['temp_delta_expected']

            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'],
                'lon': row['centroid_lon'],
                'temperature': round(temp, 1)
            })

        df_temp = pd.DataFrame(records)
        print(f"  ✓ Gerados {len(df_temp)} pontos de temperatura")

        # Associar LCZ
        df_temp = processor.assign_lcz_to_points(df_temp)
        associated = df_temp['lcz_class'].notna().sum()
        print(f"  ✓ {associated}/{len(df_temp)} pontos associados a LCZ")

        # Calcular estatísticas
        stats = processor.calculate_lcz_statistics(df_temp)
        print(f"  ✓ Estatísticas calculadas para {len(stats)} classes")

        return True

    except Exception as e:
        print(f"  ✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizations():
    """Testa criação de visualizações"""
    print("\nTestando visualizações...")

    try:
        from lcz_processor import LCZProcessor
        from visualizer import Visualizer
        import pandas as pd
        import numpy as np

        kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"

        if not os.path.exists(kml_path):
            print("  ⚠ Arquivo KML não encontrado")
            return False

        processor = LCZProcessor(kml_path)

        # Gerar dados sintéticos
        records = []
        base_temp = 28.0

        for idx, row in processor.gdf.iterrows():
            lcz_class = row['lcz_class']
            delta = row['temp_delta_expected']
            temp = base_temp + delta + np.random.normal(0, 0.5)
            records.append({
                'lat': row['centroid_lat'],
                'lon': row['centroid_lon'],
                'temperature': round(temp, 1)
            })

        df_temp = pd.DataFrame(records)
        df_temp = processor.assign_lcz_to_points(df_temp)
        stats = processor.calculate_lcz_statistics(df_temp)

        viz = Visualizer()

        # Criar diretório de teste
        test_dir = Path('test_output')
        test_dir.mkdir(exist_ok=True)

        # Testar gráficos
        viz.plot_temperature_by_lcz(stats, str(test_dir / 'test_temp_by_lcz.png'))
        print(f"  ✓ Gráfico de temperatura criado")

        viz.plot_temperature_delta(stats, str(test_dir / 'test_temp_delta.png'))
        print(f"  ✓ Gráfico de delta criado")

        viz.create_interactive_map(processor.gdf, stats, str(test_dir / 'test_map.html'))
        print(f"  ✓ Mapa interativo criado")

        print(f"  ℹ Visualizações salvas em: {test_dir.absolute()}")

        return True

    except Exception as e:
        print(f"  ✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("="*60)
    print("TESTES DO MVP - PLANEJADOR URBANO")
    print("="*60)

    results = []

    # Teste 1: Imports
    results.append(("Imports de bibliotecas", test_imports()))

    # Teste 2: Módulos do projeto
    results.append(("Módulos do projeto", test_modules()))

    # Teste 3: Arquivo KML
    results.append(("Arquivo KML", test_kml_file()))

    # Teste 4: LCZ Processor
    results.append(("LCZ Processor", test_lcz_processor()))

    # Teste 5: Dados sintéticos
    results.append(("Dados sintéticos", test_synthetic_data()))

    # Teste 6: Visualizações
    results.append(("Visualizações", test_visualizations()))

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status}: {test_name}")

    print("\n" + "="*60)
    if passed == total:
        print(f"✅ TODOS OS TESTES PASSARAM ({passed}/{total})")
        print("="*60)
        print("\nO MVP está pronto para uso!")
        print("Execute: python main.py --skip-api")
        return 0
    else:
        print(f"⚠️  ALGUNS TESTES FALHARAM ({passed}/{total})")
        print("="*60)
        print("\nVerifique os erros acima.")
        print("Instale as dependências: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
