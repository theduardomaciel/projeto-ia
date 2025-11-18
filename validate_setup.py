"""
Script de validação rápida da configuração do sistema
Verifica dependências, API keys e funcionalidade básica do LLM
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Verifica se dependências críticas estão instaladas"""
    print("🔍 Verificando dependências...")

    deps = {
        "dotenv": "python-dotenv",
        "google.generativeai": "google-generativeai",
        "openai": "openai",
        "rich": "rich",
    }

    missing = []
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - FALTANDO")
            missing.append(package)

    if missing:
        print(f"\n⚠️ Instale dependências faltando: pip install {' '.join(missing)}")
        return False

    return True


def check_env_file():
    """Verifica se arquivo .env existe e tem conteúdo"""
    print("\n🔍 Verificando arquivo .env...")

    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print("  ❌ Arquivo .env não encontrado")
        print("  💡 Copie .env.example para .env e configure suas API keys")
        return False

    print("  ✅ Arquivo .env encontrado")

    # Carrega variáveis de ambiente
    from dotenv import load_dotenv

    load_dotenv()

    # Verifica API keys
    providers = {
        "Gemini": "GEMINI_API_KEY",
        "Groq": "GROQ_API_KEY",
        "OpenRouter": "OPENROUTER_API_KEY",
    }

    found_keys = []
    for name, var in providers.items():
        key = os.getenv(var)
        if key and key != f"your_{var.lower()}":
            print(f"  ✅ {name} API key configurada")
            found_keys.append(name)
        else:
            print(f"  ⚠️ {name} API key não configurada")

    if not found_keys:
        print("\n  ❌ Nenhuma API key válida encontrada")
        print("  💡 Configure pelo menos uma API key no arquivo .env")
        return False

    print(
        f"\n  ✅ {len(found_keys)} provedor(es) configurado(s): {', '.join(found_keys)}"
    )
    return True


def check_data_files():
    """Verifica se arquivos de configuração existem"""
    print("\n🔍 Verificando arquivos de configuração...")

    files = {
        "data/config/skills.json": "Dicionário de skills",
        "data/config/weights.json": "Pesos de pontuação",
        "data/config/prompt_templates.txt": "Templates de prompts",
        "data/samples/job.txt": "Exemplo de vaga",
        "data/samples/curriculo_01.txt": "Exemplo de currículo",
    }

    base_path = Path(__file__).parent
    all_exist = True

    for file, desc in files.items():
        path = base_path / file
        if path.exists():
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc} - {file}")
            all_exist = False

    return all_exist


def test_llm_basic():
    """Testa chamada básica ao LLM"""
    print("\n🔍 Testando integração com LLM...")

    try:
        from src.llm.client import get_default_llm

        print("  Criando cliente LLM...")
        llm = get_default_llm()
        print(f"  ✅ Cliente criado: {llm.__class__.__name__}")

        print("  Fazendo chamada de teste...")
        response = llm.call(
            "Responda apenas com a palavra 'OK'", temperature=0.3, max_tokens=10
        )

        if response.success:
            print(f"  ✅ Resposta recebida: {response.content[:50]}")
            print(f"  📊 Provider: {response.provider} | Model: {response.model}")
            print(
                f"  📊 Tokens: {response.tokens_used} | Latência: {response.latency:.2f}s"
            )
            return True
        else:
            print(f"  ❌ Erro na resposta: {response.error}")
            return False

    except Exception as e:
        print(f"  ❌ Erro ao testar LLM: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_prompt_manager():
    """Testa carregamento de templates"""
    print("\n🔍 Testando gerenciador de prompts...")

    try:
        from src.llm.prompts import get_prompt_manager

        pm = get_prompt_manager()
        templates = pm.list_templates()

        if templates:
            print(f"  ✅ {len(templates)} templates carregados")
            print(f"  📋 Exemplos: {', '.join(templates[:3])}...")
            return True
        else:
            print("  ⚠️ Nenhum template encontrado")
            return False

    except Exception as e:
        print(f"  ❌ Erro ao carregar templates: {e}")
        return False


def main():
    """Executa todos os checks"""
    print("=" * 60)
    print("🚀 VALIDAÇÃO DE CONFIGURAÇÃO DO SISTEMA")
    print("=" * 60)

    results = {
        "Dependências": check_dependencies(),
        "Arquivo .env": check_env_file(),
        "Arquivos de config": check_data_files(),
        "Integração LLM": False,
        "Templates de prompt": False,
    }

    # Só testa LLM se as dependências básicas estiverem OK
    if results["Dependências"] and results["Arquivo .env"]:
        results["Integração LLM"] = test_llm_basic()
        results["Templates de prompt"] = test_prompt_manager()

    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 60)

    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ SISTEMA PRONTO PARA USO!")
        print("=" * 60)
        print("\nPróximos passos:")
        print("1. Execute exemplos: python src/llm/examples.py")
        print("2. Continue desenvolvimento com parsing de currículos")
        print("3. Consulte QUICKSTART.md para mais detalhes")
    else:
        print("⚠️ ALGUNS PROBLEMAS ENCONTRADOS")
        print("=" * 60)
        print("\nResolva os itens marcados com ❌ antes de continuar")
        print("Consulte QUICKSTART.md para instruções detalhadas")

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Validação interrompida pelo usuário")
        sys.exit(1)
