"""
Módulo para processamento de dados de Local Climate Zones (LCZ)
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from fastkml import kml
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Descrições das classes LCZ
LCZ_DESCRIPTIONS = {
    '1': 'Compact high-rise',
    '2': 'Compact midrise',
    '3': 'Compact low-rise',
    '4': 'Open high-rise',
    '5': 'Open midrise',
    '6': 'Open low-rise',
    '7': 'Lightweight low-rise',
    '8': 'Large low-rise',
    '9': 'Sparsely built',
    '10': 'Heavy industry',
    'A': 'Dense trees',
    'B': 'Scattered trees',
    'C': 'Bush, scrub',
    'D': 'Low plants',
    'E': 'Bare rock or paved',
    'F': 'Bare soil or sand',
    'G': 'Water'
}

# Diferença de temperatura esperada em relação à zona rural (LCZ D)
# Valores baseados na literatura científica (Stewart & Oke, 2012)
LCZ_TEMPERATURE_DELTA = {
    '1': 4.5,   # Mais quente - alta densidade construída
    '2': 3.5,
    '3': 2.8,
    '4': 2.5,
    '5': 2.0,
    '6': 1.5,
    '7': 1.2,
    '8': 2.2,
    '9': 0.8,
    '10': 3.0,  # Indústria pesada
    'A': -1.5,  # Mais frio - vegetação densa
    'B': -0.8,
    'C': -0.5,
    'D': 0.0,   # Referência - vegetação baixa
    'E': 2.0,   # Pavimentado
    'F': 1.0,   # Solo exposto
    'G': -2.0   # Água
}


class LCZProcessor:
    """Processador de dados LCZ"""

    def __init__(self, kml_path: str):
        """
        Inicializa processador com arquivo KML

        Args:
            kml_path: Caminho para arquivo KML com zonas LCZ
        """
        self.kml_path = kml_path
        self.gdf = None
        self.load_kml()

    def load_kml(self):
        """Carrega arquivo KML e converte para GeoDataFrame"""
        logger.info(f"Carregando KML: {self.kml_path}")

        try:
            # Habilitar suporte a KML no fiona (se disponível)
            try:
                import fiona
                if hasattr(fiona, 'drvsupport'):
                    fiona.drvsupport.supported_drivers['KML'] = 'rw'
            except:
                pass

            # KML pode ter múltiplas camadas - tentar carregar todas
            import fiona

            # Listar todas as camadas
            layers = fiona.listlayers(self.kml_path)
            logger.info(f"Camadas encontradas no KML: {layers}")

            # Carregar todas as camadas e combinar
            gdfs = []
            for layer in layers:
                if layer != '[CityName][Date][ExpertName]':  # Ignorar camada raiz
                    try:
                        gdf_layer = gpd.read_file(self.kml_path, layer=layer)
                        gdf_layer['layer_name'] = layer
                        gdfs.append(gdf_layer)
                        logger.info(f"Camada '{layer}': {len(gdf_layer)} features")
                    except Exception as e:
                        logger.warning(f"Erro ao carregar camada '{layer}': {e}")

            # Combinar todas as camadas
            if gdfs:
                gdf = pd.concat(gdfs, ignore_index=True)
            else:
                # Fallback: carregar camada padrão
                gdf = gpd.read_file(self.kml_path, driver='KML')

            # Extrair classe LCZ do nome da camada ou do campo Name
            if 'layer_name' in gdf.columns:
                gdf['lcz_class'] = gdf['layer_name']
            else:
                gdf['lcz_class'] = gdf['Name'].str.extract(r'^([0-9A-G]+)$')[0]

            # Adicionar descrição
            gdf['lcz_description'] = gdf['lcz_class'].map(LCZ_DESCRIPTIONS)

            # Adicionar delta de temperatura esperado
            gdf['temp_delta_expected'] = gdf['lcz_class'].map(LCZ_TEMPERATURE_DELTA)

            # Calcular centroide de cada polígono
            gdf['centroid'] = gdf.geometry.centroid
            gdf['centroid_lat'] = gdf.centroid.y
            gdf['centroid_lon'] = gdf.centroid.x

            # Calcular área em km²
            gdf_metric = gdf.to_crs(epsg=3857)  # Web Mercator para área em metros
            gdf['area_km2'] = gdf_metric.geometry.area / 1_000_000

            self.gdf = gdf

            logger.info(f"Carregadas {len(gdf)} zonas LCZ")
            logger.info(f"Classes LCZ encontradas: {sorted(gdf['lcz_class'].unique())}")

        except Exception as e:
            logger.error(f"Erro ao carregar KML: {e}")
            raise

    def get_lcz_at_point(self, lat: float, lon: float) -> str:
        """
        Identifica classe LCZ em ponto específico

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Classe LCZ ou None se ponto não estiver em nenhuma zona
        """
        point = Point(lon, lat)

        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return row['lcz_class']

        return None

    def assign_lcz_to_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Associa classe LCZ a pontos em DataFrame

        Args:
            df: DataFrame com colunas 'lat' e 'lon'

        Returns:
            DataFrame com coluna adicional 'lcz_class'
        """
        logger.info(f"Associando LCZ a {len(df)} pontos...")

        df = df.copy()

        # Criar GeoDataFrame dos pontos
        gdf_points = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.lon, df.lat),
            crs='EPSG:4326'
        )

        # Spatial join para associar pontos a zonas
        joined = gpd.sjoin(
            gdf_points,
            self.gdf[['lcz_class', 'geometry']],
            how='left',
            predicate='within'
        )

        # Debug: verificar colunas disponíveis
        logger.debug(f"Colunas no joined: {joined.columns.tolist()}")

        # Verificar qual coluna tem os dados LCZ
        if 'lcz_class' in joined.columns:
            df['lcz_class'] = joined['lcz_class'].values
        elif 'lcz_class_right' in joined.columns:
            df['lcz_class'] = joined['lcz_class_right'].values
        elif 'lcz_class_left' in joined.columns:
            df['lcz_class'] = joined['lcz_class_left'].values
        else:
            # Fallback: tentar de outra forma
            df['lcz_class'] = None
            for idx, row in df.iterrows():
                point_geom = gdf_points.loc[idx, 'geometry']
                for _, zone in self.gdf.iterrows():
                    if zone.geometry.contains(point_geom):
                        df.loc[idx, 'lcz_class'] = zone['lcz_class']
                        break

        logger.info(f"Pontos associados: {df['lcz_class'].notna().sum()}/{len(df)}")

        return df

    def calculate_lcz_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula estatísticas de temperatura por classe LCZ

        Args:
            df: DataFrame com colunas 'lcz_class' e 'temperature'

        Returns:
            DataFrame com estatísticas por classe LCZ
        """
        stats = df.groupby('lcz_class')['temperature'].agg([
            ('mean_temp', 'mean'),
            ('std_temp', 'std'),
            ('min_temp', 'min'),
            ('max_temp', 'max'),
            ('count', 'count')
        ]).reset_index()

        # Adicionar informações sobre cada classe
        stats['description'] = stats['lcz_class'].map(LCZ_DESCRIPTIONS)
        stats['temp_delta_expected'] = stats['lcz_class'].map(LCZ_TEMPERATURE_DELTA)

        # Calcular diferença real em relação à LCZ D (referência)
        lcz_d_temp = stats[stats['lcz_class'] == 'D']['mean_temp'].values
        if len(lcz_d_temp) > 0:
            stats['temp_delta_observed'] = stats['mean_temp'] - lcz_d_temp[0]
        else:
            stats['temp_delta_observed'] = np.nan

        stats = stats.sort_values('mean_temp', ascending=False)

        return stats

    def get_sampling_points(self, points_per_zone: int = 5) -> List[Tuple[float, float]]:
        """
        Gera pontos de amostragem distribuídos nas zonas LCZ

        Args:
            points_per_zone: Número de pontos por zona

        Returns:
            Lista de tuplas (lat, lon)
        """
        points = []

        for idx, row in self.gdf.iterrows():
            # Usar centroide e pontos próximos
            centroid = row.centroid

            points.append((centroid.y, centroid.x))

            # Gerar pontos adicionais dentro do polígono
            minx, miny, maxx, maxy = row.geometry.bounds

            for _ in range(points_per_zone - 1):
                # Gerar ponto aleatório no bounding box
                for attempt in range(10):  # Tentar até 10 vezes
                    random_lon = np.random.uniform(minx, maxx)
                    random_lat = np.random.uniform(miny, maxy)
                    random_point = Point(random_lon, random_lat)

                    if row.geometry.contains(random_point):
                        points.append((random_lat, random_lon))
                        break

        logger.info(f"Gerados {len(points)} pontos de amostragem")
        return points

    def simulate_lcz_change(
        self,
        stats: pd.DataFrame,
        from_class: str,
        to_class: str,
        area_fraction: float = 1.0
    ) -> Dict:
        """
        Simula mudança de classe LCZ e impacto na temperatura

        Args:
            stats: DataFrame com estatísticas por classe
            from_class: Classe LCZ original
            to_class: Classe LCZ final
            area_fraction: Fração da área que será convertida (0-1)

        Returns:
            Dicionário com resultados da simulação
        """
        from_row = stats[stats['lcz_class'] == from_class]
        to_row = stats[stats['lcz_class'] == to_class]

        if from_row.empty or to_row.empty:
            raise ValueError(f"Classe LCZ não encontrada: {from_class} ou {to_class}")

        from_temp = from_row['mean_temp'].values[0]
        to_temp = to_row['mean_temp'].values[0]

        # Temperatura esperada baseada em valores da literatura
        from_delta = LCZ_TEMPERATURE_DELTA.get(from_class, 0)
        to_delta = LCZ_TEMPERATURE_DELTA.get(to_class, 0)
        expected_change = to_delta - from_delta

        # Mudança observada nos dados
        observed_change = (to_temp - from_temp) * area_fraction

        result = {
            'from_class': from_class,
            'from_description': LCZ_DESCRIPTIONS.get(from_class),
            'to_class': to_class,
            'to_description': LCZ_DESCRIPTIONS.get(to_class),
            'area_fraction': area_fraction,
            'from_temp': from_temp,
            'to_temp': to_temp,
            'observed_change': observed_change,
            'expected_change': expected_change,
            'interpretation': self._interpret_change(observed_change)
        }

        return result

    @staticmethod
    def _interpret_change(delta: float) -> str:
        """Interpreta mudança de temperatura"""
        if delta > 2:
            return "Aquecimento significativo esperado"
        elif delta > 0.5:
            return "Aquecimento moderado esperado"
        elif delta > -0.5:
            return "Impacto térmico mínimo"
        elif delta > -2:
            return "Resfriamento moderado esperado"
        else:
            return "Resfriamento significativo esperado"

    def export_to_geojson(self, output_path: str, include_stats: bool = True):
        """
        Exporta dados LCZ para GeoJSON

        Args:
            output_path: Caminho do arquivo de saída
            include_stats: Se True, inclui estatísticas calculadas
        """
        gdf_export = self.gdf.copy()

        if include_stats:
            # Incluir colunas relevantes
            columns = [
                'lcz_class', 'lcz_description', 'temp_delta_expected',
                'area_km2', 'centroid_lat', 'centroid_lon', 'geometry'
            ]
        else:
            columns = ['lcz_class', 'lcz_description', 'geometry']

        gdf_export[columns].to_file(output_path, driver='GeoJSON')
        logger.info(f"Dados exportados para: {output_path}")


if __name__ == "__main__":
    # Teste com arquivo KML de Lajeado
    kml_path = "lajeado-result/data/21025c4c602c6ebc89232bf384a56fac185220af.kml"

    processor = LCZProcessor(kml_path)

    print("\n=== Zonas LCZ Carregadas ===")
    print(processor.gdf[['lcz_class', 'lcz_description', 'area_km2']].to_string(index=False))

    print("\n=== Pontos de Amostragem ===")
    points = processor.get_sampling_points(points_per_zone=3)
    print(f"Total de pontos: {len(points)}")

    print("\n=== Teste de Classificação de Ponto ===")
    test_lat, test_lon = -29.4658, -51.9592
    lcz = processor.get_lcz_at_point(test_lat, test_lon)
    print(f"LCZ em ({test_lat}, {test_lon}): {lcz}")
