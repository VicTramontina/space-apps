
#!/usr/bin/env python3
"""
MVP - Planejador Urbano com Análise de LCZ e Temperatura
Cidade: Lajeado-RS

Este script:
1. Carrega mapa LCZ de Lajeado-RS
2. Coleta dados de temperatura via API Meteomatics
3. Calcula estatísticas por classe LCZ
4. Gera visualizações e mapas interativos
5. Permite simular cenários de mudança urbana
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from lcz_processor import LCZProcessor
from meteomatics_api import MeteomaticsAPI
from visualizer import Visualizer
from scenario_simulator import ScenarioSimulator

# Tentar carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv não instalado, continuar sem ele
    pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal do MVP"""

    # Argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description='MVP Planejador Urbano - Análise LCZ e Temperatura'
    )
    parser.add_argument(
        '--kml',
        type=str,
        default='lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml',
        help='Caminho para arquivo KML com zonas LCZ'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Diretório para salvar resultados'
    )
    parser.add_argument(
        '--skip-api',
        action='store_true',
        help='Pular coleta de dados da API (usar dados simulados)'
    )
    parser.add_argument(
        '--username',
        type=str,
        help='Username da API Meteomatics (ou use variável de ambiente METEOMATICS_USERNAME)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Password da API Meteomatics (ou use variável de ambiente METEOMATICS_PASSWORD)'
    )

    args = parser.parse_args()

    # Criar diretório de saída
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    logger.info("="*60)
    logger.info("MVP - Planejador Urbano com Análise LCZ")
    logger.info("Cidade: Lajeado-RS")
    logger.info("="*60)

    # ==========================================
    # ETAPA 1: Carregar dados LCZ
    # ==========================================
    logger.info("\n[1/6] Carregando mapa de Zonas Climáticas Locais (LCZ)...")

    if not os.path.exists(args.kml):
        logger.error(f"Arquivo KML não encontrado: {args.kml}")
        sys.exit(1)

    processor = LCZProcessor(args.kml)

    logger.info(f"✓ Carregadas {len(processor.gdf)} zonas LCZ")
    logger.info(f"✓ Classes encontradas: {sorted(processor.gdf['lcz_class'].unique())}")

    # ==========================================
    # ETAPA 2: Coletar dados de temperatura
    # ==========================================
    logger.info("\n[2/6] Coletando dados de temperatura...")

    if args.skip_api:
        logger.info("Modo simulação: gerando dados sintéticos...")
        df_temp = generate_synthetic_temperature_data(processor)
    else:
        # Obter credenciais
        username = args.username or os.getenv('METEOMATICS_USERNAME')
        password = args.password or os.getenv('METEOMATICS_PASSWORD')

        if not username or not password:
            logger.error(
                "Credenciais da API não fornecidas!\n"
                "Use --username e --password ou configure variáveis de ambiente:\n"
                "  METEOMATICS_USERNAME\n"
                "  METEOMATICS_PASSWORD\n\n"
                "Ou use --skip-api para modo simulação"
            )
            sys.exit(1)

        # Coletar dados via API
        api = MeteomaticsAPI(username, password)

        # Gerar pontos de amostragem
        points = processor.get_sampling_points(points_per_zone=5)

        try:
            logger.info(f"Consultando API para {len(points)} pontos...")
            logger.info("(Isso pode levar alguns minutos...)")

            # Obter temperatura dos pontos
            from datetime import timezone
            now = datetime.now(timezone.utc)
            df_temp = api.get_temperature_points(points, timestamp=now)

            logger.info(f"✓ Coletados dados de {len(df_temp)} pontos")

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Interrompido pelo usuário!")
            logger.info("Usando dados simulados como alternativa...")
            df_temp = generate_synthetic_temperature_data(processor)
        except Exception as e:
            logger.error(f"Erro ao coletar dados da API: {e}")
            logger.info("Usando dados simulados como alternativa...")
            df_temp = generate_synthetic_temperature_data(processor)

    # Associar classes LCZ aos pontos
    df_temp = processor.assign_lcz_to_points(df_temp)

    # Salvar dados brutos
    csv_path = output_dir / 'temperature_data.csv'
    df_temp.to_csv(csv_path, index=False)
    logger.info(f"✓ Dados salvos em: {csv_path}")

    # ==========================================
    # ETAPA 3: Calcular estatísticas por LCZ
    # ==========================================
    logger.info("\n[3/6] Calculando estatísticas por classe LCZ...")

    stats = processor.calculate_lcz_statistics(df_temp)

    print("\n📊 ESTATÍSTICAS DE TEMPERATURA POR CLASSE LCZ:")
    print("="*80)
    print(stats[['lcz_class', 'description', 'mean_temp', 'std_temp', 'count']].to_string(index=False))
    print("="*80)

    # Salvar estatísticas
    stats_path = output_dir / 'lcz_statistics.csv'
    stats.to_csv(stats_path, index=False)
    logger.info(f"✓ Estatísticas salvas em: {stats_path}")

    # ==========================================
    # ETAPA 4: Gerar visualizações
    # ==========================================
    logger.info("\n[4/6] Gerando visualizações...")

    # Gráfico de temperatura por LCZ
    viz = Visualizer()

    chart1_path = output_dir / 'temperature_by_lcz.png'
    viz.plot_temperature_by_lcz(stats, str(chart1_path))
    logger.info(f"✓ Gráfico criado: {chart1_path}")

    # Gráfico de diferença de temperatura
    chart2_path = output_dir / 'temperature_delta.png'
    viz.plot_temperature_delta(stats, str(chart2_path))
    logger.info(f"✓ Gráfico criado: {chart2_path}")

    # Mapa interativo
    map_path = output_dir / 'lcz_map.html'
    viz.create_interactive_map(processor.gdf, stats, str(map_path))
    logger.info(f"✓ Mapa interativo criado: {map_path}")

    # ==========================================
    # ETAPA 5: Simular cenários
    # ==========================================
    logger.info("\n[5/6] Simulando cenários de mudança urbana...")

    simulator = ScenarioSimulator(processor, stats)

    # Criar cenários pré-definidos
    scenarios = simulator.create_what_if_scenarios()

    if scenarios:
        # Comparar cenários
        comparison = simulator.compare_scenarios(scenarios)

        print("\n🔮 CENÁRIOS DE MUDANÇA URBANA:")
        print("="*80)
        print(comparison.to_string(index=False))
        print("="*80)

        # Salvar comparação
        scenarios_path = output_dir / 'scenarios_comparison.csv'
        comparison.to_csv(scenarios_path, index=False)
        logger.info(f"✓ Cenários salvos em: {scenarios_path}")

        # Visualizar primeiro cenário como exemplo
        if len(scenarios) > 0:
            scenario_result = scenarios[0]

            # Converter para formato esperado pela visualização
            scenario_viz = {
                'from_class': scenario_result.get('vegetation_classes', scenario_result.get('urban_classes', []))[0],
                'from_description': 'Área de origem',
                'to_class': scenario_result['target_class'],
                'to_description': 'Área de destino',
                'from_temp': scenario_result.get('avg_vegetation_temp', scenario_result.get('avg_urban_temp', 0)),
                'to_temp': scenario_result.get('target_urban_temp', scenario_result.get('target_vegetation_temp', 0)),
                'observed_change': scenario_result.get('expected_temp_increase', scenario_result.get('expected_temp_decrease', 0)),
                'expected_change': scenario_result.get('expected_temp_increase', scenario_result.get('expected_temp_decrease', 0)),
                'interpretation': 'Cenário de ' + scenario_result['scenario_type']
            }

            scenario_chart_path = output_dir / 'scenario_example.png'
            viz.plot_scenario_comparison(scenario_viz, str(scenario_chart_path))
            logger.info(f"✓ Gráfico de cenário criado: {scenario_chart_path}")
    else:
        logger.warning("Nenhum cenário pôde ser criado (dados insuficientes)")

    # ==========================================
    # ETAPA 6: Gerar relatório
    # ==========================================
    logger.info("\n[6/6] Gerando relatório final...")

    report_path = output_dir / 'relatorio.txt'
    generate_report(processor, stats, scenarios if scenarios else [], report_path)
    logger.info(f"✓ Relatório gerado: {report_path}")

    # ==========================================
    # FINALIZAÇÃO
    # ==========================================
    logger.info("\n" + "="*60)
    logger.info("✅ MVP CONCLUÍDO COM SUCESSO!")
    logger.info("="*60)
    logger.info(f"\n📁 Todos os resultados foram salvos em: {output_dir.absolute()}")
    logger.info("\n📋 Arquivos gerados:")
    logger.info(f"  - {csv_path.name} - Dados de temperatura")
    logger.info(f"  - {stats_path.name} - Estatísticas por LCZ")
    logger.info(f"  - {chart1_path.name} - Gráfico de temperatura")
    logger.info(f"  - {chart2_path.name} - Gráfico de diferenças")
    logger.info(f"  - {map_path.name} - Mapa interativo")
    if scenarios:
        logger.info(f"  - {scenarios_path.name} - Comparação de cenários")
    logger.info(f"  - {report_path.name} - Relatório final")
    logger.info("\n🌐 Para visualizar o mapa interativo, abra o arquivo:")
    logger.info(f"  {map_path.absolute()}")
    logger.info("")


def generate_synthetic_temperature_data(processor: LCZProcessor) -> pd.DataFrame:
    """
    Gera dados sintéticos de temperatura para demonstração

    Args:
        processor: Instância de LCZProcessor

    Returns:
        DataFrame com dados sintéticos
    """
    import numpy as np

    logger.info("Gerando dados sintéticos baseados em valores típicos de LCZ...")

    records = []

    # Base de temperatura (típica para Lajeado-RS no verão)
    base_temp = 28.0

    for idx, row in processor.gdf.iterrows():
        lcz_class = row['lcz_class']
        delta = row['temp_delta_expected']

        # Gerar 5 pontos por zona com variação aleatória
        for _ in range(5):
            temp = base_temp + delta + np.random.normal(0, 0.5)

            records.append({
                'lat': row['centroid_lat'] + np.random.normal(0, 0.001),
                'lon': row['centroid_lon'] + np.random.normal(0, 0.001),
                'temperature': round(temp, 1)
            })

    return pd.DataFrame(records)


def generate_report(
    processor: LCZProcessor,
    stats: pd.DataFrame,
    scenarios: list,
    output_path: Path
):
    """
    Gera relatório em texto

    Args:
        processor: Instância de LCZProcessor
        stats: DataFrame com estatísticas
        scenarios: Lista de cenários simulados
        output_path: Caminho do arquivo de saída
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO - ANÁLISE DE ZONAS CLIMÁTICAS LOCAIS (LCZ)\n")
        f.write("Cidade: Lajeado-RS\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write("="*80 + "\n\n")

        f.write("1. RESUMO EXECUTIVO\n")
        f.write("-"*80 + "\n")
        f.write(f"Total de zonas LCZ mapeadas: {len(processor.gdf)}\n")
        f.write(f"Classes LCZ presentes: {', '.join(sorted(processor.gdf['lcz_class'].unique()))}\n")
        f.write(f"Área total analisada: {processor.gdf['area_km2'].sum():.2f} km²\n\n")

        f.write("2. ESTATÍSTICAS DE TEMPERATURA POR CLASSE LCZ\n")
        f.write("-"*80 + "\n")
        for _, row in stats.iterrows():
            f.write(f"\nLCZ {row['lcz_class']}: {row['description']}\n")
            f.write(f"  Temperatura média: {row['mean_temp']:.1f}°C\n")
            f.write(f"  Desvio padrão: {row['std_temp']:.1f}°C\n")
            f.write(f"  Pontos medidos: {int(row['count'])}\n")
            if pd.notna(row['temp_delta_observed']):
                f.write(f"  Diferença vs LCZ D: {row['temp_delta_observed']:+.1f}°C\n")

        f.write("\n\n3. PRINCIPAIS ACHADOS\n")
        f.write("-"*80 + "\n")

        hottest = stats.iloc[0]
        coldest = stats.iloc[-1]

        f.write(f"• Zona mais quente: LCZ {hottest['lcz_class']} ({hottest['description']}) ")
        f.write(f"com {hottest['mean_temp']:.1f}°C\n")
        f.write(f"• Zona mais fria: LCZ {coldest['lcz_class']} ({coldest['description']}) ")
        f.write(f"com {coldest['mean_temp']:.1f}°C\n")
        f.write(f"• Diferença máxima: {hottest['mean_temp'] - coldest['mean_temp']:.1f}°C\n")

        if scenarios:
            f.write("\n\n4. CENÁRIOS SIMULADOS\n")
            f.write("-"*80 + "\n")
            for i, scenario in enumerate(scenarios, 1):
                f.write(f"\nCenário {i}: {scenario['scenario_type'].upper()}\n")
                if scenario['scenario_type'] == 'urbanization':
                    f.write(f"  De: {', '.join(scenario['vegetation_classes'])} → {scenario['target_class']}\n")
                    f.write(f"  Taxa de conversão: {scenario['conversion_rate']*100:.0f}%\n")
                    f.write(f"  Área afetada: {scenario['total_area_converted_km2']:.2f} km²\n")
                    f.write(f"  Impacto térmico: {scenario['expected_temp_increase']:+.1f}°C\n")
                else:
                    f.write(f"  De: {', '.join(scenario['urban_classes'])} → {scenario['target_class']}\n")
                    f.write(f"  Taxa de conversão: {scenario['conversion_rate']*100:.0f}%\n")
                    f.write(f"  Área afetada: {scenario['total_area_converted_km2']:.2f} km²\n")
                    f.write(f"  Impacto térmico: {scenario['expected_temp_decrease']:+.1f}°C\n")

        f.write("\n\n5. RECOMENDAÇÕES\n")
        f.write("-"*80 + "\n")
        f.write("• Priorizar áreas verdes em zonas de alta densidade construída (LCZ 1-3)\n")
        f.write("• Manter e expandir corredores de vegetação (LCZ A, B)\n")
        f.write("• Considerar materiais reflexivos em áreas pavimentadas (LCZ E)\n")
        f.write("• Implementar políticas de sombreamento em zonas comerciais (LCZ 8)\n")
        f.write("• Monitorar continuamente as ilhas de calor urbanas\n")

        f.write("\n\n" + "="*80 + "\n")
        f.write("Relatório gerado automaticamente pelo MVP de Planejamento Urbano\n")
        f.write("="*80 + "\n")


if __name__ == "__main__":
    main()
