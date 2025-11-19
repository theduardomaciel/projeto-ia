<picture>
  <source media="(prefers-color-scheme: dark)" srcset="/.github/cover.png">
  <source media="(prefers-color-scheme: light)" srcset="/.github/cover_light.png">
  <img alt="Banner do projeto" src="/.github/cover_light.png">
</picture>

<br/>

## 🚶 Sobre o Projeto

Sistema de Apoio ao Recrutamento Inteligente desenvolvido como requisito da disciplina de Inteligência Artificial (UFAL, 2025.1).
O objetivo é construir um analisador de currículos capaz de identificar *hard skills* e *soft skills*, avaliar a aderência a uma vaga específica de desenvolvedor de software e gerar um ranking dos candidatos acompanhado de justificativas explicáveis.

O projeto integra conceitos de **Agentes Inteligentes (AIMA)**, **LLMs**, **RAG**, **Agentic Workflows** e **Large Reasoning Models (LRMs)**, aliados à prática de **programação em pares com um LLM**.

---

## ⭐ Features

* Extração automática de informações de currículos (.txt, .pdf, .docx)
* Identificação de *hard skills* técnicas
* Análise de *soft skills* e características comportamentais
* Sistema de pontuação configurável para aderência à vaga
* Geração de ranking final de candidatos
* Justificativas detalhadas para cada decisão do sistema
* Módulo opcional de RAG para recuperação de documentos de referência
* Integração com LLM via API (OpenAI, Claude, Gemini, etc.)
* Pipeline extensível e modular

---

## ⚙️ Arquitetura do Sistema

```
src/
  core/           -> Classes centrais do sistema (Candidate, JobProfile, Analyzer)
  parsing/        -> Leitura e normalização de currículos
  skills/         -> Extração e classificação de hard/soft skills
  scoring/        -> Mecanismo de pontuação e ranking
  llm/            -> Integração com LLMs + prompts + estratégias (LLM, RAG)
  explainability/ -> Geração de justificativas e relatórios
  api/            -> FastAPI REST endpoints (NEW!)
  ui/             -> Interface CLI simples para testes
web/
  src/            -> Interface web em Svelte + TypeScript (NEW!)
data/
  samples/        -> Currículos e vagas de exemplo
  config/         -> Listas de skills, pesos, mapeamentos, prompts
```

### Principais conceitos

* **Analyzer**: módulo responsável pela coleta de dados dos candidatos, análise dos perfis e geração do ranking final.
* **SkillExtractor**: identifica competências técnicas e comportamentais utilizando regex, dicionários, heurísticas e LLM.
* **ScoringEngine**: calcula a pontuação final com base no perfil da vaga.
* **LLMClient**: abstração genérica para chamadas a APIs de linguagem.
* **ExplainabilityEngine**: utiliza o LLM para produzir justificativas compreensíveis ao RH.
* **RAGPipeline (opcional)**: permite integrar fontes externas de conhecimento (descrições de vagas, competências, normas da empresa).

---

## 📦 Configuração do Projeto

### Pré-requisitos

* Python 3.10+
* Dependências listadas em `requirements.txt`
* Chave de API para o LLM escolhido
  *(OpenAI, Anthropic, Google, DeepSeek ou outro)*

### Instalação

```bash
git clone https://github.com/<seu-usuario>/<nome-do-repo>.git
cd <nome-do-repo>

python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## ▶️ Executando o Sistema

### 🌐 Opção 1: Interface Web (Recomendado)

**Guia rápido completo:** [`docs/QUICKSTART_INTEGRATION.md`](docs/QUICKSTART_INTEGRATION.md)

#### Backend (Terminal 1)
```bash
# Configure .env com API keys primeiro
python run_api.py --reload
```

#### Frontend (Terminal 2)
```bash
cd web
pnpm install  # primeira vez
pnpm dev
```

**Acesse:** http://localhost:5173

**Documentação da API:** http://localhost:8000/docs

### 💻 Opção 2: CLI (Testes e Desenvolvimento)

#### 1. Fornecer uma vaga e um conjunto de currículos

```
data/
  samples/
    job.txt              -> descrição da vaga
    curriculo_01.txt (ou .pdf/.docx)
    curriculo_02.pdf
    ...
```

#### 2. Rodar o analisador

**Apenas parsing (visualizar currículos carregados):**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/
```

**Com extração de skills:**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --extract
```

**Com ranking completo:**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --rank
```

**Pipeline completo (extração + ranking):**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --extract --rank
```

**Com justificativas geradas por LLM:**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --rank --explain
```

**Especificar provedor e modelo LLM:**
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --rank --explain --provider gemini --model gemini-2.5-flash
```

### 3. Exemplo de saída (ranking)

```
============================================================
RANKING DE CANDIDATOS
============================================================

1º lugar: Maria Santos — 4.5 pontos
   Arquivo: curriculo_02.txt
   Hard skills: 3.4 pts
   Soft skills: 1.1 pts
   Experiência: 0.0 pts
   Educação: 0.0 pts
   Principais skills: python (9.0), rest api (7.7), postgresql (7.2)

2º lugar: João Silva — 4.4 pontos
   Arquivo: curriculo_01.txt
   Hard skills: 3.5 pts
   Soft skills: 0.9 pts
   ...
```

---

## 📊 Dependências

### Backend (Python)
* `fastapi` / `uvicorn` → API REST **(NEW!)**
* `python-multipart` → uploads de arquivos **(NEW!)**
* `python-dotenv` → carregamento de variáveis de ambiente
* `google-generativeai` → integração com Gemini (prioridade)
* `openai` → integração com Groq/OpenRouter/DeepSeek
* `numpy` / `pandas` → manipulação de dados
* `scikit-learn` → heurísticas auxiliares (similaridade, vetorização)
* `pdfplumber` / `python-docx` → leitura unificada de currículos em PDF/DOCX
* `tqdm` / `rich` → UI/UX no terminal

### Frontend (TypeScript/Svelte)
* `svelte` / `sveltekit` → framework web **(NEW!)**
* `typescript` → type safety **(NEW!)**
* `vite` → bundler e dev server **(NEW!)**

---

## 📁 Estrutura do Repositório

```
├── src/
│   ├── core/             → Modelos de dados centrais
│   ├── parsing/          → Extração de texto de currículos
│   ├── skills/           → Identificação de skills
│   ├── scoring/          → Cálculo de pontuações
│   ├── llm/              → Cliente LLM abstrato + provedores
│   ├── explainability/   → Geração de justificativas
│   ├── api/              → FastAPI endpoints (NEW!)
│   └── ui/               → CLI para testes
├── web/
│   ├── src/
│   │   ├── routes/       → Páginas Svelte (NEW!)
│   │   └── lib/          → API client, componentes (NEW!)
│   └── package.json
├── data/
│   ├── samples/          → Currículos e vagas de exemplo
│   └── config/           → Skills, pesos, prompts
├── docs/
│   ├── API_INTEGRATION.md      → Guia da API (NEW!)
│   ├── QUICKSTART_INTEGRATION.md  → Setup rápido (NEW!)
│   ├── ARCHITECTURE.md
│   └── LLM_PROVIDERS.md
├── tests/
├── run_api.py            → Script de inicialização da API (NEW!)
├── requirements.txt
├── README.md
└── .env.example
```

---

## 🔗 Documentação Adicional

* **[API Integration Guide](docs/API_INTEGRATION.md)** - Detalhes completos da API REST
* **[Quick Start Integration](docs/QUICKSTART_INTEGRATION.md)** - Setup em 5 minutos
* **[Architecture](docs/ARCHITECTURE.md)** - Visão geral da arquitetura
* **[LLM Providers](docs/LLM_PROVIDERS.md)** - Configuração de provedores LLM
* **[Web UI Guide](web/README.md)** - Frontend Svelte

## 👣 Roadmap (Próximos Passos)

1. [x] Pipeline básico de extração e pontuação
2. [x] Integração com LLM para explicabilidade
3. [x] API REST com FastAPI **(DONE!)**
4. [x] Interface web em Svelte **(DONE!)**
3. [ ] Implementação completa do módulo de soft skills
4. [ ] Interface web simples (Flask ou FastAPI)
5. [ ] Dashboard para visualização dos resultados
6. [ ] Módulo de fairness & bias-check

---

## ℹ️ Fontes dos Datasets:

- https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset?resource=download
- https://github.com/NataliaVanetik/vacancy-resume-matching-dataset?utm_source=chatgpt.com

---

## 👥 Equipe

Disciplina ministrada pelo Prof. Dr. Evandro de Barros Costa.  
Projeto desenvolvido por:

* [Eduardo Maciel (@theduardomaciel)](https://github.com/theduardomaciel)
* [Josenilton Ferreira (@914joseph)](https://github.com/914joseph)
* [Lucas Cassiano Maciel dos Santos (@lucas7maciel)](https://github.com/lucas7maciel)
* [Maria Letícia Ventura de Oliveira (@letsventura)](https://github.com/letsventura)