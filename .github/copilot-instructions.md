# Instruções para Agentes de IA - Sistema de Apoio ao Recrutamento Inteligente

## Contexto Acadêmico

Este é um **projeto acadêmico** (UFAL, IA 2025.1) que usa **pair programming com LLM**. Todas as interações, decisões e código gerado devem ser **documentadas** para o relatório final. Antes de implementar, considere:

- Justifique escolhas arquiteturais e de design
- Documente prompts e respostas relevantes
- Sinalize sugestões que divergem do planejado
- Priorize clareza e explicabilidade sobre otimização prematura

## Arquitetura Modular Planejada

```
src/
  core/           # Candidate, JobProfile, Analyzer (classes centrais)
  parsing/        # Leitura e normalização de currículos
  skills/         # Extração hard/soft skills (regex, dicionários, LLM)
  scoring/        # ScoringEngine (pontuação configurável)
  llm/            # LLMClient (abstração genérica), prompts, RAG opcional
  explainability/ # ExplainabilityEngine (justificativas via LLM)
  ui/             # CLI simples
data/
  samples/        # job.txt, curriculo_*.txt (exemplos)
  config/         # skills.json, weights.json, prompt_templates.txt
```

### Componentes Principais

- **Analyzer**: orquestra coleta → análise → ranking
- **SkillExtractor**: identifica competências (técnicas e comportamentais) via método híbrido (regex + LLM)
- **ScoringEngine**: calcula aderência à vaga com pesos configuráveis
- **LLMClient**: interface unificada para Gemini/DeepSeek/Llama/Grok (provedores gratuitos)
- **ExplainabilityEngine**: produz justificativas compreensíveis ao RH
- **RAGPipeline** (placeholder): reservado para implementação futura de enriquecimento com docs externos

## Padrões de Desenvolvimento

### 1. Integração com LLMs
- Use abstrações genéricas (`LLMClient`) para trocar provedores facilmente
- **Provedores priorizados**: Gemini (Google AI Studio), DeepSeek, Llama, Grok (APIs gratuitas para uso acadêmico)
- Armazene prompts em `data/config/prompt_templates.txt` (não hardcode)
- Sempre inclua fallbacks para chamadas de API (rate limits, erros)
- Exemplo: `llm.call(prompt, model="gemini-pro", max_tokens=500)`
- Avalie qual provedor oferece melhor custo-benefício (qualidade vs. tokens gratuitos)

### 2. Configuração Externa
- Skills, pesos, mapeamentos → JSON em `data/config/`
- Chaves de API → `.env` (nunca commitar)
- Exemplo de peso: `{"python": 10, "comunicacao": 5}`

### 3. Comandos Essenciais

```bash
# Instalação
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt

# Execução principal
python src/main.py --job data/samples/job.txt --cvs data/samples/

# Testes (quando implementados)
pytest tests/ -v
```

### 4. Formato de Saída
Ranking final deve incluir:
- Posição, nome, pontuação total
- Hard skills identificadas
- Soft skills identificadas
- Justificativa explicável (gerada por LLM)

## Dependências Conhecidas

- `python-dotenv`: variáveis de ambiente
- `google-generativeai`: Gemini API (prioridade)
- `openai`: DeepSeek/Grok via endpoint compatível
- `numpy`, `pandas`: manipulação de dados
- `scikit-learn`: similaridade, vetorização (heurísticas)
- `PyPDF2` ou `pdfplumber`: extração de texto de PDFs (extensão futura)
- `tqdm`, `rich`: UI/UX no terminal

## Convenções do Projeto

### Nomes de Arquivos
- Currículos: `curriculo_01.txt`, `curriculo_02.txt` (foco inicial em `.txt`, suporte a `.pdf` opcional)
- Vaga: `job.txt` em `data/samples/`
- Configs: `skills.json`, `weights.json` em `data/config/`
- Prompts: `prompt_templates.txt` em `data/config/`

### Estrutura de Classes
- Classes em CamelCase (`SkillExtractor`, `ScoringEngine`)
- Métodos em snake_case (`extract_skills()`, `calculate_score()`)
- Atributos privados com `_` (`_llm_client`)

### Explicabilidade
- Toda decisão do sistema deve ser rastreável
- Use o LLM para gerar justificativas em linguagem natural
- Exemplo: "João tem forte experiência em Python (5 anos) e APIs REST, fundamentais para a vaga."

### Extração de Skills (Método Híbrido)
- **Hard skills**: regex + dicionário de tecnologias → validação via LLM se necessário
- **Soft skills**: análise semântica com LLM (detectar comunicação, liderança, adaptabilidade)
- Priorize eficiência: use LLM apenas quando heurísticas não forem suficientes

## Roadmap Atual

- [x] Definir arquitetura e estrutura
- [ ] Implementar `parsing/` (leitura de currículos `.txt`, PDF como extensão)
- [ ] Implementar `skills/` (extração híbrida: regex + LLM quando necessário)
- [ ] Implementar `scoring/` (pontuação configurável)
- [ ] Integrar `llm/` (Gemini/DeepSeek via APIs gratuitas)
- [ ] Implementar `explainability/` (justificativas)
- [ ] Criar CLI básico em `ui/`
- [ ] (Futuro) RAG para enriquecimento com docs externos

## Notas para o Agente

1. **Documente tudo**: este projeto será avaliado pela qualidade das interações com LLMs
2. **Seja explícito**: prefira código legível a otimizações obscuras
3. **Teste incrementalmente**: valide cada módulo antes de integrar
4. **Feedback loop**: espera-se análise crítica de decisões e sugestões do LLM
5. **Múltiplos LLMs**: compare respostas entre provedores quando relevante

## Informações da Equipe

- Prof. Dr. Evandro de Barros Costa (orientador)
- Eduardo Maciel, Josenilton Ferreira, Lucas Cassiano, Maria Letícia (desenvolvedores)
- Repositório: https://github.com/theduardomaciel/projeto-ia
