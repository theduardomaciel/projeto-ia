# 🤖 Provedores de LLM - Guia de Configuração

## Provedores Suportados

O sistema suporta **3 provedores gratuitos e acessíveis**:

### 1. **Google Gemini** (Recomendado)
- ✅ **Totalmente gratuito**
- ✅ Rate limit generoso (~60 requests/minuto)
- ✅ Modelos de alta qualidade
- ✅ Fácil configuração

**Como obter:**
1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Get API Key" → "Create API Key"
4. Copie e adicione ao `.env`: `GEMINI_API_KEY=sua_chave_aqui`

**Modelos disponíveis:**
- `gemini-1.5-flash` (padrão) - rápido e eficiente
- `gemini-1.5-pro` - mais poderoso, melhor para tarefas complexas
- `gemini-2.0-flash-exp` - experimental, mais recente

---

### 2. **Groq** (Agregador)
- ✅ **Gratuito** (tier inicial)
- ✅ **Muito rápido** (inferência otimizada)
- ✅ Múltiplos modelos open-source
- ⚠️ Rate limits menores que Gemini

**Como obter:**
1. Acesse: https://console.groq.com/keys
2. Crie uma conta (email ou GitHub)
3. Vá em "API Keys" → "Create API Key"
4. Copie e adicione ao `.env`: `GROQ_API_KEY=sua_chave_aqui`

**Modelos disponíveis:**
- `llama-3.1-70b-versatile` (padrão) - melhor custo-benefício
- `llama-3.1-8b-instant` - mais rápido
- `mixtral-8x7b-32768` - contexto longo
- `gemma-7b-it` - menor, mais rápido

**Rate limits (tier gratuito):**
- ~30 requests/minuto
- ~6.000 tokens/minuto

---

### 3. **OpenRouter** (Agregador)
- ✅ Tier gratuito disponível
- ✅ Acesso a múltiplos modelos
- ✅ Fallback automático entre modelos
- ⚠️ Modelos gratuitos têm rate limits

**Como obter:**
1. Acesse: https://openrouter.ai/keys
2. Crie uma conta
3. Vá em "Keys" → "Create Key"
4. Copie e adicione ao `.env`: `OPENROUTER_API_KEY=sua_chave_aqui`

**Modelos gratuitos disponíveis:**
- `google/gemma-2-9b-it:free` (padrão)
- `meta-llama/llama-3-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`
- `huggingfaceh4/zephyr-7b-beta:free`

**Rate limits (tier gratuito):**
- Varia por modelo (~10-20 requests/minuto)
- Tokens limitados por dia

---

## Comparação de Provedores

| Provedor | Gratuito | Velocidade | Qualidade | Rate Limit | Recomendação |
|----------|----------|-----------|-----------|------------|--------------|
| **Gemini** | ✅ Sim | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Alto | ✅ **Primeira escolha** |
| **Groq** | ✅ Sim | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Médio | ✅ Ótimo para produção |
| **OpenRouter** | ✅ Sim* | ⭐⭐⭐ | ⭐⭐⭐ | Baixo | ⚠️ Backup/testes |

*Modelos específicos gratuitos, com limitações

---

## Configuração Recomendada

### Para Desenvolvimento (Uso Intenso)

```env
# Configure múltiplos provedores para fallback
GEMINI_API_KEY=sua_chave_gemini
GROQ_API_KEY=sua_chave_groq
OPENROUTER_API_KEY=sua_chave_openrouter

DEFAULT_LLM_PROVIDER=gemini
```

### Para Produção (Alta Velocidade)

```env
# Priorize Groq para inferência rápida
GROQ_API_KEY=sua_chave_groq
GEMINI_API_KEY=sua_chave_gemini  # Fallback

DEFAULT_LLM_PROVIDER=groq
```

### Para Testes (Mínimo)

```env
# Apenas Gemini é suficiente
GEMINI_API_KEY=sua_chave_gemini
DEFAULT_LLM_PROVIDER=gemini
```

---

## Uso no Código

### Provedor Padrão (Automático)

```python
from src.llm.client import get_default_llm

# Usa provedor configurado em DEFAULT_LLM_PROVIDER
# Com fallback automático se falhar
llm = get_default_llm()
response = llm.call("Seu prompt aqui")
```

### Provedor Específico

```python
from src.llm.client import LLMFactory

# Força uso do Gemini
llm = LLMFactory.create("gemini")

# Força uso do Groq com modelo específico
llm = LLMFactory.create("groq", model="llama-3.1-8b-instant")

# Força uso do OpenRouter
llm = LLMFactory.create("openrouter", model="meta-llama/llama-3-8b-instruct:free")
```

### Comparação Entre Provedores

```python
from src.llm.client import LLMFactory

prompt = "Explique CI/CD em 2 frases"

for provider in ["gemini", "groq", "openrouter"]:
    try:
        llm = LLMFactory.create(provider)
        response = llm.call(prompt, max_tokens=200)
        
        print(f"{provider}: {response.content}")
        print(f"  Latência: {response.latency:.2f}s")
        print(f"  Tokens: {response.tokens_used}")
    except Exception as e:
        print(f"{provider}: Erro - {e}")
```

---

## Troubleshooting

### Erro: "API key não encontrada"
- Verifique se o arquivo `.env` existe e está na raiz do projeto
- Confirme que a variável está escrita corretamente (ex: `GEMINI_API_KEY`)
- Não deixe espaços: `GEMINI_API_KEY=suachave` ✅ vs `GEMINI_API_KEY = suachave` ❌

### Erro: "Rate limit exceeded"
- **Gemini**: Aguarde ~1 minuto (60 req/min)
- **Groq**: Aguarde ~2 minutos (30 req/min)
- **Solução**: Configure múltiplos provedores para fallback automático

### Erro: "Model not found"
- Verifique se o modelo está disponível no tier gratuito
- Groq: use modelos listados acima
- OpenRouter: use apenas modelos com `:free`

### Resposta muito lenta
- **Gemini**: Normal, ~1-3s
- **Groq**: Deve ser <1s (mais rápido)
- **OpenRouter**: Varia, ~2-5s
- **Solução**: Priorize Groq para velocidade

---

## Migração de Provedores Antigos

Se você estava usando **DeepSeek** ou **Grok (xAI)**:

### DeepSeek → Groq
```diff
- DEEPSEEK_API_KEY=...
- DEFAULT_LLM_PROVIDER=deepseek
+ GROQ_API_KEY=...
+ DEFAULT_LLM_PROVIDER=groq
```

### Grok (xAI) → OpenRouter
```diff
- GROK_API_KEY=...
- DEFAULT_LLM_PROVIDER=grok
+ OPENROUTER_API_KEY=...
+ DEFAULT_LLM_PROVIDER=openrouter
```

**Motivo da mudança:**
- DeepSeek: Acesso gratuito descontinuado/limitado
- Grok (xAI): Sem tier gratuito acessível no momento
- Groq/OpenRouter: Alternativas gratuitas e estáveis

---

## Recomendações para o Projeto Acadêmico

### 1. Configure pelo menos 2 provedores
```env
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

**Por quê?**
- Comparação de respostas (requisito do relatório)
- Resiliência se um provedor cair
- Bypass de rate limits

### 2. Use Gemini como padrão
```env
DEFAULT_LLM_PROVIDER=gemini
```

**Por quê?**
- Melhor qualidade geral
- Rate limits mais generosos
- Gratuito sem preocupações

### 3. Documente as diferenças
Para o relatório, compare:
- Qualidade das respostas (soft skills, justificativas)
- Velocidade de inferência
- Rate limits atingidos
- Facilidade de configuração

---

## Recursos Adicionais

- **Gemini Docs**: https://ai.google.dev/docs
- **Groq Docs**: https://console.groq.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Código de exemplo**: `src/llm/examples.py`
- **Validação de setup**: `python validate_setup.py`
