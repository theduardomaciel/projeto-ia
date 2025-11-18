"""Módulo de parsing

Fornece utilidades para:
 - Carregar vaga e currículos (.txt)
 - Normalizar textos (lowercase, remover acentos, colapsar espaços)
 - Inferir nome do candidato
 - Registrar eventos de parsing

Extensível para suporte futuro a PDF.
"""

from .loader import FileLoader, TextNormalizer, ParserService
from .service import parse_all

__all__ = ["FileLoader", "TextNormalizer", "ParserService", "parse_all"]
