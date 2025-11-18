# Arquitetura do Sistema

## Visão Geral

Sistema modular para análise de currículos usando IA, desenvolvido com pair programming (LLM + desenvolvedores).

## Decisões Arquiteturais

### 1. Modularização por Responsabilidade

**Decisão**: Estrutura em módulos separados (core, parsing, skills, scoring, llm, explainability, ui)

**Justificativa**:
- **Testabilidade**: cada módulo pode ser testado isoladamente
- **Manutenibilidade**: mudanças em um módulo não afetam outros
- **Colaboração**: múltiplos desenvolvedores podem trabalhar em paralelo
- **Documentação**: responsabilidades claras facilitam o relatório acadêmico

**Trade-offs**:
- ✅ Maior clareza e organização
- ⚠️ Mais arquivos para gerenciar (aceitável para projeto acadêmico)

---

### 2. Abstração de LLM (LLMClient)

**Decisão**: Interface genérica para múltiplos provedores de LLM

**Justificativa**:
- **Flexibilidade**: trocar entre Gemini, DeepSeek, Grok sem reescrever código
- **Documentação**: comparar diferentes LLMs (requisito do relatório)
- **Resiliência**: fallback automático se um provedor falhar
- **Custos**: APIs gratuitas têm rate limits, múltiplos provedores aumentam disponibilidade

**Implementação planejada**:
```python
class LLMClient(ABC):
    @abstractmethod
    def call(self, prompt: str, **kwargs) -> str:
        pass

class GeminiClient(LLMClient):
    # Implementação específica do Gemini
    
class DeepSeekClient(LLMClient):
    # Implementação específica do DeepSeek
```

---

### 3. Configuração Externa (JSON)

**Decisão**: Skills, pesos, prompts em arquivos JSON/TXT separados

**Justificativa**:
- **Experimentação**: ajustar parâmetros sem recompilar
- **Versionamento**: git diff mostra claramente mudanças de configuração
- **Documentação**: configurações explícitas no relatório

**Estrutura**:
```
data/config/
  skills.json           # dicionário de hard skills conhecidas
  weights.json          # pesos para pontuação
  prompt_templates.txt  # prompts padronizados
```

---

### 4. Método Híbrido para Skills

**Decisão**: Combinar regex/dicionários + LLM para extração

**Justificativa**:
- **Eficiência**: regex é rápida para padrões conhecidos (Python, Java, SQL)
- **Precisão**: LLM para casos ambíguos ou contextuais
- **Custo**: minimizar chamadas de API (tokens)

**Fluxo**:
1. Regex detecta tecnologias explícitas
2. Dicionário valida variações (py → Python)
3. LLM analisa soft skills (comunicação, liderança)
4. LLM valida hard skills duvidosas

---

### 5. Explicabilidade via LLM

**Decisão**: Usar LLM para gerar justificativas, não apenas heurísticas

**Justificativa**:
- **Compreensibilidade**: linguagem natural para RH não-técnico
- **Contexto**: LLM pode relacionar experiências do candidato com a vaga
- **Demonstração**: mostra capacidade avançada de IA (objetivo acadêmico)

**Exemplo de prompt**:
> "Explique por que João Silva (5 anos Python, projetos REST API) é adequado para a vaga de Backend Developer (requisitos: Python, APIs, bancos de dados)"

---

## Fluxo de Dados

```
1. [CLI] Usuário fornece vaga + currículos
         ↓
2. [Parsing] Leitura de arquivos .txt
         ↓
3. [Skills] Extração híbrida (regex + LLM)
         ↓
4. [Scoring] Cálculo de aderência com pesos
         ↓
5. [Explainability] Geração de justificativas
         ↓
6. [UI] Exibição do ranking formatado
```

---

## Tecnologias Escolhidas

| Categoria | Tecnologia | Justificativa |
|-----------|-----------|---------------|
| Linguagem | Python 3.10+ | Type hints, dataclasses, ecossistema ML/IA |
| LLMs | Gemini (prioridade), Groq, OpenRouter | APIs gratuitas e acessíveis para uso acadêmico |
| Dados | JSON, TXT | Simplicidade, versionamento |
| CLI | rich, tqdm | UX profissional no terminal |
| Testes | pytest | Padrão da indústria |

---

## Módulo de Parsing

### Responsabilidades
- Carregar arquivos de vaga e currículos (`.txt`, futuro `.pdf`)
- Normalizar texto para facilitar extração de skills
- Inferir informações básicas (ex: nome do candidato)
- Registrar eventos de parsing para auditoria

### Componentes

#### FileLoader
Carrega arquivos com encoding robusto (UTF-8 + fallback Latin-1).

```python
loader = FileLoader()
job = loader.load_job("data/samples/job.txt")
candidates = loader.load_candidates("data/samples/")
```

**Decisões técnicas**:
- **Encoding adaptativo**: tenta UTF-8, fallback para Latin-1 (acentos brasileiros)
- **Inferência de nome**: heurística simples (2-5 tokens com iniciais maiúsculas, evita palavras técnicas)
- **Padrão de arquivo**: `curriculo_NN.txt` para ordenação automática
- **Logging**: cada arquivo registrado em `logs/parsing_events.log` com tamanho (bytes/chars)

#### TextNormalizer
Pipeline configurável de normalização de texto.

```python
normalizer = TextNormalizer(
    lower=True,           # lowercase
    remove_acc=True,      # remover acentos
    collapse_ws=True      # colapsar espaços múltiplos
)
normalized = normalizer.normalize(raw_text)
```

**Transformações aplicadas**:
1. **Lowercase**: "Python" → "python" (facilita matching regex)
2. **Remoção de acentos**: "Programação" → "programacao" (normalização NFD)
3. **Colapso de espaços**: "Python  Django" → "Python Django"

**Justificativa**:
- Aumenta recall de skills (case-insensitive)
- Simplifica regex (sem variações de acento)
- Preserva contexto (não remove stopwords)

#### ParserService
Orquestra loader + normalizer e retorna objetos estruturados.

```python
service = ParserService()
job, candidates = service.parse(job_path, cvs_dir)

# Cada candidato tem:
# - name: inferido ou fallback "Candidato NN"
# - raw_text: texto original
# - normalized_text: texto processado para extração
# - file_path: caminho do arquivo
```

### Modelo de Dados: Candidate

Campo `normalized_text` adicionado ao dataclass `Candidate` (em `src/core/models.py`):

```python
@dataclass
class Candidate:
    name: str
    raw_text: str
    normalized_text: Optional[str] = None  # <-- novo campo
    # ... outros campos
```

**Justificativa**: separar texto original (para display) do texto processado (para análise) mantém rastreabilidade.

### Stub para PDF

```python
loader.parse_pdf("curriculo.pdf")  # NotImplementedError
```

Sinaliza extensão futura sem bloquear implementação atual.

### Fluxo Completo de Parsing

```
[data/samples/job.txt] ──┐
                         ├─> FileLoader.load_job() ──> JobProfile
[data/samples/*.txt]  ───┘
                         ├─> FileLoader.load_candidates()
                         │       ↓
                         │   [raw_text]
                         │       ↓
                         └─> TextNormalizer.normalize()
                                 ↓
                             [normalized_text]
                                 ↓
                             Candidate objects
```

### Exemplo Real

**Input** (`curriculo_01.txt`):
```
João Silva
Email: joao.silva@email.com
...
Desenvolvedor Backend com 5 anos de experiência em Python...
```

**Output**:
```python
Candidate(
    name="João Silva",
    raw_text="João Silva\nEmail: joao.silva@email.com\n...",
    normalized_text="joao silva email: joao.silva@email.com ...",
    file_path="data/samples/curriculo_01.txt"
)
```

### Logs de Parsing

Arquivo: `logs/parsing_events.log`

Formato:
```
2025-11-18T02:45:12	file_read	path=data/samples/job.txt bytes=1234 chars=1200
2025-11-18T02:45:12	job_loaded	title=Desenvolvedor Backend Python - Pleno/Sênior
2025-11-18T02:45:12	file_read	path=data/samples/curriculo_01.txt bytes=2456 chars=2400
2025-11-18T02:45:12	candidate_loaded	name='João Silva' file=curriculo_01.txt
```

**Utilidade**: auditoria, troubleshooting, estatísticas para o relatório.

### Validação

CLI de teste:
```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/
```

Saída esperada:
```
Vaga:
  Título: Desenvolvedor Backend Python - Pleno/Sênior
  Arquivo: data\samples\job.txt

Candidatos carregados: 4
01. João Silva — arquivo=curriculo_01.txt
    preview: joao silva email: joao.silva@email.com | tel: (82) ...
```

---

## Módulo de Skills (Extração)

### Método Híbrido: Dicionário + Regex

**Decisão**: começar com abordagem determinística (regex + dicionários), adicionar LLM como fallback depois.

**Justificativa**:
- **Hard skills técnicas**: padrões previsíveis ("Python", "Docker", "PostgreSQL") → regex eficiente
- **Custo-benefício**: evita chamadas de API desnecessárias para termos óbvios
- **Transparência**: matching determinístico é mais fácil de auditar (importante para relatório)
- **LLM reservado para**: soft skills contextuais ("comunicação clara", "liderança em projetos") e validação de ambiguidades

### SkillExtractor

```python
extractor = SkillExtractor()
skills = extractor.extract_from_text(normalized_text)
# ou
extractor.extract_from_candidate(candidate)  # popula candidate.hard_skills e .soft_skills
```

**Algoritmo**:
1. **Carrega dicionários** de `data/config/skills.json` (hard_skills, soft_skills, synonyms)
2. **Compila regex** para cada termo + sinônimos (espaços flexíveis, limites de palavra)
3. **Busca no texto normalizado** e conta ocorrências
4. **Mapeia sinônimos → canônico** ("py" → "python", "postgres" → "postgresql")
5. **Retorna objetos Skill** com `name`, `category` (hard/soft), `confidence`, `source` (dictionary/synonym)

### Configuração: skills.json

```json
{
  "hard_skills": {
    "languages": ["python", "java", "javascript", ...],
    "frameworks": ["fastapi", "django", "flask", ...],
    "databases": ["postgresql", "mysql", "mongodb", ...],
    ...
  },
  "soft_skills": {
    "communication": ["comunicação", "comunicação clara", ...],
    "teamwork": ["trabalho em equipe", "colaboração", ...],
    ...
  },
  "synonyms": {
    "python": ["py", "python3"],
    "postgresql": ["postgres", "psql"],
    "docker": ["containers", "containerização"],
    ...
  }
}
```

**Design rationale**:
- **Categorias semânticas**: languages, frameworks, databases (facilita análise posterior)
- **Termos em lowercase**: matching case-insensitive (depende de normalização prévia)
- **Sinônimos explícitos**: captura variações comuns sem regex complexa

### Regex com Tolerância

```python
def _compile_pattern(term: str) -> re.Pattern:
    escaped = re.escape(term)
    escaped = escaped.replace("\\ ", r"\s+")  # espaços flexíveis
    pattern = rf"(?<!\w){escaped}(?!\w)"      # word boundaries
    return re.compile(pattern, re.IGNORECASE)
```

**Exemplos**:
- `"rest api"` → detecta "REST API", "rest   api", "restAPI" (com espaços variáveis)
- `"python"` → detecta "Python", mas não "pythonic" (word boundaries)
- `"c++"` → escapa caracteres especiais corretamente

### Modelo de Dados: Skill

```python
@dataclass
class Skill:
    name: str              # canônico: "python", "postgresql"
    category: str          # 'hard' ou 'soft'
    confidence: float      # 0.9 (dictionary) | 0.85 (synonym) | 0.7+ (LLM)
    source: str            # 'dictionary' | 'synonym' | 'llm'
    context: Optional[str] # snippet onde foi encontrada (futuro)
```

### Integração com Candidate

```python
candidate.add_skill(Skill("python", "hard", 0.9, "dictionary"))
# evita duplicatas automaticamente
```

### Exemplo Real

**Input** (normalizado):
```
desenvolvedor backend com 5 anos de experiencia em python, 
fastapi, postgresql. trabalho em equipe e comunicacao clara.
```

**Output**:
```python
[
  Skill(name="python", category="hard", confidence=0.9, source="dictionary"),
  Skill(name="fastapi", category="hard", confidence=0.9, source="dictionary"),
  Skill(name="postgresql", category="hard", confidence=0.9, source="dictionary"),
  Skill(name="trabalho em equipe", category="soft", confidence=0.9, source="dictionary"),
  Skill(name="comunicação", category="soft", confidence=0.85, source="synonym"),
]
```

### Logs de Extração

Arquivo: `logs/skill_events.log`

Formato:
```
2025-11-18T03:12:34	file=curriculo_01.txt	hard=[api,aws,django,docker,...]	soft=[adaptabilidade,proatividade]
```

### Validação CLI

```bash
python -m src.ui.main --job data/samples/job.txt --cvs data/samples/ --extract
```

Saída esperada:
```
Extraindo skills...
01. João Silva
    Hard skills: api, aws, django, docker, fastapi, git, python, postgresql, ...
    Soft skills: adaptabilidade, proatividade
```

### Limitações Conhecidas e Roadmap

**Atual (Dicionário + Regex)**:
- ✅ Detecta skills técnicas explícitas
- ✅ Alta precisão para termos conhecidos
- ⚠️ Não captura contexto (ex: "3 anos de Python" vs "cursinho de Python")
- ⚠️ Soft skills limitadas a termos exatos

**Próximas melhorias (LLM)**:
- Validar anos de experiência por skill
- Detectar soft skills implícitas ("liderou equipe de 5 pessoas" → liderança)
- Distinguir habilidades principais vs menções superficiais
- Enriquecer contexto (`context` field no dataclass `Skill`)

---

## Extensões Futuras (Planejadas)

- **RAGPipeline**: enriquecer análise com documentos externos (descrições de vagas, competências)
- **Suporte a PDF**: extração via PyPDF2/pdfplumber
- **Interface Web**: Flask/FastAPI para demonstração
- **Fairness Check**: detectar vieses no sistema
- **LLM para Skills Contextuais**: integrar chamadas de LLM para soft skills ambíguas e validação de experiência

---

## Registro de Interações com LLM

**Primeira interação** (18/11/2025):
- **Pergunta**: Como estruturar arquitetura modular para analisador de currículos?
- **Resposta**: Sugestão de separação clara entre parsing, skills, scoring, llm, explainability
- **Decisão**: Adotada integralmente - alinha com princípios SOLID e facilita documentação

**Nível de assistência**: Alto - estrutura clara e bem justificada
**Comparação de LLMs**: (a ser preenchido conforme desenvolvimento)
