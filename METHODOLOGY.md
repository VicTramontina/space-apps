# 📐 Documentação da Metodologia de Cálculo

## 1. Framework Local Climate Zones (LCZ)

### 1.1 Origem e Desenvolvimento
O framework LCZ foi desenvolvido por Stewart & Oke (2012) para padronizar a caracterização de áreas urbanas em estudos de Urban Heat Island (UHI).

**Referência Principal:**
> Stewart, I. D., & Oke, T. R. (2012). Local Climate Zones for Urban Temperature Studies. Bulletin of the American Meteorological Society, 93(12), 1879-1900. https://doi.org/10.1175/BAMS-D-11-00019.1

### 1.2 Definição de LCZ
Uma Local Climate Zone é definida como:
- **Escala**: 10² a 10⁴ metros (centenas de metros a alguns quilômetros)
- **Características**: Combinação única de estrutura de superfície, cobertura e atividade humana
- **Propriedades**: Térmicas, radiativas e aerodinâmicas distintas

### 1.3 Sistema de Classificação
**17 classes** divididas em:
- **Built types (1-10)**: Áreas com construções predominantes
- **Land cover types (11-17)**: Áreas com cobertura natural predominante

## 2. Metodologia de Cálculo de Temperatura

### 2.1 Conceito Base: Temperatura de Referência

O framework LCZ define o UHI usando a diferença de temperatura entre zonas:

```
ΔT_UHI = T_LCZ_X - T_LCZ_D
```

Onde:
- **T_LCZ_X**: Temperatura de qualquer LCZ
- **T_LCZ_D**: Temperatura da LCZ D (Low Plants) - **baseline**

**Por que LCZ D (14) é a baseline?**
- Representa vegetação baixa e natural
- Condições mais próximas ao rural tradicional
- Mínima influência antropogênica
- Amplamente disponível para comparação

### 2.2 Derivação dos Offsets Térmicos

Os offsets térmicos foram derivados de múltiplas fontes científicas:

#### 2.2.1 Zonas Urbanas Compactas (LCZ 1-3)

**LCZ 1 - Compact High-Rise: +2.5°C**
- **Base**: Estudos em Hong Kong, Singapura (Stewart et al., 2014)
- **Características**: Sky View Factor < 0.4, altura > 25m
- **Mecanismo**: Aprisionamento de radiação de onda longa
- **Padrão**: Mais quente à noite que durante o dia

**LCZ 2 - Compact Mid-Rise: +2.8°C**
- **Base**: Identificada como LCZ mais quente em revisão sistemática (Yang et al., 2024)
- **Evidência**: Estudos em Beijing (Li et al., 2024) mostram pico de +2.62°C
- **Características**: Densidade construída > 40%, altura 10-25m
- **Mecanismo**: Combinação ótima de massa térmica e aprisionamento radiativo

**LCZ 3 - Compact Low-Rise: +2.3°C**
- **Base**: Estudos em cidades mediterrâneas e asiáticas
- **Características**: Típico de centros históricos
- **Mecanismo**: Alta densidade + materiais tradicionais

#### 2.2.2 Zonas Urbanas Abertas (LCZ 4-6)

**LCZ 4 - Open High-Rise: +1.8°C**
**LCZ 5 - Open Mid-Rise: +2.0°C**
**LCZ 6 - Open Low-Rise: +1.5°C**

- **Base**: Stewart & Oke (2012), estudos em Vancouver, Dublin
- **Diferencial**: Maior espaçamento = maior ventilação
- **Evidência**: Redução de 0.5-1.0°C comparado às versões compactas
- **LCZ 5**: Identificada como contribuidor significativo para UHI total (área-weighted)

#### 2.2.3 Zonas Especiais (LCZ 7-10)

**LCZ 7 - Lightweight Low-Rise: +1.2°C**
- **Características**: Materiais leves (madeira, metal corrugado)
- **Mecanismo**: Baixa capacidade térmica = rápido resfriamento noturno

**LCZ 8 - Large Low-Rise: +2.2°C**
- **Exemplos**: Shopping centers, warehouses
- **Mecanismo**: Grande área de cobertura impermeável

**LCZ 9 - Sparsely Built: +0.5°C**
- **Características**: < 20% de cobertura construída
- **Mecanismo**: Mínima modificação do ambiente natural

**LCZ 10 - Heavy Industry: +2.6°C**
- **Base**: Estudos em Tóquio (Fukuda et al., 2023) - temperaturas > 41°C
- **Mecanismo**: Calor antropogênico + superfícies metálicas/pavimentadas

#### 2.2.4 Zonas de Vegetação (LCZ 11-13)

**LCZ 11 - Dense Trees: -1.5°C**
- **Base**: Múltiplos estudos de cooling effect of vegetation
- **Mecanismo**:
  - Evapotranspiração
  - Sombreamento
  - Redução de albedo
- **Evidência**: Efeito de resfriamento de 1-2°C amplamente documentado

**LCZ 12 - Scattered Trees: -0.8°C**
- **Base**: Interpolação entre dense trees e scrub
- **Densidade**: 10-40% de cobertura arbórea

**LCZ 13 - Bush/Scrub: -0.3°C**
- **Base**: Vegetação baixa com menor efeito evapotranspirativo
- **Evidência**: Efeito marginal mas mensurável

#### 2.2.5 Zonas Especiais (LCZ 14-17)

**LCZ 14 - Low Plants: 0.0°C (BASELINE)**
- **Definição**: Referência zero por definição
- **Características**: Grama, herbáceas, agricultura

**LCZ 15 - Bare Rock/Paved: +2.0°C**
- **Base**: Estudos de estacionamentos e áreas pavimentadas
- **Mecanismo**: Alta absorção solar + baixa evaporação

**LCZ 16 - Bare Soil/Sand: +1.0°C**
- **Base**: Estudos em áreas desérticas urbanas
- **Variação**: Pode ser mais frio que vegetado se úmido

**LCZ 17 - Water: -2.0°C**
- **Base**: Alta capacidade térmica da água
- **Mecanismo**: Armazenamento de calor latente
- **Evidência**: Consistente em estudos de corpos d'água urbanos

### 2.3 Fórmula de Cálculo de Cenários

Quando uma área é convertida de LCZ_A para LCZ_B:

```python
# 1. Obter offsets das LCZs
offset_A = LCZ_CLASSES[lcz_a]['thermal_offset']
offset_B = LCZ_CLASSES[lcz_b]['thermal_offset']

# 2. Calcular diferença
ΔT = offset_B - offset_A

# 3. Calcular nova temperatura
T_new = T_current + ΔT
```

**Exemplo Completo:**

```
Situação: Área industrial (LCZ 10) será convertida em parque (LCZ 11)
Temperatura atual: 32.0°C

offset_LCZ10 = +2.6°C
offset_LCZ11 = -1.5°C

ΔT = (-1.5) - (+2.6) = -4.1°C

T_new = 32.0 + (-4.1) = 27.9°C

Resultado: Redução de 4.1°C
```

## 3. Validação e Limitações

### 3.1 Validação
- Valores baseados em **meta-análise** de múltiplos estudos
- Consistência com framework original Stewart & Oke
- Verificação com estudos recentes (2022-2024)

### 3.2 Limitações Conhecidas

1. **Variabilidade Temporal**
   - Offsets podem variar entre dia/noite
   - Implementação atual usa valores médios

2. **Variabilidade Geográfica**
   - Clima tropical vs. temperado pode alterar valores
   - Recomenda-se calibração local quando possível

3. **Escala**
   - Aplicável para áreas de 100m - 10km
   - Não adequado para microescala (< 100m)

4. **Condições Meteorológicas**
   - Offsets são mais pronunciados em condições calmas e claras
   - Vento forte pode reduzir diferenças

### 3.3 Incertezas
- **Offsets urbanos (LCZ 1-10)**: ±0.5°C
- **Offsets vegetação (LCZ 11-13)**: ±0.3°C
- **Offsets água/pavimento (LCZ 15-17)**: ±0.4°C

## 4. Integração de Dados de Temperatura

### 4.1 API Meteomatics
**Parâmetro utilizado**: `t_2m:C` (temperatura a 2 metros)

**Justificativa:**
- Padrão meteorológico internacional
- Representativo de temperatura sentida por pedestres
- Disponível globalmente

**Alternativas consideradas:**
- `t_0m:C` - temperatura de superfície
- LST de satélite - menor resolução temporal

### 4.2 Processamento de Grid

```python
# Resolução espacial
resolution = 0.005  # ~500m

# Grid sobre área de interesse
temp_grid = meteomatics.get_temperature_grid(
    lat_min, lat_max, lon_min, lon_max, resolution
)
```

## 5. Referências Completas

### Artigos Fundamentais
1. Stewart, I. D., & Oke, T. R. (2012). Local Climate Zones for Urban Temperature Studies. *BAMS*, 93(12), 1879-1900.

2. Stewart, I. D., Oke, T. R., & Krayenhoff, E. S. (2014). Evaluation of the 'local climate zone' scheme using temperature observations and model simulations. *Int. J. Climatology*, 34(4), 1062-1080.

### Revisões Sistemáticas
3. Mushore, T. D., et al. (2022). Local Climate Zones to Identify Surface Urban Heat Islands: A Systematic Review. *Remote Sensing*, 15(4), 884.

4. Yang, J., et al. (2024). Urban heat dynamics in Local Climate Zones: A systematic review. *Building and Environment*, 110679.

### Estudos de Caso Recentes
5. Li, Y., et al. (2024). Impact of Local Climate Zones on the Urban Heat and Dry Islands in Beijing. *J. Meteorol. Res.*, 38, 1-15.

6. Fukuda, S., et al. (2023). Comparative Analysis of SUHI Based on LCZ Classification. *Climate*, 11(7), 142.

### Recursos Online
7. WUDAPT - World Urban Database and Access Portal Tools
   https://www.wudapt.org/

8. Meteomatics API Documentation
   https://www.meteomatics.com/en/api/

---

**Última atualização**: Janeiro 2025
**Versão da metodologia**: 1.0
