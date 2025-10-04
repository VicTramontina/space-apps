# 🚀 Guia Rápido de Início

## Passo 1: Instalar Python
Certifique-se de ter Python 3.8 ou superior instalado:
```bash
python --version
```

## Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

## Passo 3: Configurar API Meteomatics

1. Acesse: https://www.meteomatics.com/
2. Crie uma conta (há opção de teste gratuito)
3. Copie suas credenciais

4. Crie o arquivo `.env` na raiz do projeto:
```bash
cp .env.example .env
```

5. Edite `.env` e adicione suas credenciais:
```
METEOMATICS_USERNAME=seu_usuario_aqui
METEOMATICS_PASSWORD=sua_senha_aqui
```

## Passo 4: Executar a Aplicação
```bash
python app.py
```

## Passo 5: Abrir no Navegador
Acesse: http://localhost:5000

## 🎯 Primeiros Passos na Interface

1. **Visualizar o Mapa**: O mapa de Lajeado-RS carregará automaticamente com as zonas LCZ coloridas

2. **Ver Temperaturas**: Clique no botão "📊 Carregar Camada de Temperatura"
   - Isso pode levar alguns segundos
   - Pontos coloridos aparecerão mostrando a temperatura

3. **Selecionar uma Zona**: Clique em qualquer área colorida no mapa
   - A zona será destacada em amarelo
   - Informações aparecerão na barra lateral

4. **Simular uma Mudança**:
   - No dropdown "Selecione uma nova LCZ", escolha um tipo diferente
   - Clique em "🔄 Calcular Cenário"
   - Veja o impacto na temperatura!

## 💡 Exemplo de Uso

**Cenário**: "O que aconteceria se transformássemos uma área industrial em um parque?"

1. Clique em uma zona LCZ 10 (Heavy Industry) - laranja escuro
2. Veja a temperatura atual (ex: 32°C)
3. Selecione "LCZ 11 - Dense Trees"
4. Clique em "Calcular Cenário"
5. **Resultado**: Temperatura cairia para ~27.9°C (redução de -4.1°C!)

## ⚠️ Solução de Problemas

### Erro: "Unable to fetch temperature data"
- Verifique se as credenciais da Meteomatics estão corretas no arquivo `.env`
- Certifique-se de que sua conta Meteomatics está ativa

### Mapa não carrega
- Verifique se o arquivo KMZ está em `lajeado-result/21025c4c602c6ebc89232bf384a56fac185220af.kmz`
- Veja os logs no terminal para mais detalhes

### Erro de dependências
```bash
pip install --upgrade -r requirements.txt
```

## 📖 Próximos Passos

- Leia o [README.md](README.md) completo para entender a metodologia
- Explore diferentes cenários de conversão de LCZ
- Veja a [documentação de referência](README.md#-referências-científicas)
