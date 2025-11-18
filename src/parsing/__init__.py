"""Módulo de parsing

Fornece utilidades para:
 - Carregar vaga e currículos (.txt, .pdf, .docx)
 - Normalizar textos (lowercase, remover acentos, colapsar espaços)
 - Inferir nome do candidato
 - Registrar eventos de parsing
"""

from .document_extractor import DocumentExtractor
from .loader import FileLoader, TextNormalizer, ParserService
from .service import parse_all

__all__ = [
	"DocumentExtractor",
	"FileLoader",
	"TextNormalizer",
	"ParserService",
	"parse_all",
]
