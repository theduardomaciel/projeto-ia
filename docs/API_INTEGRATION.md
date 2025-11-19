# API Backend - Guia de Integração

## Visão Geral

A API FastAPI expõe o pipeline de IA de recrutamento inteligente via endpoints REST, permitindo que o frontend web Svelte consuma os serviços de análise de currículos.

## Arquitetura

```
src/api/
  ├── __init__.py          # Exporta app FastAPI
  ├── main.py              # Aplicação principal (CORS, lifespan)
  ├── routes.py            # Endpoints REST
  ├── schemas.py           # Modelos Pydantic (validação)
  └── service.py           # Lógica de negócio (orquestração do pipeline)
```

### Fluxo de Processamento

1. **Upload**: Frontend envia currículos + descrição da vaga via `POST /api/analyze`
2. **Parsing**: `DocumentExtractor` processa arquivos (.txt/.pdf)
3. **Skills**: `SkillExtractor` identifica competências (hard/soft)
4. **Scoring**: `ScoringEngine` calcula pontuações e rankeia
5. **Explainability**: `ExplainabilityEngine` gera justificativas via LLM
6. **Response**: API retorna JSON com candidatos ranqueados

## Endpoints

### `GET /api/health`
Health check da API.

**Response:**
```json
{
  "status": "healthy",
  "api": "recruitment-pipeline"
}
```

### `POST /api/analyze`
Analisa currículos em relação a uma vaga.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `resumes` (files, required): Lista de arquivos de currículos (.txt ou .pdf)
- `job_text` (string, optional): Descrição da vaga como texto
- `job_file` (file, optional): Arquivo com descrição da vaga

**Regras:**
- Pelo menos um de `job_text` ou `job_file` deve ser fornecido
- Currículos devem ser .txt ou .pdf
- Máximo recomendado: 50 currículos por requisição

**Response:** `200 OK`
```json
{
  "data": [
    {
      "candidate_name": "João Silva",
      "hard_skills": ["Python", "FastAPI", "Docker"],
      "soft_skills": ["Comunicação", "Liderança"],
      "match_score": 87.5,
      "explanation": "João possui forte experiência...",
      "ranking_position": 1
    }
  ]
}
```

**Errors:**
- `400 Bad Request`: Parâmetros inválidos
- `500 Internal Server Error`: Erro no processamento

## Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Novas dependências adicionadas:
- `fastapi==0.115.0` - Framework web
- `uvicorn[standard]==0.32.0` - Servidor ASGI
- `python-multipart==0.0.9` - Suporte a file uploads

### 2. Variáveis de Ambiente

Configure as API keys dos provedores LLM em `.env`:

```env
# Gemini (Google AI Studio) - Prioridade
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter (DeepSeek, Llama, etc.) - Alternativa
OPENROUTER_API_KEY=your_openrouter_key_here

# Groq - Alternativa
GROQ_API_KEY=your_groq_key_here
```

### 3. Iniciar Servidor

**Opção 1: Script de conveniência**
```bash
python run_api.py --reload
```

**Opção 2: Uvicorn direto**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Opção 3: Python module**
```bash
python -m src.api.main
```

O servidor estará disponível em:
- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Integração com Frontend

### Estrutura do Frontend (web/)

```typescript
// web/src/lib/api.ts
export async function analyzeResumes(
  files: File[],
  jobOrOptions?: string | { jobText?: string; jobFile?: File }
): Promise<CandidateResult[]>
```

### Configuração

Crie `web/.env` baseado em `web/.env.example`:

```env
# Desenvolvimento (padrão)
PUBLIC_API_BASE_URL=http://localhost:8000

# Produção
# PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

### Iniciar Frontend

```bash
cd web
pnpm install
pnpm dev
```

Frontend: http://localhost:5173

## CORS

CORS está configurado em `src/api/main.py` para permitir acesso dos seguintes origins:

- `http://localhost:5173` (Vite dev server)
- `http://localhost:4173` (Vite preview)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:4173`

**Para produção**, ajuste `allow_origins` para incluir seu domínio:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Desenvolvimento

### Estrutura de Dados

**Candidate (interno)** → **CandidateResult (API)**

```python
# src/core/models.py
@dataclass
class Candidate:
    name: str
    hard_skills: List[Skill]
    soft_skills: List[Skill]
    score: float
    explanation: Optional[str]
    # ...
```

```python
# src/api/schemas.py
class CandidateResult(BaseModel):
    candidate_name: str
    hard_skills: List[str]      # Apenas nomes
    soft_skills: List[str]      # Apenas nomes
    match_score: float
    explanation: str
    ranking_position: int
```

### Logging

Logs estruturados são gerados automaticamente:

```
2025-01-18 10:30:15 [INFO] src.api.service: 📊 Iniciando análise: 1 vaga, 3 currículos
2025-01-18 10:30:15 [INFO] src.api.service:    [1/4] Parsing de documentos...
2025-01-18 10:30:16 [INFO] src.api.service:       ✓ Vaga: Desenvolvedor Python Sênior
2025-01-18 10:30:16 [INFO] src.api.service:       ✓ Candidatos: 3
```

### Testing

```bash
# Via curl
curl -X POST http://localhost:8000/api/analyze \
  -F "resumes=@data/samples/curriculo_01.txt" \
  -F "resumes=@data/samples/curriculo_02.txt" \
  -F "job_text=Desenvolvedor Python com 3+ anos de experiência"

# Via Python
import requests

files = [
    ('resumes', open('data/samples/curriculo_01.txt', 'rb')),
    ('resumes', open('data/samples/curriculo_02.txt', 'rb'))
]
data = {'job_text': 'Desenvolvedor Python Sênior'}

response = requests.post('http://localhost:8000/api/analyze', 
                        files=files, data=data)
print(response.json())
```

## Fallbacks e Resiliência

### 1. Explicações sem LLM

Se API keys não estiverem configuradas ou houver erro, o sistema gera explicações simplificadas baseadas nos scores:

```python
def _generate_fallback_explanations(candidates, job):
    """Gera explicações quando LLM não está disponível"""
    # Usa score_breakdown para criar texto explicativo
```

### 2. Extração Híbrida

`SkillExtractor` usa método híbrido (regex + dicionários + LLM opcional):
- Primeiro tenta métodos determinísticos
- Usa LLM apenas quando necessário

### 3. Error Handling

Todos os endpoints têm tratamento de erros apropriado:
- Validação de inputs (Pydantic)
- Try/except com logs detalhados
- Respostas HTTP com status codes corretos

## Troubleshooting

### Erro: "Não foi possível resolver a importação 'fastapi'"

```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: "Address already in use"

```bash
# Porta 8000 ocupada, use outra:
python run_api.py --port 8001
```

### Frontend não conecta à API

1. Verificar se backend está rodando: `curl http://localhost:8000/api/health`
2. Verificar `PUBLIC_API_BASE_URL` em `web/.env`
3. Verificar CORS no console do navegador

### LLM não gera explicações

1. Verificar `.env` tem API keys configuradas
2. Ver logs: explicações fallback são usadas automaticamente
3. Testar LLM isoladamente: `python -m src.llm.client`

## Próximos Passos

### Features Planejadas

- [ ] Rate limiting (prevenir abuso)
- [ ] Autenticação (JWT tokens)
- [ ] Webhook para processar análises assíncronas
- [ ] Cache de resultados (Redis)
- [ ] Suporte a .docx
- [ ] Batch processing otimizado
- [ ] Métricas e monitoring (Prometheus)

### Melhorias de Performance

- Processar currículos em paralelo (asyncio)
- Cache de embeddings de skills
- Compressão de respostas (gzip)
- Streaming de resultados parciais

## Referências

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Uvicorn**: https://www.uvicorn.org/
- **Pydantic**: https://docs.pydantic.dev/

## Contato

Projeto acadêmico - UFAL IA 2025.1
- Repositório: https://github.com/theduardomaciel/projeto-ia
- Orientador: Prof. Dr. Evandro de Barros Costa
