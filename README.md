# 🌆 Planejador Urbano com Análise de LCZ e Temperatura

MVP (Minimum Viable Product) para análise de Zonas Climáticas Locais (Local Climate Zones - LCZ) e diferenças de temperatura em ambientes urbanos.

**Cidade de estudo:** Lajeado-RS, Brasil

## 📋 Sobre o Projeto

Este projeto permite:
- ✅ Carregar mapas de LCZ classificados por IA (formato KML/GeoJSON)
- ✅ Consultar dados de temperatura via API Meteomatics
- ✅ Calcular médias de temperatura por classe LCZ
- ✅ Gerar mapas e gráficos comparativos de diferenças térmicas
- ✅ Simular cenários de mudança urbana ("e se...")

### O que são Local Climate Zones (LCZ)?

LCZ é um sistema de classificação padronizado que divide áreas urbanas e rurais em 17 classes baseadas em propriedades que afetam o clima local:
- **Classes Construídas (1-10):** Diferentes densidades e alturas de edificações
- **Classes Naturais (A-G):** Tipos de cobertura do solo (vegetação, água, solo exposto)

## 🚀 Instalação

### 1. Requisitos

- Python 3.8+
- Credenciais da API Meteomatics (opcional - pode usar modo simulado)

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

## 📦 Estrutura do Projeto

```
space-apps/
├── main.py                      # Script principal do MVP
├── lcz_processor.py            # Processamento de dados LCZ
├── meteomatics_api.py          # Cliente da API Meteomatics
├── visualizer.py               # Geração de gráficos e mapas
├── scenario_simulator.py       # Simulação de cenários
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
└── lajeado-result/
    └── data/
        └── *.kml               # Mapa LCZ de Lajeado-RS
```

## 🎯 Como Usar

### Modo 1: Usando a API Meteomatics (Recomendado)

```bash
# Configurar credenciais
export METEOMATICS_USERNAME="seu_usuario"
export METEOMATICS_PASSWORD="sua_senha"

# Executar MVP
python main.py
```

### Modo 2: Modo Simulação (Sem API)

Útil para demonstração e testes sem credenciais:

```bash
python main.py --skip-api
```

### Opções Avançadas

```bash
# Especificar arquivo KML diferente
python main.py --kml caminho/para/seu_arquivo.kml

# Especificar diretório de saída
python main.py --output-dir resultados

# Passar credenciais via linha de comando
python main.py --username seu_usuario --password sua_senha
```

## 📊 Saídas Geradas

O MVP gera os seguintes arquivos no diretório `output/`:

### 1. Dados
- **temperature_data.csv** - Dados brutos de temperatura por ponto
- **lcz_statistics.csv** - Estatísticas agregadas por classe LCZ
- **scenarios_comparison.csv** - Comparação entre cenários simulados

### 2. Visualizações
- **temperature_by_lcz.png** - Gráfico de barras com temperatura média por LCZ
- **temperature_delta.png** - Comparação entre diferença esperada vs observada
- **scenario_example.png** - Visualização de cenário de mudança

### 3. Mapas
- **lcz_map.html** - Mapa interativo com zonas LCZ e temperaturas
  - Abra no navegador para visualização interativa
  - Inclui popups com informações detalhadas
  - Camadas de base alternativas

### 4. Relatórios
- **relatorio.txt** - Relatório final em texto com resumo executivo

## 🔮 Simulação de Cenários

O MVP permite testar cenários como:

### Cenário de Urbanização
"E se esta área verde (LCZ A) virar área construída (LCZ 2)?"
- Calcula impacto térmico esperado
- Estima aquecimento em °C

### Cenário de Revegetação
"E se esta área urbana (LCZ 2) for convertida em parque (LCZ A)?"
- Calcula potencial de resfriamento
- Estima redução de temperatura

### Exemplo de Código

```python
from lcz_processor import LCZProcessor
from scenario_simulator import ScenarioSimulator

# Carregar dados
processor = LCZProcessor('lajeado.kml')
stats = processor.calculate_lcz_statistics(df_temp)

# Criar simulador
simulator = ScenarioSimulator(processor, stats)

# Simular urbanização
scenario = simulator.simulate_urbanization_scenario(
    vegetation_classes=['A', 'B'],
    target_class='2',
    conversion_rate=0.5
)

print(f"Impacto: {scenario['expected_temp_increase']:+.1f}°C")
```

## 📚 Referências Científicas

- **Stewart, I. D., & Oke, T. R. (2012).** Local climate zones for urban temperature studies. *Bulletin of the American Meteorological Society*, 93(12), 1879-1900.

- **Demuzere, M., et al. (2022).** A global map of local climate zones to support earth system modelling and urban-scale environmental science. *Earth System Science Data*, 14(8), 3835-3873.

## 🛠️ Arquitetura Técnica

### Módulos Principais

#### 1. `lcz_processor.py`
- Carrega e processa arquivos KML/GeoJSON
- Associa pontos de temperatura a classes LCZ
- Calcula estatísticas agregadas
- Exporta dados para GeoJSON

#### 2. `meteomatics_api.py`
- Cliente para API Meteomatics
- Suporta queries por ponto, grid e série temporal
- Parâmetros: `t_2m:C` (temperatura a 2m)
- Tratamento de erros e retry

#### 3. `visualizer.py`
- Gráficos com matplotlib/seaborn
- Mapas interativos com folium
- Paleta de cores baseada em Stewart & Oke (2012)
- Visualização de cenários

#### 4. `scenario_simulator.py`
- Simulação de mudanças urbanas
- Cenários pré-definidos e personalizados
- Cálculo de impactos térmicos
- Comparação multi-cenário

## 🔧 API Meteomatics

### Configuração

1. Criar conta em: https://www.meteomatics.com/en/sign-up-weather-api-test-account/
2. Receber credenciais por email
3. Configurar variáveis de ambiente ou passar via CLI

### Parâmetros Disponíveis

- `t_2m:C` - Temperatura a 2m do solo (°C)
- `t_apparent:C` - Temperatura aparente
- `windchill:C` - Sensação térmica

### Exemplo de Requisição

```
GET https://api.meteomatics.com/2025-10-04T12:00:00Z/t_2m:C/-29.4658,-51.9592/json
Authorization: Basic <base64(username:password)>
```

## ⚠️ Limitações Conhecidas

1. **Dados de API**
   - Requer conta Meteomatics (gratuita para teste)
   - Limite de requisições por dia
   - Cobertura pode variar por região

2. **Simulações**
   - Baseadas em valores médios da literatura
   - Não consideram todos os fatores microclimáticos
   - Aproximações lineares simplificadas

3. **Processamento**
   - Arquivos KML devem seguir formato específico
   - Geometrias devem ser polígonos válidos
   - Sistema de coordenadas: WGS84 (EPSG:4326)

## 🔄 Próximos Passos

### Versão 1.1
- [ ] Interface web com Streamlit/Dash
- [ ] Suporte a múltiplas cidades
- [ ] Séries temporais de temperatura
- [ ] Análise sazonal

### Versão 2.0
- [ ] Machine Learning para predição térmica
- [ ] Integração com modelos WRF/ENVI-met
- [ ] API REST para acesso programático
- [ ] Dashboard em tempo real

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto, abra uma issue no repositório.

## 🙏 Agradecimentos

- **Stewart & Oke** - Sistema de classificação LCZ
- **Meteomatics** - API de dados meteorológicos
- **Comunidade de Planejamento Urbano** - Feedback e sugestões

---

**Desenvolvido para análise de ilhas de calor urbanas e planejamento climático** 🌡️🏙️
