"""
API FastAPI para expor o pipeline de IA de recrutamento.

Módulo responsável por:
- Receber uploads de currículos e descrição de vaga
- Processar através do pipeline (parsing → skills → scoring → explainability)
- Retornar ranking de candidatos com justificativas
"""

from src.api.main import app

__all__ = ["app"]
