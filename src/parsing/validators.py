"""Validadores para garantir qualidade dos dados extraídos.

Responsabilidades:
 - Validar formato de currículos
 - Checar completude de informações críticas
 - Detectar anomalias nos dados extraídos
 - Fornecer scores de confiança
"""

from __future__ import annotations

from typing import List, Dict, Optional
from dataclasses import dataclass

from src.core.models import Candidate, Experience, Education


@dataclass
class ValidationResult:
    """Resultado da validação de um candidato."""

    is_valid: bool
    confidence_score: float  # 0.0 a 1.0
    warnings: List[str]
    errors: List[str]
    suggestions: List[str]


class CandidateValidator:
    """Valida e avalia qualidade dos dados de candidatos."""

    # Limites de confiança
    MIN_TEXT_LENGTH = 100  # Currículo muito curto
    MAX_TEXT_LENGTH = 50000  # Currículo excessivamente longo
    MIN_SKILLS = 2  # Mínimo de skills para considerar válido

    def validate_candidate(self, candidate: Candidate) -> ValidationResult:
        """Valida um candidato completo."""
        warnings = []
        errors = []
        suggestions = []
        confidence = 1.0

        # 1. Validar texto base
        text_length = len(candidate.raw_text)
        if text_length < self.MIN_TEXT_LENGTH:
            errors.append(f"Currículo muito curto ({text_length} chars)")
            confidence *= 0.3
        elif text_length > self.MAX_TEXT_LENGTH:
            warnings.append(f"Currículo muito longo ({text_length} chars)")
            confidence *= 0.9

        # 2. Validar nome
        if not candidate.name or candidate.name.startswith("Candidato"):
            warnings.append("Nome do candidato não identificado (usando fallback)")
            confidence *= 0.95

        # 3. Validar skills
        total_skills = len(candidate.hard_skills) + len(candidate.soft_skills)
        if total_skills < self.MIN_SKILLS:
            errors.append(f"Poucas skills identificadas ({total_skills})")
            suggestions.append("Considerar usar LLM para extração de skills")
            confidence *= 0.5
        elif total_skills == 0:
            errors.append("Nenhuma skill identificada")
            confidence *= 0.2

        # 4. Validar experiência
        exp_result = self._validate_experiences(candidate.experiences)
        warnings.extend(exp_result["warnings"])
        suggestions.extend(exp_result["suggestions"])
        confidence *= exp_result["confidence_factor"]

        # 5. Validar educação
        edu_result = self._validate_education(candidate.education)
        warnings.extend(edu_result["warnings"])
        suggestions.extend(edu_result["suggestions"])
        confidence *= edu_result["confidence_factor"]

        # 6. Validar informações de contato
        if not candidate.email and not candidate.contact:
            warnings.append("Informações de contato não encontradas")
            confidence *= 0.95

        # Determinar se é válido
        is_valid = len(errors) == 0 and confidence > 0.3

        return ValidationResult(
            is_valid=is_valid,
            confidence_score=round(confidence, 2),
            warnings=warnings,
            errors=errors,
            suggestions=suggestions,
        )

    def _validate_experiences(self, experiences: List[Experience]) -> Dict:
        """Valida lista de experiências."""
        warnings = []
        suggestions = []
        confidence_factor = 1.0

        if not experiences:
            warnings.append("Nenhuma experiência profissional identificada")
            suggestions.append("Verificar se seção de experiência está presente")
            confidence_factor = 0.8
            return {
                "warnings": warnings,
                "suggestions": suggestions,
                "confidence_factor": confidence_factor,
            }

        # Validar cada experiência
        incomplete_count = 0
        for exp in experiences:
            # Checar se tem informações básicas
            if not exp.role:
                incomplete_count += 1
            if not exp.company and not exp.duration:
                incomplete_count += 1

        if incomplete_count > len(experiences) / 2:
            warnings.append(f"{incomplete_count} experiências com dados incompletos")
            confidence_factor = 0.9

        # Se todas as experiências são muito curtas/vagas
        avg_role_length = sum(len(exp.role or "") for exp in experiences) / len(
            experiences
        )
        if avg_role_length < 10:
            warnings.append("Cargos identificados são muito curtos")
            suggestions.append("Considerar usar LLM para melhor extração")
            confidence_factor *= 0.9

        return {
            "warnings": warnings,
            "suggestions": suggestions,
            "confidence_factor": confidence_factor,
        }

    def _validate_education(self, education: List[Education]) -> Dict:
        """Valida lista de formações."""
        warnings = []
        suggestions = []
        confidence_factor = 1.0

        if not education:
            warnings.append("Nenhuma formação acadêmica identificada")
            suggestions.append("Verificar se seção de formação está presente")
            confidence_factor = 0.85
            return {
                "warnings": warnings,
                "suggestions": suggestions,
                "confidence_factor": confidence_factor,
            }

        # Validar cada formação
        incomplete_count = 0
        for edu in education:
            if not edu.degree:
                incomplete_count += 1
            if len(edu.degree) < 5:  # Grau muito curto
                incomplete_count += 1

        if incomplete_count > 0:
            warnings.append(f"{incomplete_count} formações com dados incompletos")
            confidence_factor = 0.92

        return {
            "warnings": warnings,
            "suggestions": suggestions,
            "confidence_factor": confidence_factor,
        }

    def should_use_llm_fallback(self, validation: ValidationResult) -> bool:
        """Determina se deve usar LLM como fallback."""
        # Usar LLM se:
        # 1. Confiança muito baixa
        if validation.confidence_score < 0.5:
            return True

        # 2. Há erros críticos
        critical_errors = ["Nenhuma skill identificada", "Currículo muito curto"]
        if any(err in validation.errors for err in critical_errors):
            return True

        # 3. Muitas sugestões para usar LLM
        llm_suggestions = [
            s for s in validation.suggestions if "LLM" in s or "llm" in s
        ]
        if len(llm_suggestions) >= 2:
            return True

        return False


class DataQualityChecker:
    """Verifica qualidade e consistência dos dados extraídos."""

    @staticmethod
    def check_date_consistency(experiences: List[Experience]) -> List[str]:
        """Verifica se datas de experiência são consistentes."""
        warnings = []

        # Checar se há períodos sobrepostos (pode ser válido, mas sinalizar)
        # Checar se soma de anos é realista (não > 50 anos)
        # (implementação simplificada)

        return warnings

    @staticmethod
    def check_skill_relevance(candidate: Candidate, job_keywords: List[str]) -> float:
        """Calcula score de relevância das skills para a vaga."""
        if not job_keywords:
            return 0.5  # Neutro se não temos keywords

        all_skills = [s.name.lower() for s in candidate.get_all_skills()]
        matches = sum(
            1 for kw in job_keywords if any(kw.lower() in skill for skill in all_skills)
        )

        return min(matches / len(job_keywords), 1.0) if job_keywords else 0.0

    @staticmethod
    def detect_anomalies(candidate: Candidate) -> List[str]:
        """Detecta anomalias nos dados."""
        anomalies = []

        # Skills duplicadas ou muito similares
        skill_names = [s.name.lower() for s in candidate.get_all_skills()]
        if len(skill_names) != len(set(skill_names)):
            anomalies.append("Skills duplicadas detectadas")

        # Experiência inconsistente com skills
        if len(candidate.experiences) > 5 and len(candidate.hard_skills) < 3:
            anomalies.append("Muita experiência mas poucas skills técnicas")

        # Educação avançada mas sem experiência
        if candidate.education:
            high_degree = any(
                "mestrado" in edu.degree.lower() or "doutorado" in edu.degree.lower()
                for edu in candidate.education
            )
            if high_degree and not candidate.experiences:
                anomalies.append("Formação avançada mas sem experiência registrada")

        return anomalies
