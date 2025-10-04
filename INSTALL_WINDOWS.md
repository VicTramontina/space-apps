# 🪟 Guia de Instalação para Windows

## Opção 1: Instalação Completa (com GeoPandas)

### Pré-requisitos
1. Python 3.8+ instalado
2. Visual C++ Build Tools (para compilar pacotes)

### Passos

```bash
# 1. Atualizar pip
python -m pip install --upgrade pip

# 2. Tentar instalação completa
pip install -r requirements.txt
```

**Se der erro no GeoPandas**, siga para Opção 2.

---

## Opção 2: Instalação Simplificada (SEM GeoPandas)

Esta é a opção recomendada para Windows!

### Passos

```bash
# 1. Usar requirements simplificado
pip install -r requirements-simple.txt

# 2. Modificar app.py para usar versão simplificada
```

Abra `app.py` e modifique a linha 8:

**De:**
```python
from lcz_processor import LCZProcessor
```

**Para:**
```python
from lcz_processor_simple import LCZProcessor
```

---

## Opção 3: Conda (Mais Fácil para Windows)

Se você tem Anaconda ou Miniconda:

```bash
# Criar ambiente
conda create -n lcz-analysis python=3.10

# Ativar
conda activate lcz-analysis

# Instalar GeoPandas via conda (muito mais fácil!)
conda install -c conda-forge geopandas

# Instalar resto
pip install Flask folium python-dotenv requests Pillow
```

---

## Configurar API Meteomatics

```bash
# Copiar exemplo
copy .env.example .env

# Editar .env no Notepad ou seu editor favorito
notepad .env
```

Adicione suas credenciais:
```
METEOMATICS_USERNAME=seu_usuario
METEOMATICS_PASSWORD=sua_senha
```

---

## Executar

```bash
python app.py
```

Acesse: http://localhost:5000

---

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'geopandas'"

**Solução A** - Use a versão simplificada:
```bash
pip install -r requirements-simple.txt
```

E modifique `app.py` linha 8:
```python
from lcz_processor_simple import LCZProcessor
```

**Solução B** - Instale via Conda:
```bash
conda install -c conda-forge geopandas
```

### Erro: "Building wheel for shapely"

```bash
# Instalar via binário pré-compilado
pip install --only-binary :all: shapely
```

### Erro: "Microsoft Visual C++ 14.0 is required"

Baixe e instale: https://visualstudio.microsoft.com/visual-cpp-build-tools/

Ou use `requirements-simple.txt` + `lcz_processor_simple.py`

---

## Verificar Instalação

```bash
python -c "from lcz_processor_simple import LCZProcessor; print('OK!')"
```

Se imprimir "OK!", está tudo certo! 🎉
