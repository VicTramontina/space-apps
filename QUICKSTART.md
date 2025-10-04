# 🚀 Guia de Início Rápido

## 1️⃣ Instalação Rápida (5 minutos)

### Passo 1: Clonar o Repositório
```bash
cd space-apps
```

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Executar em Modo Demo
```bash
python main.py --skip-api
```

**Pronto!** 🎉 Os resultados estarão em `output/`

---

## 2️⃣ Usando com API Real (Recomendado)

### Passo 1: Obter Credenciais Meteomatics

1. Acesse: https://www.meteomatics.com/en/sign-up-weather-api-test-account/
2. Preencha o formulário
3. Receba credenciais por email (username e password)

### Passo 2: Configurar Credenciais

**Opção A: Variáveis de Ambiente (Linux/Mac)**
```bash
export METEOMATICS_USERNAME="seu_usuario"
export METEOMATICS_PASSWORD="sua_senha"
python main.py
```

**Opção B: Variáveis de Ambiente (Windows)**
```cmd
set METEOMATICS_USERNAME=seu_usuario
set METEOMATICS_PASSWORD=sua_senha
python main.py
```

**Opção C: Linha de Comando**
```bash
python main.py --username seu_usuario --password sua_senha
```

---

## 3️⃣ Visualizar Resultados

### Mapa Interativo
Abra no navegador:
```
output/lcz_map.html
```

### Gráficos
- `output/temperature_by_lcz.png` - Temperatura por zona
- `output/temperature_delta.png` - Comparação com valores esperados
- `output/scenario_example.png` - Exemplo de cenário

### Dados
- `output/temperature_data.csv` - Dados brutos
- `output/lcz_statistics.csv` - Estatísticas por LCZ
- `output/relatorio.txt` - Relatório completo

---

## 4️⃣ Testar com Seus Próprios Dados

```bash
python main.py --kml seu_arquivo.kml --output-dir meus_resultados
```

**Requisitos do arquivo KML:**
- Polígonos com classe LCZ no campo "Name" (ex: "2", "A", "G")
- Sistema de coordenadas WGS84
- Estrutura compatível com Google Earth

---

## 5️⃣ Resolução de Problemas

### Erro: "Arquivo KML não encontrado"
```bash
# Verificar caminho do arquivo
ls lajeado-result/data/*.kml

# Usar caminho absoluto
python main.py --kml /caminho/completo/arquivo.kml
```

### Erro: "Credenciais inválidas"
```bash
# Testar em modo simulado primeiro
python main.py --skip-api

# Verificar variáveis de ambiente
echo $METEOMATICS_USERNAME
```

### Erro: "ModuleNotFoundError"
```bash
# Reinstalar dependências
pip install -r requirements.txt --upgrade
```

### Erro: "KML driver not available"
```bash
# Instalar GDAL (se necessário)
# Ubuntu/Debian:
sudo apt-get install gdal-bin libgdal-dev

# Mac:
brew install gdal

# Windows: baixar de https://www.gisinternals.com/
```

---

## 6️⃣ Exemplos de Uso

### Exemplo 1: Análise Básica
```bash
python main.py --skip-api
```

### Exemplo 2: Análise com API
```bash
export METEOMATICS_USERNAME="user123"
export METEOMATICS_PASSWORD="pass456"
python main.py
```

### Exemplo 3: Arquivo KML Customizado
```bash
python main.py \
  --kml dados/minha_cidade.kml \
  --output-dir resultados/minha_cidade \
  --skip-api
```

---

## 7️⃣ Próximos Passos

Após executar com sucesso:

1. 📊 **Explore os dados** em `output/lcz_statistics.csv`
2. 🗺️ **Visualize o mapa** em `output/lcz_map.html`
3. 🔮 **Analise cenários** em `output/scenarios_comparison.csv`
4. 📄 **Leia o relatório** em `output/relatorio.txt`

### Aprofundar-se no Código

```python
# Experimentar com código Python
from lcz_processor import LCZProcessor
from visualizer import Visualizer

processor = LCZProcessor('lajeado-result/data/*.kml')
print(processor.gdf[['lcz_class', 'lcz_description', 'area_km2']])
```

---

## ❓ Precisa de Ajuda?

- 📖 Documentação completa: [`README.md`](README.md)
- 🐛 Reportar problema: Abra uma issue
- 💡 Sugestões: Pull requests são bem-vindos!

---

**Tempo estimado:** 5-10 minutos ⏱️

**Dificuldade:** Iniciante 🟢
