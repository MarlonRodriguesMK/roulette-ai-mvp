# 🎰 Roulette AI - Backend API

API de análise inteligente para roleta ao vivo com IA, OCR e análise em tempo real.

## ✨ Funcionalidades

- 🧠 **Motor de IA Avançado**: Análise completa de padrões físicos e estatísticos
- 📸 **OCR Inteligente**: Extração automática de números de screenshots
- 🔥 **Análise em Tempo Real**: Zonas quentes/frias, vizinhos, cavalos
- 📊 **Setores Físicos**: Voisins du Zero, Tiers, Orphelins
- 🎯 **Estratégias Customizadas**: Sistema de gatilhos personalizáveis
- 📈 **Terminais e Ausências**: Análise avançada de padrões
- 🔐 **Sessões Isoladas**: Cada usuário tem seu próprio histórico

## 🚀 Quick Start

### Pré-requisitos

- Python 3.9+
- Tesseract OCR (para funcionalidade de OCR)

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# MacOS
brew install tesseract

# Windows
# Baixar de: https://github.com/UB-Mannheim/tesseract/wiki
```

### Instalação

```bash
# 1. Clone o repositório
git clone <seu-repo>
cd roulette-ai-backend

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env conforme necessário

# 5. Execute
python main.py
```

API estará rodando em: `http://localhost:8000`

## 📚 Documentação da API

### Endpoints Principais

#### 1️⃣ Adicionar Spin Único

```http
POST /api/v1/add-spin
Content-Type: application/json

{
  "number": 17,
  "history_limit": 50
}
```

**Resposta:**
```json
{
  "status": "ok",
  "session_id": "uuid-da-sessao",
  "data": {
    "status": "ok",
    "history": [17],
    "spins": [...],
    "physical_zones": [...],
    "neighbors": [...],
    "terminals": {...},
    "absences": {...},
    "stats": {...}
  }
}
```

#### 2️⃣ Entrada Manual Múltipla

```http
POST /api/v1/manual-input
Content-Type: application/json

{
  "numbers": [7, 12, 33, 0, 21, 17],
  "history_limit": 50
}
```

#### 3️⃣ Upload de Imagem (OCR)

```http
POST /api/v1/ocr-upload
Content-Type: multipart/form-data

file: <imagem.png>
session_id: <opcional>
history_limit: 50
```

#### 4️⃣ Obter Análise

```http
GET /api/v1/analysis?session_id=<uuid>&history_limit=50
```

#### 5️⃣ Estratégias Customizadas

```http
POST /api/v1/strategies
Content-Type: application/json

{
  "strategies": [
    {
      "name": "Vizinhos do 17",
      "triggers": [17, 34, 6, 25, 2]
    }
  ],
  "history_limit": 50
}
```

#### 6️⃣ Limpar Sessão

```http
DELETE /api/v1/session/<session_id>
```

#### 7️⃣ Stats da Sessão

```http
GET /api/v1/session/<session_id>/stats
```

## 🧪 Testando a API

### Com cURL

```bash
# Healthcheck
curl http://localhost:8000/

# Adicionar spin
curl -X POST http://localhost:8000/api/v1/add-spin \
  -H "Content-Type: application/json" \
  -d '{"number": 17}'

# Múltiplos números
curl -X POST http://localhost:8000/api/v1/manual-input \
  -H "Content-Type: application/json" \
  -d '{"numbers": [7, 12, 33, 0, 21]}'
```

### Com Python

```python
import requests

# Adicionar spin
response = requests.post(
    "http://localhost:8000/api/v1/add-spin",
    json={"number": 17, "history_limit": 50}
)

data = response.json()
print(data["data"]["stats"])

# Upload OCR
with open("screenshot.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/ocr-upload",
        files={"file": f}
    )

numbers = response.json()["extracted_numbers"]
print(f"Números extraídos: {numbers}")
```

### Documentação Interativa

Acesse a documentação Swagger em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Estrutura de Resposta

### Análise Completa

```json
{
  "status": "ok",
  "numbers": {"17": 3, "0": 1, ...},
  "history": [17, 0, 12, ...],
  
  "spins": [
    {
      "number": 17,
      "wheel_index": 8,
      "color": "black",
      "parity": "odd",
      "dozen": 2,
      "column": 2,
      "high_low": "low",
      "terminal": 7,
      "sector": "voisins",
      "neighbors_1": [25, 2],
      "neighbors_3": [34, 6, 25, 2, 21, 4]
    }
  ],
  
  "physical_zones": [
    {
      "name": "Voisins du Zero",
      "key": "voisins",
      "numbers": [0, 2, 3, ...],
      "hits": 15,
      "percentage": 45.5,
      "status": "🔥 Quente",
      "explanation": "Zona com maior recorrência..."
    }
  ],
  
  "neighbors": [
    {"number": 25, "pressure": 5},
    {"number": 2, "pressure": 4}
  ],
  
  "terminals": {
    "window": 50,
    "counts": {"7": 8, "2": 6, ...},
    "detail": [...],
    "top": [...],
    "cold": [...]
  },
  
  "absences": {
    "numbers": [1, 5, 9, ...],
    "zones": [],
    "horses": [...],
    "terminals": [3, 8]
  },
  
  "stats": {
    "total_spins": 50,
    "hottest_number": 17,
    "hottest_hits": 5,
    "color": {"red": 22, "black": 25, "green": 3},
    "parity": {"even": 24, "odd": 23},
    "dozens": {"1": 15, "2": 18, "3": 14},
    "high_low": {"low": 26, "high": 21}
  }
}
```

## 🔐 Segurança

### Desenvolvimento

O `.env.example` está configurado para desenvolvimento:
- CORS aberto para localhost
- Debug mode ativado
- Logs verbosos

### Produção

**IMPORTANTE**: Antes de deploy em produção:

1. **CORS**: Configure `ALLOWED_ORIGINS` apenas com domínios permitidos
2. **Debug**: `DEBUG=False`
3. **HTTPS**: Use apenas HTTPS
4. **Rate Limiting**: Implemente rate limiting
5. **Autenticação**: Adicione JWT ou API Keys
6. **Secrets**: Use secrets manager (AWS Secrets, etc)

```bash
# .env de produção
DEBUG=False
ALLOWED_ORIGINS=["https://meu-frontend.com"]
```

## 🛠️ Desenvolvimento

### Estrutura de Pastas

```
app/
├── core/          # Configurações
├── models/        # Schemas Pydantic
├── services/      # Lógica de negócio
├── engines/       # Motor de IA
└── routers/       # Rotas (futuro)
```

### Adicionar Nova Funcionalidade

1. Crie schema em `app/models/schemas.py`
2. Implemente lógica em `app/services/`
3. Adicione rota em `main.py` (ou crie novo router)
4. Adicione testes em `tests/`

### Executar Testes

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Executar testes
pytest tests/

# Com coverage
pytest --cov=app tests/
```

## 🐛 Troubleshooting

### OCR não funciona

```bash
# Verificar se Tesseract está instalado
tesseract --version

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Se ainda não funcionar, especifique o caminho no código:
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
```

### Erro de CORS

```bash
# Adicione seu domínio frontend em .env
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Sessão não encontrada

As sessões ficam em memória. Se reiniciar o servidor, todas as sessões são perdidas.
Para produção, migre para Redis ou banco de dados.

## 📈 Performance

### Otimizações Implementadas

- ✅ Precomputação de vizinhos físicos
- ✅ Uso de frozenset para lookups rápidos
- ✅ Cache de índices da roleta
- ✅ Validação Pydantic eficiente
- ✅ Thread de limpeza automática de sessões

### Para Escalar

- Use Redis para sessões
- Adicione cache com Redis/Memcached
- Use banco de dados para persistência
- Configure workers Gunicorn
- Use load balancer (nginx)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 License

MIT License

## 👨‍💻 Autor

Seu Nome - [@MarlonRodrigueMK](https://github.com/MarlonRodrigueMK)

## 🙏 Agradecimentos

- FastAPI pela excelente framework
- Tesseract pela engine OCR
- Comunidade Python