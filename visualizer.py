"""
Módulo para visualização de dados LCZ e temperatura
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
import geopandas as gpd
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar estilo dos gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


# Cores para cada classe LCZ (baseado em Stewart & Oke, 2012)
LCZ_COLORS = {
    '1': '#8B0000',   # Compact high-rise - vermelho escuro
    '2': '#CD5C5C',   # Compact midrise - vermelho médio
    '3': '#F08080',   # Compact low-rise - vermelho claro
    '4': '#FF8C00',   # Open high-rise - laranja escuro
    '5': '#FFA500',   # Open midrise - laranja
    '6': '#FFD700',   # Open low-rise - dourado
    '7': '#FFFF00',   # Lightweight low-rise - amarelo
    '8': '#A0522D',   # Large low-rise - marrom
    '9': '#D2B48C',   # Sparsely built - bege
    '10': '#696969',  # Heavy industry - cinza escuro
    'A': '#006400',   # Dense trees - verde escuro
    'B': '#228B22',   # Scattered trees - verde floresta
    'C': '#32CD32',   # Bush, scrub - verde lima
    'D': '#90EE90',   # Low plants - verde claro
    'E': '#808080',   # Bare rock or paved - cinza
    'F': '#D2691E',   # Bare soil or sand - chocolate
    'G': '#1E90FF'    # Water - azul dodger
}


class Visualizer:
    """Classe para criar visualizações de dados LCZ e temperatura"""

    @staticmethod
    def plot_temperature_by_lcz(stats: pd.DataFrame, output_path: str = None):
        """
        Cria gráfico de barras de temperatura média por classe LCZ

        Args:
            stats: DataFrame com estatísticas por LCZ
            output_path: Caminho para salvar figura (opcional)
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Ordenar por temperatura
        stats_sorted = stats.sort_values('mean_temp', ascending=False)

        # Cores das barras
        colors = [LCZ_COLORS.get(lcz, '#CCCCCC') for lcz in stats_sorted['lcz_class']]

        # Criar gráfico de barras
        bars = ax.bar(
            range(len(stats_sorted)),
            stats_sorted['mean_temp'],
            color=colors,
            edgecolor='black',
            linewidth=1
        )

        # Adicionar barras de erro (desvio padrão)
        ax.errorbar(
            range(len(stats_sorted)),
            stats_sorted['mean_temp'],
            yerr=stats_sorted['std_temp'],
            fmt='none',
            ecolor='black',
            capsize=5,
            alpha=0.7
        )

        # Configurar eixos
        ax.set_xticks(range(len(stats_sorted)))
        ax.set_xticklabels(
            [f"{row['lcz_class']}\n{row['description'][:20]}"
             for _, row in stats_sorted.iterrows()],
            rotation=45,
            ha='right'
        )

        ax.set_ylabel('Temperatura Média (°C)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Classe LCZ', fontsize=12, fontweight='bold')
        ax.set_title(
            'Temperatura Média por Classe de Zona Climática Local (LCZ)',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        # Adicionar valores nas barras
        for i, (idx, row) in enumerate(stats_sorted.iterrows()):
            ax.text(
                i,
                row['mean_temp'] + 0.2,
                f"{row['mean_temp']:.1f}°C",
                ha='center',
                va='bottom',
                fontsize=9
            )

        # Adicionar linha de grade
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {output_path}")

        plt.close()

    @staticmethod
    def plot_temperature_delta(stats: pd.DataFrame, output_path: str = None):
        """
        Compara diferença de temperatura observada vs esperada

        Args:
            stats: DataFrame com estatísticas por LCZ
            output_path: Caminho para salvar figura (opcional)
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Filtrar apenas classes com dados
        stats_filtered = stats.dropna(subset=['temp_delta_observed'])

        x = range(len(stats_filtered))
        width = 0.35

        # Barras para delta esperado e observado
        ax.bar(
            [i - width/2 for i in x],
            stats_filtered['temp_delta_expected'],
            width,
            label='Diferença Esperada (Literatura)',
            color='skyblue',
            edgecolor='black'
        )

        ax.bar(
            [i + width/2 for i in x],
            stats_filtered['temp_delta_observed'],
            width,
            label='Diferença Observada (Dados)',
            color='salmon',
            edgecolor='black'
        )

        # Linha zero
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

        # Configurar eixos
        ax.set_xticks(x)
        ax.set_xticklabels(
            [f"{row['lcz_class']}" for _, row in stats_filtered.iterrows()],
            fontsize=10
        )

        ax.set_ylabel('Diferença de Temperatura (°C)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Classe LCZ', fontsize=12, fontweight='bold')
        ax.set_title(
            'Diferença de Temperatura Esperada vs Observada\n(Relativo à LCZ D - Vegetação Baixa)',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        ax.legend(loc='upper right', fontsize=11)
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico salvo em: {output_path}")

        plt.close()

    @staticmethod
    def create_interactive_map(
        gdf: gpd.GeoDataFrame,
        stats: pd.DataFrame = None,
        output_path: str = 'lcz_map.html'
    ):
        """
        Cria mapa interativo com zonas LCZ

        Args:
            gdf: GeoDataFrame com geometrias LCZ
            stats: DataFrame com estatísticas (opcional)
            output_path: Caminho para salvar HTML
        """
        # Centro do mapa (Lajeado-RS)
        center_lat = gdf.geometry.centroid.y.mean()
        center_lon = gdf.geometry.centroid.x.mean()

        # Criar mapa base
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Adicionar camadas de base
        folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)
        folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark').add_to(m)

        # Juntar estatísticas se disponíveis
        if stats is not None:
            gdf = gdf.merge(
                stats[['lcz_class', 'mean_temp', 'count']],
                on='lcz_class',
                how='left'
            )

        # Adicionar polígonos LCZ
        for idx, row in gdf.iterrows():
            # Popup com informações
            popup_html = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <h4 style="margin-bottom: 10px;">LCZ {row['lcz_class']}</h4>
                <p><b>Descrição:</b> {row['lcz_description']}</p>
                <p><b>Área:</b> {row['area_km2']:.3f} km²</p>
            """

            if 'mean_temp' in row and pd.notna(row['mean_temp']):
                popup_html += f"""
                <p><b>Temperatura Média:</b> {row['mean_temp']:.1f}°C</p>
                <p><b>Pontos Medidos:</b> {int(row['count'])}</p>
                """

            popup_html += "</div>"

            # Tooltip
            tooltip = f"LCZ {row['lcz_class']}: {row['lcz_description']}"

            # Estilo do polígono
            style = {
                'fillColor': LCZ_COLORS.get(row['lcz_class'], '#CCCCCC'),
                'color': 'black',
                'weight': 2,
                'fillOpacity': 0.6
            }

            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda x, style=style: style,
                tooltip=tooltip,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

        # Adicionar legenda
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; right: 50px; width: 220px;
                    background-color: white; z-index:9999;
                    border:2px solid grey; border-radius: 5px;
                    padding: 10px; font-family: Arial; font-size: 12px;">
        <p style="margin-top:0; font-weight: bold; text-align: center;">
            Classes LCZ
        </p>
        '''

        for lcz_class in sorted(gdf['lcz_class'].unique()):
            if pd.notna(lcz_class):
                desc = gdf[gdf['lcz_class'] == lcz_class]['lcz_description'].iloc[0]
                color = LCZ_COLORS.get(lcz_class, '#CCCCCC')
                legend_html += f'''
                <p style="margin: 5px 0;">
                    <span style="background-color: {color};
                                 border: 1px solid black;
                                 display: inline-block;
                                 width: 20px; height: 15px;
                                 margin-right: 5px;">
                    </span>
                    <b>{lcz_class}:</b> {desc[:15]}...
                </p>
                '''

        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))

        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)

        # Adicionar plugin de fullscreen
        plugins.Fullscreen().add_to(m)

        # Salvar mapa
        m.save(output_path)
        logger.info(f"Mapa interativo salvo em: {output_path}")

        return m

    @staticmethod
    def plot_scenario_comparison(
        scenario_result: dict,
        output_path: str = None
    ):
        """
        Visualiza resultado de simulação de cenário

        Args:
            scenario_result: Dicionário com resultado de simulação
            output_path: Caminho para salvar figura (opcional)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Gráfico 1: Comparação de temperaturas
        categories = ['Situação Atual', 'Cenário Simulado']
        temps = [scenario_result['from_temp'], scenario_result['to_temp']]
        colors_bar = [
            LCZ_COLORS.get(scenario_result['from_class'], '#CCCCCC'),
            LCZ_COLORS.get(scenario_result['to_class'], '#CCCCCC')
        ]

        bars = ax1.bar(categories, temps, color=colors_bar, edgecolor='black', linewidth=2)

        ax1.set_ylabel('Temperatura Média (°C)', fontsize=12, fontweight='bold')
        ax1.set_title('Comparação de Temperatura', fontsize=14, fontweight='bold')

        # Adicionar valores
        for bar, temp in zip(bars, temps):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.2,
                f'{temp:.1f}°C',
                ha='center',
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )

        # Gráfico 2: Mudança de temperatura
        delta_types = ['Mudança\nObservada', 'Mudança\nEsperada']
        deltas = [
            scenario_result['observed_change'],
            scenario_result['expected_change']
        ]

        colors_delta = ['salmon' if d > 0 else 'skyblue' for d in deltas]

        bars2 = ax2.bar(delta_types, deltas, color=colors_delta, edgecolor='black', linewidth=2)

        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.set_ylabel('Mudança de Temperatura (°C)', fontsize=12, fontweight='bold')
        ax2.set_title('Impacto da Mudança de LCZ', fontsize=14, fontweight='bold')

        # Adicionar valores
        for bar, delta in zip(bars2, deltas):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                delta + (0.2 if delta > 0 else -0.2),
                f'{delta:+.1f}°C',
                ha='center',
                va='bottom' if delta > 0 else 'top',
                fontsize=12,
                fontweight='bold'
            )

        # Adicionar informações do cenário
        scenario_text = f"""
        Cenário: {scenario_result['from_class']} → {scenario_result['to_class']}
        De: {scenario_result['from_description']}
        Para: {scenario_result['to_description']}
        Fração de Área: {scenario_result['area_fraction']*100:.0f}%

        {scenario_result['interpretation']}
        """

        fig.text(
            0.5, 0.02, scenario_text,
            ha='center', va='bottom',
            fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico de cenário salvo em: {output_path}")

        plt.close()


if __name__ == "__main__":
    # Exemplo de uso
    print("Módulo de visualização carregado com sucesso!")
    print("Use as funções:")
    print("- Visualizer.plot_temperature_by_lcz()")
    print("- Visualizer.plot_temperature_delta()")
    print("- Visualizer.create_interactive_map()")
    print("- Visualizer.plot_scenario_comparison()")
