# 🚀 Guia Rápido de Configuração e Teste

## 1. Configuração Inicial

### Instalar Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```

### Configurar API Keys

Escolha **pelo menos um** provedor de LLM:

#### Opção A: Google Gemini (Recomendado - Gratuito)

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Get API Key" → "Create API Key"
4. Copie a chave gerada

#### Opção B: DeepSeek (Alternativa gratuita)

1. Acesse: https://platform.deepseek.com/
2. Crie uma conta
3. Vá em "API Keys" e gere uma nova chave

#### Opção C: Grok/xAI

1. Acesse: https://x.ai/
2. Cadastre-se para acesso à API
3. Gere uma API key

### Criar arquivo .env

```bash
# Copie o template
cp .env.example .env

# Edite o arquivo .env e adicione sua(s) chave(s)
```

Exemplo de `.env` configurado:

```env
# Google Gemini (prioridade - API gratuita)
GEMINI_API_KEY=AIzaSy...sua_chave_aqui

# Configurações do sistema
DEFAULT_LLM_PROVIDER=gemini
MAX_TOKENS=1000
TEMPERATURE=0.7
```

---

## 2. Testar Integração com LLM

### Teste Básico (Verificar se funciona)

```bash
# Execute o script de exemplos
python src/llm/examples.py
```

**Saída esperada:**
```
🚀 Exemplos de uso do módulo LLM
============================================================

Exemplo 1: Chamada básica
============================================================

✅ Resposta (gemini/gemini-1.5-flash):
Pair programming é uma técnica ágil onde dois desenvolvedores trabalham 
juntos em um único computador...

Tokens usados: 87
Latência: 1.23s
```

### Teste Individual por Provedor

```python
# Crie um arquivo test_llm.py
from dotenv import load_dotenv
load_dotenv()

from src.llm.client import LLMFactory

# Teste Gemini
try:
    llm = LLMFactory.create("gemini")
    response = llm.call("Diga olá!", max_tokens=50)
    print(f"✅ Gemini funcionando: {response.content}")
except Exception as e:
    print(f"❌ Gemini falhou: {e}")

# Teste DeepSeek
try:
    llm = LLMFactory.create("deepseek")
    response = llm.call("Diga olá!", max_tokens=50)
    print(f"✅ DeepSeek funcionando: {response.content}")
except Exception as e:
    print(f"❌ DeepSeek falhou: {e}")
```

---

## 3. Validar Templates de Prompt

```python
from src.llm.prompts import get_prompt_manager

pm = get_prompt_manager()

# Lista templates disponíveis
print("Templates disponíveis:")
for template in pm.list_templates():
    print(f"  - {template}")

# Testa um template
prompt = pm.get(
    "extração de soft skills",
    resume_text="João é comunicativo e trabalha bem em equipe."
)
print("\nPrompt formatado:")
print(prompt[:200] + "...")
```

---

## 4. Testar Logging de Interações

```python
from src.llm.client import get_default_llm
from src.llm.utils import get_llm_logger

llm = get_default_llm()
logger = get_llm_logger()

# Faz uma chamada
response = llm.call("Liste 3 linguagens de programação")

# Registra
logger.log_interaction(
    prompt="Liste 3 linguagens de programação",
    response=response.content,
    provider=response.provider,
    model=response.model,
    purpose="teste",
    tokens_used=response.tokens_used,
    latency=response.latency
)

# Ver estatísticas
stats = logger.get_session_stats()
print(f"Total de chamadas: {stats['total_calls']}")
print(f"Tokens usados: {stats['total_tokens']}")

# Logs salvos em: logs/llm_session_YYYYMMDD_HHMMSS.jsonl
```

---

## 5. Comparação entre Provedores (Documentação do Relatório)

Este teste é importante para o relatório acadêmico:

```python
from src.llm.client import LLMFactory
import time

prompt = "Explique o que é CI/CD em 2 frases."

provedores = ["gemini", "deepseek", "grok"]
resultados = []

for provider in provedores:
    try:
        llm = LLMFactory.create(provider)
        
        start = time.time()
        response = llm.call(prompt, temperature=0.7, max_tokens=200)
        
        if response.success:
            resultados.append({
                "provider": provider,
                "resposta": response.content,
                "tokens": response.tokens_used,
                "latencia": response.latency,
                "qualidade": "✅"  # Avaliar manualmente
            })
    except Exception as e:
        print(f"⚠️ {provider} indisponível: {e}")

# Comparar resultados
for r in resultados:
    print(f"\n{'='*60}")
    print(f"Provedor: {r['provider'].upper()}")
    print(f"Resposta: {r['resposta']}")
    print(f"Tokens: {r['tokens']} | Latência: {r['latencia']:.2f}s")
```

---

## 6. Troubleshooting

### Erro: "API key não encontrada"

```bash
# Verifique se o arquivo .env existe
ls .env

# Verifique o conteúdo (sem expor a chave completa)
cat .env | grep API_KEY

# Se estiver vazio, edite:
nano .env  # ou code .env
```

### Erro: "google-generativeai não instalado"

```bash
# Reinstale as dependências
pip install -r requirements.txt

# Ou instale individualmente
pip install google-generativeai
```

### Erro: Rate limit exceeded

- **Solução**: Configure múltiplos provedores para fallback automático
- Gemini gratuito: ~15 requests/minuto
- Adicione delays entre chamadas se necessário

### Erro: JSON inválido na resposta

- **Causa**: LLM retornou texto fora do formato JSON esperado
- **Solução**: Use temperatura mais baixa (0.2-0.3) para respostas estruturadas
- O parser já tenta extrair JSON de texto com markdown

---

## 7. Próximos Passos no Desenvolvimento

Após validar o módulo LLM, continue com:

1. **Módulo de Parsing** (`src/parsing/`)
   - Leitura de currículos `.txt`
   - Extração de blocos (experiência, formação, etc)

2. **SkillExtractor** (`src/skills/`)
   - Extração híbrida: regex + LLM
   - Validação de hard skills
   - Análise de soft skills

3. **ScoringEngine** (`src/scoring/`)
   - Cálculo de pontuação com pesos
   - Ranking de candidatos

4. **ExplainabilityEngine** (`src/explainability/`)
   - Geração de justificativas via LLM

5. **CLI** (`src/main.py`)
   - Interface completa
   - Orquestração de todo o pipeline

---

## 8. Checklist de Validação

- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip list` mostra `google-generativeai`)
- [ ] Arquivo `.env` criado com pelo menos uma API key
- [ ] Teste básico executado com sucesso (`python src/llm/examples.py`)
- [ ] Pelo menos um provedor funcionando
- [ ] Templates de prompt carregando corretamente
- [ ] Logs sendo salvos em `logs/`
- [ ] Comparação entre provedores testada (para relatório)

---

## 9. Documentação para o Relatório

**Registre estas informações:**

### Interação 1: Configuração inicial do módulo LLM
- **Pergunta**: Como integrar múltiplos provedores LLM mantendo código desacoplado?
- **Resposta do LLM**: Sugestão de usar padrão Abstract Factory com interface `LLMClient`
- **Decisão**: Adotada - permite trocar provedores sem reescrever código
- **Resultado**: Implementação bem-sucedida com Gemini, DeepSeek, Grok

### Interação 2: Tratamento de respostas JSON
- **Problema**: LLMs às vezes retornam JSON dentro de markdown (```json)
- **Solução do LLM**: Parser robusto que tenta múltiplas estratégias
- **Implementação**: Método `_parse_json_response()` com fallbacks
- **Eficácia**: ✅ Alta - funciona com diferentes formatos de resposta

### Comparação de Provedores (preencher após testes)

| Provedor | Latência Média | Qualidade das Respostas | Rate Limit | Custo |
|----------|---------------|------------------------|------------|-------|
| Gemini   | X.XXs        | [avaliar]              | ~15/min    | Grátis|
| DeepSeek | X.XXs        | [avaliar]              | [testar]   | Grátis|
| Grok     | X.XXs        | [avaliar]              | [testar]   | ?     |

---

## Suporte

Em caso de dúvidas ou problemas:
1. Verifique os logs em `logs/llm_session_*.jsonl`
2. Consulte a documentação em `docs/ARCHITECTURE.md`
3. Execute os exemplos em `src/llm/examples.py` para debugging
