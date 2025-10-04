# 🎨 Guia Visual - Entendendo o MVP

## 📊 Fluxo de Dados

```
┌─────────────────┐
│  Mapa LCZ (KML) │
│   Lajeado-RS    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐      ┌──────────────────────┐
│   lcz_processor.py      │      │  meteomatics_api.py  │
│                         │      │                      │
│ • Carrega geometrias    │      │ • Consulta API       │
│ • Extrai classes LCZ    │      │ • Coleta temperatura │
│ • Calcula centroides    │      │ • Ou gera sintéticos │
└────────┬────────────────┘      └──────────┬───────────┘
         │                                   │
         └───────────────┬───────────────────┘
                         ↓
              ┌──────────────────────┐
              │  Associação Espacial │
              │   Ponto → Polígono   │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Cálculo Estatísticas │
              │   • Média por LCZ    │
              │   • Desvio padrão    │
              │   • Comparações      │
              └──────────┬───────────┘
                         ↓
         ┌───────────────┴────────────────┐
         ↓                                ↓
┌─────────────────┐            ┌──────────────────────┐
│  visualizer.py  │            │ scenario_simulator.py│
│                 │            │                      │
│ • Gráficos      │            │ • Urbanização        │
│ • Mapas         │            │ • Revegetação        │
│ • Comparações   │            │ • Impactos térmicos  │
└────────┬────────┘            └──────────┬───────────┘
         │                                │
         └───────────────┬────────────────┘
                         ↓
                 ┌───────────────┐
                 │    OUTPUT     │
                 │               │
                 │ • CSV         │
                 │ • PNG         │
                 │ • HTML        │
                 │ • TXT         │
                 └───────────────┘
```

## 🗺️ Estrutura de Classes LCZ

### Classes Construídas (Urbanas)

```
┌─────────────────────────────────────────────────────────┐
│  CLASSES CONSTRUÍDAS - URBAN ZONES                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  LCZ 1-3: COMPACT (Alta densidade)                      │
│  ┌──────┐ ┌──────┐ ┌──────┐                           │
│  │  🏢  │ │  🏢  │ │  🏢  │                           │
│  │ High │ │ Mid  │ │ Low  │                           │
│  └──────┘ └──────┘ └──────┘                           │
│   +4.5°C   +3.5°C   +2.8°C  (vs rural)                 │
│                                                          │
│  LCZ 4-6: OPEN (Baixa densidade)                        │
│  ┌──────┐ ┌──────┐ ┌──────┐                           │
│  │ 🏢   │ │ 🏢   │ │ 🏢   │                           │
│  │ High │ │ Mid  │ │ Low  │                           │
│  └──────┘ └──────┘ └──────┘                           │
│   +2.5°C   +2.0°C   +1.5°C                             │
│                                                          │
│  LCZ 8: LARGE LOW-RISE (Industrial/Comercial)          │
│  ┌────────────────┐                                     │
│  │    🏭  🏢      │                                     │
│  │  Large & Low   │                                     │
│  └────────────────┘                                     │
│       +2.2°C                                            │
│                                                          │
│  LCZ 9: SPARSELY BUILT (Disperso)                      │
│  🏠    🏠     🏠                                        │
│       +0.8°C                                            │
│                                                          │
│  LCZ 10: HEAVY INDUSTRY (Indústria Pesada)             │
│  ┌────────────────┐                                     │
│  │   🏭  🏭  🏭   │                                     │
│  └────────────────┘                                     │
│       +3.0°C                                            │
└─────────────────────────────────────────────────────────┘
```

### Classes Naturais

```
┌─────────────────────────────────────────────────────────┐
│  CLASSES NATURAIS - NATURAL ZONES                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  LCZ A: DENSE TREES (Floresta/Mata densa)              │
│     🌳🌳🌳🌳🌳                                           │
│     🌳🌳🌳🌳🌳                                           │
│        -1.5°C                                           │
│                                                          │
│  LCZ B: SCATTERED TREES (Árvores esparsas)             │
│     🌳   🌳   🌳                                        │
│           🌳                                            │
│        -0.8°C                                           │
│                                                          │
│  LCZ D: LOW PLANTS (Vegetação baixa/campo)             │
│     🌿🌿🌿🌿🌿                                           │
│      REFERÊNCIA: 0°C                                    │
│                                                          │
│  LCZ E: BARE ROCK/PAVED (Rocha/Pavimento)              │
│     ▓▓▓▓▓▓▓▓▓▓                                         │
│        +2.0°C                                           │
│                                                          │
│  LCZ F: BARE SOIL/SAND (Solo/Areia)                    │
│     ░░░░░░░░░░                                         │
│        +1.0°C                                           │
│                                                          │
│  LCZ G: WATER (Água)                                    │
│     ≈≈≈≈≈≈≈≈≈≈                                         │
│        -2.0°C                                           │
└─────────────────────────────────────────────────────────┘
```

## 📈 Exemplos de Saídas

### 1. Gráfico de Temperatura por LCZ

```
Temperature (°C)
    32│     ▄▄
      │    ████
    30│   ██████
      │  ████████
    28│ ██████████  ▄▄
      │████████████████
    26│████████████████  ▄▄
      │████████████████████
    24│████████████████████▄▄
      │██████████████████████
    22│██████████████████████
      └─┬──┬──┬──┬──┬──┬──┬─
        2  3  6  8  9  D  A
       (Mais quente → Mais frio)
```

### 2. Mapa de Calor (Conceitual)

```
     ┌─────────────────────────────┐
     │                              │
     │  🟥🟥🟧🟧🟨🟨🟩🟩🟦🟦        │
     │  ▲                 ▼         │
     │  Quente          Frio        │
     │                              │
     │  LCZ 2 (Centro)             │
     │  🟥 32°C                     │
     │                              │
     │  LCZ 6 (Subúrbio)           │
     │  🟨 28°C                     │
     │                              │
     │  LCZ A (Parque)             │
     │  🟦 24°C                     │
     │                              │
     └─────────────────────────────┘
```

## 🔮 Simulação de Cenários

### Cenário 1: Urbanização

```
ANTES                      DEPOIS
┌──────────┐              ┌──────────┐
│  🌳🌳🌳  │              │  🏢🏢🏢  │
│  🌳🌳🌳  │    ══>       │  🏢🏢🏢  │
│ LCZ A    │              │ LCZ 2    │
│ 26°C     │              │ 30°C     │
└──────────┘              └──────────┘
            IMPACTO: +4°C
```

### Cenário 2: Revegetação

```
ANTES                      DEPOIS
┌──────────┐              ┌──────────┐
│  🏢🏢🏢  │              │  🌳🌳🌳  │
│  🏢🏢🏢  │    ══>       │  🌳🌳🌳  │
│ LCZ 2    │              │ LCZ A    │
│ 30°C     │              │ 26°C     │
└──────────┘              └──────────┘
            IMPACTO: -4°C
```

## 🎯 Interpretação de Resultados

### Ilha de Calor Urbana

```
Perfil de Temperatura Urbano-Rural

Temp (°C)
    32│      ╱‾‾‾‾‾‾╲
      │     ╱        ╲
    30│    ╱          ╲
      │   ╱            ╲
    28│  ╱              ╲____
      │ ╱                    ‾‾╲
    26│╱                        ╲
      │                          ‾
    24│
      └────────────────────────────
       Rural  Subúrbio  Centro  Parque

       LCZ D    LCZ 6    LCZ 2   LCZ A
```

### Recomendações Baseadas em Temperatura

```
┌─────────────────────────────────────┐
│  ZONA CRÍTICA (>30°C) - PRIORIDADE  │
│  ────────────────────────────────   │
│  ⚠️  LCZ 1, 2, 3 (Centros densos)   │
│  ✅  Ação: Plantar árvores          │
│  ✅  Ação: Telhados verdes          │
│  ✅  Ação: Pavimentos permeáveis    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ZONA MODERADA (27-30°C)            │
│  ────────────────────────────────   │
│  ⚡  LCZ 4, 5, 6, 8 (Subúrbios)     │
│  ✅  Ação: Corredores verdes        │
│  ✅  Ação: Sombreamento             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ZONA CONFORTÁVEL (<27°C)           │
│  ────────────────────────────────   │
│  ✅  LCZ A, B, D, G (Vegetação)     │
│  ✅  Ação: Manter e expandir        │
│  ✅  Ação: Proteger de urbanização  │
└─────────────────────────────────────┘
```

## 📱 Interface do Usuário (Conceitual)

### Tela Principal

```
╔════════════════════════════════════════════════╗
║  🏙️  PLANEJADOR URBANO - LAJEADO-RS          ║
╠════════════════════════════════════════════════╣
║                                                ║
║  📊 Dashboard                                  ║
║  ├── 🌡️  Temperatura Média: 28.5°C           ║
║  ├── 🏘️  Zonas Analisadas: 45                ║
║  ├── 🌳 Área Verde: 12.3 km²                  ║
║  └── 🏗️  Área Urbana: 18.7 km²               ║
║                                                ║
║  🗺️  Mapa Interativo                          ║
║  [Ver mapa completo]                           ║
║                                                ║
║  🔮 Simulador de Cenários                      ║
║  ┌──────────────────────────────────┐         ║
║  │ De: [LCZ 2 ▼] Para: [LCZ A ▼]   │         ║
║  │ Área: [50%  ════════════] │         ║
║  │                                    │         ║
║  │ Impacto: -3.5°C ✅                │         ║
║  └──────────────────────────────────┘         ║
║                                                ║
║  📈 Relatórios                                 ║
║  [Baixar PDF] [Baixar CSV] [Compartilhar]     ║
║                                                ║
╚════════════════════════════════════════════════╝
```

## 🔍 Como Interpretar os Arquivos de Saída

### temperature_data.csv
```csv
lat,lon,temperature,lcz_class
-29.4658,-51.9592,30.2,2
-29.4670,-51.9580,28.5,6
-29.4640,-51.9610,26.1,A
```
**Uso:** Dados brutos para análises customizadas

### lcz_statistics.csv
```csv
lcz_class,description,mean_temp,std_temp,count
2,Compact midrise,30.2,0.8,15
A,Dense trees,26.1,0.5,12
```
**Uso:** Resumo executivo por zona

### lcz_map.html
```html
<!DOCTYPE html>
<html>
  <!-- Mapa interativo Leaflet/Folium -->
  <!-- Clique nas zonas para ver detalhes -->
</html>
```
**Uso:** Visualização geoespacial interativa

## 🎓 Glossário Visual

| Termo | Símbolo | Significado |
|-------|---------|-------------|
| LCZ | 🏘️ | Local Climate Zone |
| Ilha de Calor | 🔥 | Área urbana mais quente |
| Temperatura | 🌡️ | Medida em °C |
| Urbanização | 🏗️ | Construção em área verde |
| Revegetação | 🌳 | Plantio em área urbana |
| Delta (Δ) | ± | Diferença de temperatura |

---

**📚 Este guia visual ajuda a entender rapidamente o funcionamento do MVP!**
