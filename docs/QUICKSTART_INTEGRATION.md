# Guia Rápido - Integração API + Web Frontend

## Setup Completo em 5 Minutos

### 1. Instalar Dependências do Backend

```bash
# No diretório raiz do projeto
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. Configurar API Keys

Crie `.env` na raiz do projeto:

```env
# Escolha pelo menos um provedor LLM
GEMINI_API_KEY=sua_chave_aqui
# OPENROUTER_API_KEY=sua_chave_aqui
# GROQ_API_KEY=sua_chave_aqui
```

**Obter API Keys (gratuitas):**
- Gemini: https://aistudio.google.com/app/apikey
- OpenRouter: https://openrouter.ai/keys
- Groq: https://console.groq.com/keys

### 3. Iniciar Backend (Terminal 1)

```bash
python run_api.py --reload
```

Aguarde mensagem:
```
🚀 Sistema de Apoio ao Recrutamento Inteligente - API
📍 Servidor: http://0.0.0.0:8000
📖 Documentação: http://localhost:8000/docs
```

### 4. Instalar Dependências do Frontend

```bash
# Em novo terminal, navegue para web/
cd web
pnpm install  # ou npm install
```

### 5. Configurar Frontend (Opcional)

Crie `web/.env` (opcional, usa defaults se não criar):

```env
PUBLIC_API_BASE_URL=http://localhost:8000
```

### 6. Iniciar Frontend (Terminal 2)

```bash
# Dentro de web/
pnpm dev
```

Aguarde mensagem:
```
VITE v5.x.x  ready in XXX ms
➜  Local:   http://localhost:5173/
```

### 7. Testar Integração

1. Abra http://localhost:5173 no navegador
2. Faça upload de currículos de `data/samples/curriculo_*.txt`
3. Cole descrição de vaga ou envie `data/samples/job.txt`
4. Clique em "Analisar Currículos"
5. Veja resultados ranqueados com explicações!

## Testes Via API (sem interface)

### Teste 1: Health Check

```bash
curl http://localhost:8000/api/health
```

Esperado:
```json
{"status":"healthy","api":"recruitment-pipeline"}
```

### Teste 2: Análise com curl

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resumes=@data/samples/curriculo_01.txt" \
  -F "resumes=@data/samples/curriculo_02.txt" \
  -F "job_text=Desenvolvedor Python com experiência em APIs REST e bancos de dados"
```

### Teste 3: Via Documentação Interativa

Acesse http://localhost:8000/docs e use a interface Swagger para testar endpoints.

## Estrutura de Resposta

```typescript
interface CandidateResult {
  candidate_name: string;        // Nome do candidato
  hard_skills: string[];         // ["Python", "FastAPI", ...]
  soft_skills: string[];         // ["Comunicação", "Liderança", ...]
  match_score: number;           // 0-100
  explanation: string;           // Justificativa via LLM
  ranking_position: number;      // 1, 2, 3...
}
```

## Comandos Úteis

### Backend

```bash
# Iniciar com auto-reload
python run_api.py --reload

# Iniciar em porta diferente
python run_api.py --port 8080

# Logs debug
python run_api.py --log-level debug

# Ver documentação interativa
open http://localhost:8000/docs
```

### Frontend

```bash
cd web

# Desenvolvimento
pnpm dev

# Build para produção
pnpm build

# Preview da build
pnpm preview

# Linting
pnpm lint
```

## Troubleshooting Rápido

### Backend não inicia

```bash
# Verificar se porta 8000 está livre
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# Verificar instalação
pip list | grep fastapi
pip list | grep uvicorn
```

### Frontend não conecta

1. Backend rodando? → `curl http://localhost:8000/api/health`
2. CORS configurado? → Ver console do navegador (F12)
3. URL correta? → Verificar `PUBLIC_API_BASE_URL` em `web/.env`

### Sem explicações LLM

- **Normal**: Sistema usa fallback automático se API keys não configuradas
- **Ver logs**: Backend mostra avisos se LLM não disponível
- **Testar**: `python -m src.llm.client` (verifica conexão)

### Erro ao processar PDF

```bash
# Reinstalar dependências de parsing
pip install --upgrade pdfplumber python-docx
```

## Arquivos de Exemplo

Use os arquivos de teste incluídos:

```
data/samples/
  ├── job.txt           # Descrição de vaga exemplo
  ├── curriculo_01.txt  # Candidato 1
  ├── curriculo_02.txt  # Candidato 2
  ├── curriculo_03.txt  # Candidato 3
  └── curriculo_04.txt  # Candidato 4
```

## Próximos Passos

- ✅ Pipeline básico funcionando
- ✅ API REST exposta
- ✅ Frontend conectado
- 🔄 Melhorar extração de skills (ajustar regex em `data/config/skills.json`)
- 🔄 Ajustar pesos de pontuação (`data/config/weights.json`)
- 🔄 Refinar prompts LLM (`data/config/prompt_templates.txt`)
- 🔄 Adicionar mais exemplos de currículos
- 🔄 Deploy (Render, Vercel, Railway, etc.)

## Documentação Completa

- **API**: `docs/API_INTEGRATION.md`
- **Arquitetura**: `docs/ARCHITECTURE.md`
- **LLM Providers**: `docs/LLM_PROVIDERS.md`
- **Interface Web**: `web/README.md`

## Suporte

Problemas? Abra issue no GitHub:
https://github.com/theduardomaciel/projeto-ia/issues
