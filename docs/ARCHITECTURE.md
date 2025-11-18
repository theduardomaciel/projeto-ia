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
| LLMs | Gemini (prioridade), DeepSeek, Grok | APIs gratuitas para uso acadêmico |
| Dados | JSON, TXT | Simplicidade, versionamento |
| CLI | rich, tqdm | UX profissional no terminal |
| Testes | pytest | Padrão da indústria |

---

## Extensões Futuras (Planejadas)

- **RAGPipeline**: enriquecer análise com documentos externos (descrições de vagas, competências)
- **Suporte a PDF**: extração via PyPDF2/pdfplumber
- **Interface Web**: Flask/FastAPI para demonstração
- **Fairness Check**: detectar vieses no sistema

---

## Registro de Interações com LLM

**Primeira interação** (18/11/2025):
- **Pergunta**: Como estruturar arquitetura modular para analisador de currículos?
- **Resposta**: Sugestão de separação clara entre parsing, skills, scoring, llm, explainability
- **Decisão**: Adotada integralmente - alinha com princípios SOLID e facilita documentação

**Nível de assistência**: Alto - estrutura clara e bem justificada
**Comparação de LLMs**: (a ser preenchido conforme desenvolvimento)
