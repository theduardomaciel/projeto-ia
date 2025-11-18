"""
Exemplo de uso do módulo LLM
Demonstra como utilizar os diferentes clientes
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.client import LLMFactory, get_default_llm, LLMResponse
from llm.prompts import get_prompt_manager, get_prompt
from llm.utils import get_llm_logger, retry_on_failure


def example_basic_call():
    """Exemplo 1: Chamada básica ao LLM"""
    print("=" * 60)
    print("Exemplo 1: Chamada básica")
    print("=" * 60)

    # Cria cliente Gemini
    try:
        llm = LLMFactory.create("gemini")

        prompt = "Explique em 2 frases o que é pair programming."
        response = llm.call(prompt, temperature=0.7, max_tokens=200)

        if response.success:
            print(f"\n✅ Resposta ({response.provider}/{response.model}):")
            print(response.content)
            print(f"\nTokens usados: {response.tokens_used}")
            print(f"Latência: {response.latency:.2f}s")
        else:
            print(f"❌ Erro: {response.error}")

    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")


def example_json_response():
    """Exemplo 2: Resposta em JSON estruturado"""
    print("\n" + "=" * 60)
    print("Exemplo 2: Resposta JSON estruturada")
    print("=" * 60)

    try:
        llm = get_default_llm()

        prompt = """
Extraia as seguintes informações do texto:

Texto: "João Silva é desenvolvedor Python há 5 anos. Tem experiência com Django e FastAPI."

Retorne em JSON com esta estrutura:
{
    "name": "nome da pessoa",
    "years_experience": número de anos,
    "technologies": ["lista", "de", "tecnologias"]
}
"""

        result = llm.call_json(prompt, temperature=0.3, max_tokens=300)

        print("\n✅ JSON parseado:")
        import json

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Erro: {e}")


def example_with_template():
    """Exemplo 3: Uso de templates de prompt"""
    print("\n" + "=" * 60)
    print("Exemplo 3: Uso de prompt templates")
    print("=" * 60)

    try:
        llm = get_default_llm()
        pm = get_prompt_manager()

        # Lista templates disponíveis
        print("\nTemplates disponíveis:")
        for template in pm.list_templates():
            print(f"  - {template}")

        # Usa template de extração de contato
        resume_text = """
João Silva
Email: joao@example.com
Tel: (11) 98765-4321
GitHub: github.com/joaosilva
"""

        prompt = get_prompt(
            "extração de informações de contato", resume_text=resume_text
        )

        result = llm.call_json(prompt, temperature=0.2)

        print("\n✅ Informações extraídas:")
        import json

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Erro: {e}")


def example_with_logging():
    """Exemplo 4: Logging de interações"""
    print("\n" + "=" * 60)
    print("Exemplo 4: Logging de interações")
    print("=" * 60)

    try:
        llm = get_default_llm()
        logger = get_llm_logger()

        prompt = "Liste 3 soft skills importantes para desenvolvedores."
        response = llm.call(prompt, temperature=0.7, max_tokens=200)

        # Registra interação
        logger.log_interaction(
            prompt=prompt,
            response=response.content,
            provider=response.provider,
            model=response.model,
            purpose="teste de logging",
            tokens_used=response.tokens_used,
            latency=response.latency,
            success=response.success,
            error=response.error,
        )

        if response.success:
            print(f"\n✅ Resposta:")
            print(response.content)

        # Mostra estatísticas
        stats = logger.get_session_stats()
        print(f"\n📊 Estatísticas da sessão:")
        print(f"  Total de chamadas: {stats['total_calls']}")
        print(f"  Bem-sucedidas: {stats['successful_calls']}")
        print(f"  Tokens totais: {stats['total_tokens']}")
        print(f"  Latência média: {stats['avg_latency']:.2f}s")
        print(f"\n📝 Logs salvos em: {logger.session_file}")

    except Exception as e:
        print(f"❌ Erro: {e}")


@retry_on_failure(max_retries=3, delay=1.0)
def example_with_retry():
    """Exemplo 5: Retry automático"""
    print("\n" + "=" * 60)
    print("Exemplo 5: Retry automático em falhas")
    print("=" * 60)

    llm = get_default_llm()

    prompt = "Diga olá em 3 idiomas diferentes."
    response = llm.call(prompt, max_tokens=100)

    if response.success:
        print(f"\n✅ Resposta:")
        print(response.content)
    else:
        raise RuntimeError(f"Falha após retries: {response.error}")


def example_compare_providers():
    """Exemplo 6: Comparação entre provedores"""
    print("\n" + "=" * 60)
    print("Exemplo 6: Comparação entre provedores")
    print("=" * 60)

    prompt = "Explique em uma frase o que é CI/CD."

    providers = ["gemini", "groq", "openrouter"]

    for provider in providers:
        try:
            print(f"\n🔍 Testando {provider.upper()}...")
            llm = LLMFactory.create(provider)
            response = llm.call(prompt, temperature=0.7, max_tokens=100)

            if response.success:
                print(f"✅ {provider}: {response.content[:100]}...")
                print(
                    f"   Latência: {response.latency:.2f}s | Tokens: {response.tokens_used}"
                )
            else:
                print(f"❌ {provider}: {response.error}")

        except Exception as e:
            print(f"⚠️ {provider} não disponível: {e}")


def main():
    """Executa todos os exemplos"""
    print("\n🚀 Exemplos de uso do módulo LLM")
    print("=" * 60)

    # Carrega variáveis de ambiente
    from dotenv import load_dotenv

    load_dotenv()

    # Verifica se há API keys configuradas
    if (
        not os.getenv("GEMINI_API_KEY")
        and not os.getenv("GROQ_API_KEY")
        and not os.getenv("OPENROUTER_API_KEY")
    ):
        print("\n⚠️ AVISO: Nenhuma API key configurada!")
        print("Configure pelo menos uma das seguintes variáveis de ambiente:")
        print("  - GEMINI_API_KEY (https://aistudio.google.com/app/apikey)")
        print("  - GROQ_API_KEY (https://console.groq.com/keys)")
        print("  - OPENROUTER_API_KEY (https://openrouter.ai/keys)")
        print("\nOu crie um arquivo .env na raiz do projeto.")
        return

    try:
        example_basic_call()
        example_json_response()
        example_with_template()
        example_with_logging()
        example_with_retry()
        example_compare_providers()

    except KeyboardInterrupt:
        print("\n\n❌ Execução interrompida pelo usuário")


if __name__ == "__main__":
    main()
