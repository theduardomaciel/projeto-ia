#!/usr/bin/env python3
"""
Script de inicialização do servidor API.

Uso:
    python run_api.py

    ou com opções:
    python run_api.py --host 0.0.0.0 --port 8000 --reload
"""

import argparse
import sys
from pathlib import Path

# Adicionar diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    parser = argparse.ArgumentParser(
        description="Inicia o servidor FastAPI do sistema de recrutamento"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host para bind do servidor (padrão: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Porta do servidor (padrão: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Habilitar auto-reload em desenvolvimento",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Nível de log (padrão: info)",
    )

    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("❌ Erro: uvicorn não está instalado.")
        print("   Instale as dependências: pip install -r requirements.txt")
        sys.exit(1)

    print("=" * 60)
    print("🚀 Sistema de Apoio ao Recrutamento Inteligente - API")
    print("=" * 60)
    print(f"📍 Servidor: http://{args.host}:{args.port}")
    print(f"📖 Documentação: http://localhost:{args.port}/docs")
    print(f"🔧 Auto-reload: {'✓ Ativado' if args.reload else '✗ Desativado'}")
    print("=" * 60)
    print()

    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
