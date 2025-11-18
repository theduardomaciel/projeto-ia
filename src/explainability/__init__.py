"""Módulo explainability: Geração de justificativas
- ExplainabilityEngine: usa LLM para criar explicações compreensíveis
- Justificativas para decisões do sistema
"""

from .engine import ExplainabilityEngine

__all__ = ["ExplainabilityEngine"]
