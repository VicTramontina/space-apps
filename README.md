# Análise de Temperatura por Local Climate Zones (LCZ) - Lajeado, RS

Sistema de visualização e simulação de temperaturas baseado em Local Climate Zones (LCZ) para a cidade de Lajeado, Rio Grande do Sul.

## 📋 Visão Geral

Este projeto permite:
- **Visualizar zonas climáticas locais (LCZ)** mapeadas para Lajeado-RS
- **Obter dados de temperatura em tempo real** via API Meteomatics
- **Simular cenários** de mudança de uso do solo e seus impactos térmicos
- **Calcular diferenças de temperatura** ao converter uma LCZ para outra

## 🌡️ O que são Local Climate Zones (LCZ)?

Local Climate Zones são uma classificação padronizada de áreas urbanas e rurais com base em suas propriedades térmicas, desenvolvida por Stewart & Oke (2012). O sistema define 17 tipos de zonas:

### Zonas Urbanas (LCZ 1-10)
- **LCZ 1-3**: Compact High/Mid/Low-Rise (edifícios compactos)
- **LCZ 4-6**: Open High/Mid/Low-Rise (edifícios espaçados)
- **LCZ 7**: Lightweight Low-Rise (construções leves)
- **LCZ 8**: Large Low-Rise (grandes edifícios baixos)
- **LCZ 9**: Sparsely Built (construções esparsas)
- **LCZ 10**: Heavy Industry (indústria pesada)

### Zonas Naturais (LCZ 11-17)
- **LCZ 11-13**: Árvores densas/esparsas, arbustos
- **LCZ 14**: Low Plants (vegetação baixa) - **baseline de temperatura**
- **LCZ 15**: Bare Rock or Paved (rocha exposta ou pavimentado)
- **LCZ 16**: Bare Soil or Sand (solo exposto ou areia)
- **LCZ 17**: Water (corpos d'água)

## 🔬 Metodologia de Cálculo de Temperatura

### Baseline e Offsets Térmicos

A metodologia de cálculo é baseada no framework LCZ (Stewart & Oke, 2012) e em revisões sistemáticas sobre Urban Heat Island (UHI):

**LCZ 14 (Low Plants)** é utilizada como baseline (offset = 0°C)

Cada LCZ possui um **offset térmico** característico:

| LCZ | Tipo | Offset Térmico | Base Científica |
|-----|------|----------------|-----------------|
| 1 | Compact High-Rise | +2.5°C | Estudos mostram valores entre +2.0 e +3.0°C |
| 2 | Compact Mid-Rise | +2.8°C | Identificada como a LCZ mais quente em múltiplos estudos |
| 3 | Compact Low-Rise | +2.3°C | Valores típicos de +2.0 a +2.5°C |
| 4 | Open High-Rise | +1.8°C | Menor densidade = menor aquecimento |
| 5 | Open Mid-Rise | +2.0°C | Contribuidor significativo para UHI |
| 6 | Open Low-Rise | +1.5°C | Aquecimento moderado |
| 7 | Lightweight Low-Rise | +1.2°C | Materiais leves = menor retenção de calor |
| 8 | Large Low-Rise | +2.2°C | Grande massa construída |
| 9 | Sparsely Built | +0.5°C | Mínimo aquecimento urbano |
| 10 | Heavy Industry | +2.6°C | Alto calor antropogênico |
| 11 | Dense Trees | -1.5°C | Forte efeito de resfriamento por evapotranspiração |
| 12 | Scattered Trees | -0.8°C | Resfriamento moderado |
| 13 | Bush/Scrub | -0.3°C | Leve resfriamento |
| 14 | Low Plants | 0.0°C | **BASELINE** |
| 15 | Bare Rock/Paved | +2.0°C | Alta absorção térmica |
| 16 | Bare Soil/Sand | +1.0°C | Aquecimento moderado |
| 17 | Water | -2.0°C | Forte resfriamento por alta capacidade térmica |

### Fórmula de Cálculo

Quando uma área é convertida de LCZ A para LCZ B:

```
ΔT = Offset_LCZ_B - Offset_LCZ_A
T_nova = T_atual + ΔT
```

**Exemplo:**
- Área atual: LCZ 3 (Compact Low-Rise), Temperatura = 28°C
- Conversão para: LCZ 11 (Dense Trees)
- ΔT = (-1.5°C) - (+2.3°C) = -3.8°C
- T_nova = 28°C - 3.8°C = **24.2°C**

## 🌐 API Meteomatics

### Autenticação
O sistema utiliza a API da Meteomatics para obter dados de temperatura em tempo real.

**Endpoint:** `https://api.meteomatics.com`

**Parâmetros utilizados:**
- `t_2m:C` - Temperatura a 2 metros (proxy para temperatura de superfície urbana)
- Formato: `{datetime}/{parameter}/{location}/json`

### Configuração

1. Obtenha credenciais em: https://www.meteomatics.com/
2. Configure o arquivo `.env`:

```env
METEOMATICS_USERNAME=seu_usuario
METEOMATICS_PASSWORD=sua_senha
```

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas credenciais da Meteomatics
# METEOMATICS_USERNAME=seu_usuario
# METEOMATICS_PASSWORD=sua_senha
```

### Executar

```bash
python app.py
```

Acesse: http://localhost:5000

## 🎯 Como Usar a Interface

1. **Visualizar LCZs**: O mapa carrega automaticamente as zonas de Lajeado
2. **Ver Temperatura**: Clique em "Carregar Camada de Temperatura" para ver dados térmicos
3. **Selecionar Zona**: Clique em qualquer zona LCZ no mapa
4. **Simular Mudança**:
   - Selecione uma nova LCZ no dropdown
   - Clique em "Calcular Cenário"
   - Veja o impacto térmico calculado
5. **Legenda**: Use o botão "Mostrar/Ocultar Legenda" para ver todas as LCZs

## 📊 Estrutura do Projeto

```
space-apps/
├── app.py                      # Aplicação Flask principal
├── config.py                   # Configurações e constantes LCZ
├── lcz_processor.py            # Processamento de arquivos KMZ
├── meteomatics_api.py          # Integração com API Meteomatics
├── temperature_calculator.py   # Cálculos de diferenças térmicas
├── requirements.txt            # Dependências Python
├── .env.example               # Exemplo de configuração
├── templates/
│   └── index.html             # Interface web
├── static/
│   └── app.js                 # JavaScript da aplicação
├── lajeado-result/            # Dados de LCZ de Lajeado
│   └── *.kmz                  # Arquivo KMZ com geometrias
└── output/                    # Saídas geradas
```

## 📚 Referências Científicas

### Framework LCZ
1. **Stewart, I. D., & Oke, T. R. (2012).** Local Climate Zones for Urban Temperature Studies. *Bulletin of the American Meteorological Society*, 93(12), 1879-1900.
   - DOI: 10.1175/BAMS-D-11-00019.1
   - Define o framework LCZ e metodologia de cálculo ΔT_LCZ X-LCZ D

### Revisões Sistemáticas
2. **Yang, J., et al. (2024).** Urban heat dynamics in Local Climate Zones (LCZs): A systematic review. *Building and Environment*.
   - Identificou LCZ 2 (Compact Mid-Rise) como a mais quente
   - Diferenças de até 2.62°C entre LCZs em Pequim

3. **Mushore, T. D., et al. (2022).** Local Climate Zones to Identify Surface Urban Heat Islands: A Systematic Review. *Remote Sensing*, 15(4), 884.
   - Confirma metodologia baseada em LCZ
   - Valida uso de LCZ 14 como baseline

### Estudos de Caso
4. **Li, Y., et al. (2024).** Impact of Local Climate Zones on the Urban Heat and Dry Islands in Beijing. *Journal of Meteorological Research*.
   - Quantifica diferenças térmicas entre LCZs
   - Heterogeneidade espacial da UHI

5. **Fukuda, S., et al. (2023).** Comparative Analysis of SUHI Based on LCZ for Hiroshima and Sapporo. *Climate*, 11(7), 142.
   - LCZ 10 e LCZ E com temperaturas > 40°C
   - Padrões dia/noite em diferentes LCZs

### WUDAPT (World Urban Database and Access Portal Tools)
6. **Demuzere, M., et al. (2019).** WUDAPT Level 0 Training Data.
   - Framework global para mapeamento LCZ
   - Fonte: https://www.wudapt.org/

## 🔧 API Endpoints

### `GET /api/lcz-data`
Retorna dados GeoJSON das zonas LCZ

### `GET /api/temperature?lat={lat}&lon={lon}`
Obtém temperatura para um ponto específico

### `GET /api/temperature-grid`
Obtém grade de temperatura para toda a área

### `POST /api/calculate-scenario`
Calcula impacto de mudança de LCZ
```json
{
  "zone_id": "zone_1",
  "from_lcz": 3,
  "to_lcz": 11,
  "base_temperature": 28.5
}
```

### `GET /api/lcz-classes`
Retorna definições de todas as classes LCZ

## 📝 Notas sobre Precisão

- **Offsets térmicos** são valores típicos baseados em literatura científica
- Variações locais podem ocorrer devido a:
  - Condições meteorológicas específicas
  - Topografia local
  - Proximidade a corpos d'água
  - Densidade de vegetação real vs. classificada
- Recomenda-se validação com medições locais quando disponíveis

## 🤝 Contribuindo

Melhorias são bem-vindas! Áreas de interesse:
- Calibração de offsets térmicos com dados locais
- Integração com outras fontes de temperatura
- Análise temporal (séries históricas)
- Validação com estações meteorológicas

## 📄 Licença

Este projeto foi desenvolvido para análise científica e educacional.

## 👥 Autores

Desenvolvido para análise de Urban Heat Island em Lajeado, RS.

---

**Nota**: Este sistema requer credenciais válidas da API Meteomatics para funcionar completamente. Uma conta de teste gratuita pode ser obtida em https://www.meteomatics.com/
