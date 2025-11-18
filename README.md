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

* Extração automática de informações de currículos (texto puro ou estruturado)
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
  ui/             -> Interface CLI simples para testes
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

### 1. Fornecer uma vaga e um conjunto de currículos

```
data/
  samples/
    job.txt              -> descrição da vaga
    curriculo_01.txt
    curriculo_02.txt
    ...
```

### 2. Rodar o analisador

```bash
python src/main.py \
  --job data/samples/job.txt \
  --cvs data/samples/
```

### 3. Exemplo de saída (resumo)

```
Ranking de Candidatos
----------------------

1º João Silva (82 pts)
   Hard skills: Python, SQL, APIs REST
   Soft skills: Comunicação clara, Adaptabilidade
   Justificativa: O candidato demonstra...

2º Maria Santos (78 pts)
   Hard skills: Java, Spring, Docker
   Justificativa: ...

3º Pedro Costa (64 pts)
   ...
```

---

## 📊 Dependências

* `python-dotenv` → carregamento de variáveis de ambiente
* `openai` / `anthropic` / `google-generativeai` → integração com LLM
* `numpy` / `pandas` → manipulação de dados
* `scikit-learn` → heurísticas auxiliares (similaridade, vetorização)
* `tqdm` → barras de progresso
* `rich` → logs bonitos no terminal

---

## 🔍 Programação em Pares com um LLM

Durante o desenvolvimento, o sistema registra:

* exemplos de prompts utilizados
* respostas do LLM
* sugestões adotadas ou rejeitadas
* análises críticas de decisões incorretas ou enviesadas

Esse material é utilizado no relatório final da disciplina.

---

## 📁 Estrutura do Repositório

```
├── src/
│   ├── core/
│   ├── parsing/
│   ├── skills/
│   ├── scoring/
│   ├── llm/
│   ├── explainability/
│   ├── ui/
│   └── main.py
├── data/
│   ├── samples/
│   └── config/
├── docs/
│   └── relatorio/ (opcional)
├── tests/
├── requirements.txt
├── README.md
└── .env.example
```

---

## 👣 Roadmap (Próximos Passos)

1. [x] Pipeline básico de extração e pontuação
2. [x] Integração com LLM para explicabilidade
3. [ ] Implementação completa do módulo de soft skills
4. [ ] RAG para enriquecimento da análise
5. [ ] Interface web simples (Flask ou FastAPI)
6. [ ] Dashboard para visualização dos resultados
7. [ ] Módulo de fairness & bias-check

---

## 👥 Equipe

Disciplina ministrada pelo Prof. Dr. Evandro de Barros Costa.  
Projeto desenvolvido por:

* [Eduardo Maciel (@theduardomaciel)](https://github.com/theduardomaciel)
* [Josenilton Ferreira (@914joseph)](https://github.com/914joseph)
* [Lucas Cassiano Maciel dos Santos (@lucas7maciel)](https://github.com/lucas7maciel)
* [Maria Letícia Ventura de Oliveira (@letsventura)](https://github.com/letsventura)