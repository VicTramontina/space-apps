"""
Módulo para coleta de dados de temperatura da API Meteomatics
"""
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeteomaticsAPI:
    """Cliente para API Meteomatics"""

    BASE_URL = "https://api.meteomatics.com"

    def __init__(self, username: str, password: str):
        """
        Inicializa cliente da API

        Args:
            username: Nome de usuário da API Meteomatics
            password: Senha da API Meteomatics
        """
        self.username = username
        self.password = password
        self.auth = (username, password)

    def get_temperature_grid(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        resolution: float = 0.005,
        start_time: datetime = None,
        end_time: datetime = None,
        time_step: str = "1H"
    ) -> pd.DataFrame:
        """
        Obtém dados de temperatura em grid para área especificada

        Args:
            lat_min: Latitude mínima
            lat_max: Latitude máxima
            lon_min: Longitude mínima
            lon_max: Longitude máxima
            resolution: Resolução do grid em graus (default: 0.005 = ~500m)
            start_time: Tempo inicial (default: 24h atrás)
            end_time: Tempo final (default: agora)
            time_step: Intervalo de tempo (default: 1H)

        Returns:
            DataFrame com colunas: lat, lon, timestamp, temperature
        """
        if start_time is None:
            now = datetime.now(timezone.utc)
            start_time = now - timedelta(hours=24)
        if end_time is None:
            end_time = datetime.now(timezone.utc)

        # Formato de data ISO para API
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Parâmetro de temperatura a 2m em Celsius
        parameter = "t_2m:C"

        # Construir URL para grid
        # Formato: lat_min,lon_min_lat_max,lon_max:resolution
        location = f"{lat_min},{lon_min}_{lat_max},{lon_max}:{resolution}"

        # Formato de tempo com intervalo
        time_range = f"{start_str}--{end_str}:PT{time_step}"

        url = f"{self.BASE_URL}/{time_range}/{parameter}/{location}/json"

        logger.info(f"Consultando API Meteomatics: {url}")

        try:
            response = requests.get(url, auth=self.auth, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Processar resposta em DataFrame
            records = []
            for entry in data.get('data', []):
                for coord in entry.get('coordinates', []):
                    for value in coord.get('dates', []):
                        records.append({
                            'lat': coord['lat'],
                            'lon': coord['lon'],
                            'timestamp': value['date'],
                            'temperature': value['value']
                        })

            df = pd.DataFrame(records)
            logger.info(f"Coletados {len(df)} registros de temperatura")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar API: {e}")
            raise

    def get_temperature_points(
        self,
        points: List[Tuple[float, float]],
        timestamp: datetime = None
    ) -> pd.DataFrame:
        """
        Obtém temperatura para lista de pontos específicos

        Args:
            points: Lista de tuplas (lat, lon)
            timestamp: Data/hora para consulta (default: agora)

        Returns:
            DataFrame com colunas: lat, lon, temperature
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        time_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        parameter = "t_2m:C"

        results = []

        # API Meteomatics permite múltiplos pontos separados por +
        # Mas para simplificar, vamos fazer requisições individuais
        for lat, lon in points:
            location = f"{lat},{lon}"
            url = f"{self.BASE_URL}/{time_str}/{parameter}/{location}/json"

            try:
                response = requests.get(url, auth=self.auth, timeout=30)
                response.raise_for_status()

                data = response.json()
                temp = data['data'][0]['coordinates'][0]['dates'][0]['value']

                results.append({
                    'lat': lat,
                    'lon': lon,
                    'temperature': temp
                })

            except requests.exceptions.RequestException as e:
                logger.warning(f"Erro ao obter temperatura para ({lat}, {lon}): {e}")
                results.append({
                    'lat': lat,
                    'lon': lon,
                    'temperature': None
                })

        return pd.DataFrame(results)

    def get_temperature_timeseries(
        self,
        lat: float,
        lon: float,
        start_time: datetime = None,
        end_time: datetime = None,
        time_step: str = "1H"
    ) -> pd.DataFrame:
        """
        Obtém série temporal de temperatura para um ponto

        Args:
            lat: Latitude
            lon: Longitude
            start_time: Tempo inicial (default: 7 dias atrás)
            end_time: Tempo final (default: agora)
            time_step: Intervalo de tempo (default: 1H)

        Returns:
            DataFrame com colunas: timestamp, temperature
        """
        if start_time is None:
            now = datetime.now(timezone.utc)
            start_time = now - timedelta(days=7)
        if end_time is None:
            end_time = datetime.now(timezone.utc)

        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        parameter = "t_2m:C"
        location = f"{lat},{lon}"
        time_range = f"{start_str}--{end_str}:PT{time_step}"

        url = f"{self.BASE_URL}/{time_range}/{parameter}/{location}/json"

        logger.info(f"Consultando série temporal: {url}")

        try:
            response = requests.get(url, auth=self.auth, timeout=30)
            response.raise_for_status()

            data = response.json()

            records = []
            for value in data['data'][0]['coordinates'][0]['dates']:
                records.append({
                    'timestamp': value['date'],
                    'temperature': value['value']
                })

            df = pd.DataFrame(records)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            logger.info(f"Coletados {len(df)} pontos na série temporal")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar API: {e}")
            raise


if __name__ == "__main__":
    # Exemplo de uso (requer credenciais válidas)
    import os

    username = os.getenv("METEOMATICS_USERNAME", "your_username")
    password = os.getenv("METEOMATICS_PASSWORD", "your_password")

    api = MeteomaticsAPI(username, password)

    # Coordenadas de Lajeado-RS
    lajeado_lat = -29.4658
    lajeado_lon = -51.9592

    # Bounding box para Lajeado (aproximado)
    lat_min, lat_max = -29.48, -29.42
    lon_min, lon_max = -52.03, -51.92

    print("Testando API Meteomatics...")
    print(f"Para usar, configure as variáveis de ambiente:")
    print(f"  METEOMATICS_USERNAME=seu_usuario")
    print(f"  METEOMATICS_PASSWORD=sua_senha")
