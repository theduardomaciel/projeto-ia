"""Extração de requisitos de vagas.

Analisa texto da vaga e identifica:
- Requisitos obrigatórios (required)
- Requisitos desejáveis (preferred)
- Nice to have
- Hard skills vs soft skills
"""

from __future__ import annotations

import re
from typing import List, Dict, Tuple
from pathlib import Path

from src.core.models import JobProfile, JobRequirement
from src.core.config import load_skills


class RequirementsExtractor:
    """Extrai requisitos estruturados de descrições de vaga."""

    def __init__(self, skills_config: Dict | None = None) -> None:
        """Inicializa extrator com configuração de skills.

        Args:
            skills_config: Config com listas de hard_skills e soft_skills
        """
        self.config = skills_config or load_skills()

        # Carregar skills conhecidas (skills.json tem estrutura aninhada)
        self.known_hard_skills = set()
        hard_skills_dict = self.config.get("hard_skills", {})
        if isinstance(hard_skills_dict, dict):
            for category, skills in hard_skills_dict.items():
                self.known_hard_skills.update(s.lower() for s in skills)

        self.known_soft_skills = set(
            s.lower() for s in self.config.get("soft_skills", [])
        )

        # Padrões de seções
        self.section_patterns = {
            "required": re.compile(
                r"requisitos?\s+(obrigat[oó]rios?|essenciais?|necess[aá]rios?)",
                re.IGNORECASE,
            ),
            "preferred": re.compile(
                r"requisitos?\s+(desej[aá]veis?|preferenciais?)", re.IGNORECASE
            ),
            "nice_to_have": re.compile(
                r"(diferenciais?|nice\s+to\s+have|seria\s+um\s+plus)", re.IGNORECASE
            ),
        }

    def extract_from_job(self, job: JobProfile) -> JobProfile:
        """Extrai requisitos do texto da vaga e popula job.requirements.

        Args:
            job: JobProfile com raw_text preenchido

        Returns:
            JobProfile com requirements populado
        """
        text = job.raw_text

        # Identificar seções
        sections = self._identify_sections(text)

        # Extrair requisitos de cada seção
        for importance, section_text in sections.items():
            requirements = self._extract_requirements_from_section(
                section_text, importance
            )
            job.requirements.extend(requirements)

        return job

    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identifica e extrai seções de requisitos do texto.

        Returns:
            Dict mapeando importance -> texto da seção
        """
        sections = {}
        lines = text.split("\n")

        current_section = None
        current_lines = []

        for line in lines:
            # Verificar se linha inicia nova seção
            matched = False
            for importance, pattern in self.section_patterns.items():
                if pattern.search(line):
                    # Salvar seção anterior
                    if current_section and current_lines:
                        sections[current_section] = "\n".join(current_lines)

                    # Iniciar nova seção
                    current_section = importance
                    current_lines = []
                    matched = True
                    break

            if not matched and current_section:
                current_lines.append(line)

        # Salvar última seção
        if current_section and current_lines:
            sections[current_section] = "\n".join(current_lines)

        return sections

    def _extract_requirements_from_section(
        self, section_text: str, importance: str
    ) -> List[JobRequirement]:
        """Extrai skills individuais de uma seção.

        Args:
            section_text: Texto da seção
            importance: 'required', 'preferred', ou 'nice_to_have'

        Returns:
            Lista de JobRequirement
        """
        requirements = []

        # Normalizar texto
        text_lower = section_text.lower()

        # Buscar hard skills conhecidas
        for skill in self.known_hard_skills:
            # Buscar skill como palavra completa ou em contexto
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                req = JobRequirement(
                    skill=skill, importance=importance, weight=1.0, category="hard"
                )
                requirements.append(req)

        # Buscar soft skills conhecidas
        for skill in self.known_soft_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                req = JobRequirement(
                    skill=skill, importance=importance, weight=1.0, category="soft"
                )
                requirements.append(req)

        return requirements

    def get_requirements_summary(self, job: JobProfile) -> Dict:
        """Gera resumo dos requisitos extraídos.

        Returns:
            Dict com estatísticas dos requisitos
        """
        if not job.requirements:
            return {"total": 0, "by_importance": {}, "by_category": {}}

        by_importance = {}
        by_category = {}

        for req in job.requirements:
            # Contar por importance
            by_importance[req.importance] = by_importance.get(req.importance, 0) + 1

            # Contar por category
            by_category[req.category] = by_category.get(req.category, 0) + 1

        return {
            "total": len(job.requirements),
            "by_importance": by_importance,
            "by_category": by_category,
            "required_skills": job.get_required_skills(),
            "preferred_skills": job.get_preferred_skills(),
        }
