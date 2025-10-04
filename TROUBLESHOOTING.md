# 🔧 Solução de Problemas

## ❌ Erro: "Credenciais da API não fornecidas"

### Problema
```
ERROR:__main__:Credenciais da API não fornecidas!
```

### Soluções

#### **Opção 1: Modo Demo (Sem API)** ⭐ Recomendado
```bash
python main.py --skip-api
```
Usa dados sintéticos - perfeito para testar!

---

#### **Opção 2: Arquivo .env**
1. Instale python-dotenv:
   ```bash
   pip install python-dotenv
   ```

2. Crie arquivo `.env` (sem .example):
   ```bash
   METEOMATICS_USERNAME=seu_usuario
   METEOMATICS_PASSWORD=sua_senha
   ```

3. Execute:
   ```bash
   python main.py
   ```

---

#### **Opção 3: Linha de Comando**
```bash
python main.py --username seu_usuario --password sua_senha
```

---

#### **Opção 4: Variáveis de Ambiente**

**Windows (PowerShell):**
```powershell
$env:METEOMATICS_USERNAME="seu_usuario"
$env:METEOMATICS_PASSWORD="sua_senha"
python main.py
```

**Windows (CMD):**
```cmd
set METEOMATICS_USERNAME=seu_usuario
set METEOMATICS_PASSWORD=sua_senha
python main.py
```

**Linux/Mac:**
```bash
export METEOMATICS_USERNAME="seu_usuario"
export METEOMATICS_PASSWORD="sua_senha"
python main.py
```

---

## ❌ Erro: "Arquivo KML não encontrado"

### Problema
```
ERROR:__main__:Arquivo KML não encontrado
```

### Soluções

1. **Verificar se o arquivo existe:**
   ```bash
   # Windows
   dir lajeado-result\data\*.kml

   # Linux/Mac
   ls lajeado-result/data/*.kml
   ```

2. **Usar caminho absoluto:**
   ```bash
   python main.py --kml "C:\caminho\completo\arquivo.kml" --skip-api
   ```

3. **Verificar estrutura:**
   ```
   space-apps/
   ├── main.py
   └── lajeado-result/
       └── data/
           └── *.kml  ← Deve estar aqui
   ```

---

## ❌ Erro: "ModuleNotFoundError"

### Problema
```
ModuleNotFoundError: No module named 'geopandas'
```

### Solução
```bash
pip install -r requirements.txt
```

Se persistir, instale individualmente:
```bash
pip install geopandas pandas numpy matplotlib seaborn folium requests shapely fiona pyproj fastkml python-dotenv
```

---

## ❌ Erro: "KML driver not available"

### Problema
```
ERROR: KML driver not available in fiona
```

### Soluções

#### Windows
1. **Instalar GDAL via conda:**
   ```bash
   conda install -c conda-forge gdal
   pip install geopandas
   ```

2. **Ou usar pyogrio (mais simples):**
   ```bash
   pip install pyogrio
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
pip install geopandas
```

#### Mac
```bash
brew install gdal
pip install geopandas
```

---

## ⚠️ Aviso: "Only 3 zones loaded"

### Problema
```
INFO:__main__:✓ Carregadas 3 zonas LCZ
```
Mas deveria carregar mais.

### Causa
KML com múltiplas camadas (layers).

### Solução
✅ **Já corrigido!** O código agora carrega automaticamente todas as camadas.

Execute novamente:
```bash
python main.py --skip-api
```

Você deve ver:
```
INFO:lcz_processor:Camadas encontradas no KML: ['2', '3', '4', '5', '6', '8', '9', '10', 'A', 'B', 'D', 'E', 'F', 'G']
```

---

## ❌ Erro: "Geometry is in a geographic CRS"

### Problema
```
UserWarning: Geometry is in a geographic CRS. Results from 'centroid' are likely incorrect.
```

### Solução
⚠️ Este é apenas um **aviso**, não um erro. O código funciona corretamente.

Para suprimir o aviso, adicione no início do script:
```python
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
```

---

## ❌ Erro: "Package lxml missing"

### Problema
```
UserWarning: Package `lxml` missing. Pretty print will be disabled
```

### Solução (Opcional)
```bash
pip install lxml
```

⚠️ Não é necessário para funcionalidade básica.

---

## 🐍 Versão do Python

### Requisitos
- **Python 3.8 ou superior**
- Testado com Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

### Verificar versão
```bash
python --version
```

Se < 3.8, atualize o Python.

---

## 💾 Falta de Memória

### Problema
```
MemoryError: Unable to allocate array
```

### Solução
Reduza o número de pontos de amostragem em `main.py`:

```python
# Altere de:
points = processor.get_sampling_points(points_per_zone=5)

# Para:
points = processor.get_sampling_points(points_per_zone=2)
```

---

## 🗺️ Mapa não Abre

### Problema
Arquivo `lcz_map.html` não abre corretamente.

### Soluções

1. **Abrir com navegador específico:**
   ```bash
   # Windows
   start chrome output\lcz_map.html

   # Mac
   open -a "Google Chrome" output/lcz_map.html

   # Linux
   google-chrome output/lcz_map.html
   ```

2. **Verificar se arquivo foi criado:**
   ```bash
   ls -lh output/lcz_map.html
   ```

3. **Usar caminho absoluto:**
   - Clique com botão direito no arquivo
   - "Abrir com" → Navegador

---

## 📊 Gráficos não Aparecem

### Problema
Arquivos PNG criados mas vazios.

### Solução
Verifique backend do matplotlib:

```python
import matplotlib
print(matplotlib.get_backend())
```

Se necessário, altere em `visualizer.py`:
```python
import matplotlib
matplotlib.use('Agg')  # Backend para salvar arquivos
```

---

## 🔍 Como Verificar se Está Funcionando?

Execute o teste completo:

```bash
python test_mvp.py
```

Você deve ver:
```
✅ TODOS OS TESTES PASSARAM (6/6)
```

---

## 📞 Ainda com Problemas?

1. **Verifique logs detalhados:**
   Execute com mais verbosidade:
   ```bash
   python main.py --skip-api 2>&1 | tee log.txt
   ```

2. **Abra uma issue:**
   - Inclua: versão Python, SO, erro completo
   - Cole o conteúdo de `log.txt`

3. **Documentação:**
   - README.md
   - QUICKSTART.md
   - examples.py

---

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] pip atualizado (`pip install --upgrade pip`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo KML existe em `lajeado-result/data/`
- [ ] Teste executado com sucesso (`python test_mvp.py`)
- [ ] MVP rodando em modo demo (`python main.py --skip-api`)

---

**Se tudo isso funcionou, você está pronto! 🎉**
