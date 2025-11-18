"""Motor de pontuação de candidatos.

Calcula aderência à vaga com base em:
 - Hard skills detectadas × peso da skill
 - Soft skills detectadas × peso da skill
 - Pesos por categoria (hard_skills, soft_skills, experience, education)

Gera score_breakdown detalhado para transparência.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from src.core.models import Candidate, JobProfile, AnalysisResult
from src.core.config import load_weights
from src.parsing.experience_extractor import ExperienceExtractor
from src.parsing.education_extractor import EducationExtractor


class ScoringEngine:
    def __init__(self, weights_config: Optional[Dict] = None) -> None:
        self.config = weights_config or load_weights()
        self.category_weights = self.config.get("category_weights", {})
        self.skill_weights = self.config.get("skill_weights", {})
        # Extractors para métricas adicionais
        self.exp_extractor = ExperienceExtractor()
        self.edu_extractor = EducationExtractor()
        # log file
        self._log_file = (
            Path(__file__).resolve().parents[2] / "logs" / "scoring_events.log"
        )

    def _calculate_skills_score(
        self, skills: List, category_weight: float, default_skill_weight: float = 5.0
    ) -> tuple[float, Dict[str, float]]:
        """Calcula pontuação de uma categoria de skills.

        Retorna: (score_total, breakdown)
        """
        if not skills:
            return 0.0, {}

        breakdown = {}
        total = 0.0

        for skill in skills:
            skill_name = skill.name.lower()
            weight = self.skill_weights.get(skill_name, default_skill_weight)
            # confidence influencia o peso final
            score = weight * skill.confidence
            breakdown[skill_name] = score
            total += score

        # normaliza pela quantidade de skills (evita candidato com 50 skills dominar)
        normalized = total / len(skills) if skills else 0.0
        # aplica peso da categoria
        final = normalized * category_weight

        return final, breakdown

    def _calculate_experience_score(
        self, candidate: Candidate, weight: float, job: Optional[JobProfile] = None
    ) -> float:
        """Calcula pontuação baseada em experiência profissional.

        Fatores considerados:
        - Anos totais de experiência
        - Senioridade inferida
        - Relevância dos cargos (se há match com vaga)
        """
        if not candidate.experiences:
            return 0.0

        # Calcular anos totais
        total_years = self.exp_extractor.calculate_total_years(candidate.experiences)

        # Score base por anos (escala: 0-10)
        # 0 anos = 0, 1-2 anos = 4, 3-4 anos = 6, 5+ anos = 8-10
        if total_years >= 5:
            years_score = 10.0
        elif total_years >= 3:
            years_score = 6.0 + (total_years - 3) * 1.0
        elif total_years >= 1:
            years_score = 4.0 + (total_years - 1) * 1.0
        else:
            years_score = total_years * 4.0

        # Inferir senioridade
        first_exp = candidate.experiences[0] if candidate.experiences else None
        seniority = self.exp_extractor.infer_seniority(
            total_years, first_exp.role if first_exp else ""
        )

        # Bônus por senioridade
        seniority_bonus = {"senior": 2.0, "mid": 1.0, "junior": 0.0}.get(seniority, 0.0)

        # Bônus por relevância (checar se cargo contém palavras-chave da vaga)
        relevance_bonus = 0.0
        if job and candidate.experiences:
            job_text_lower = (job.description or "").lower()
            for exp in candidate.experiences:
                role_lower = exp.role.lower()
                # Checar overlap de palavras relevantes
                if any(
                    term in job_text_lower
                    for term in ["desenvolvedor", "developer"]
                    if term in role_lower
                ):
                    relevance_bonus += 1.0

        # Score final
        total_score = (years_score + seniority_bonus + relevance_bonus) * weight
        return round(total_score, 2)

    def _calculate_education_score(
        self, candidate: Candidate, weight: float, job: Optional[JobProfile] = None
    ) -> float:
        """Calcula pontuação baseada em formação acadêmica.

        Fatores considerados:
        - Nível do maior grau (técnico < graduação < pós)
        - Relevância da área para tech
        - Status (completo vs cursando)
        """
        if not candidate.education:
            return 0.0

        # Obter nível do maior grau
        highest_level = self.edu_extractor.get_highest_degree_level(candidate.education)

        # Score base por nível (0-10)
        level_scores = {
            6: 10.0,  # Doutorado
            5: 9.0,  # Mestrado/MBA
            4: 8.0,  # Especialização
            3: 7.0,  # Bacharelado/Licenciatura
            2: 5.0,  # Tecnólogo
            1: 3.0,  # Técnico
            0: 1.0,  # Ensino médio
        }
        level_score = level_scores.get(highest_level, 0.0)

        # Bônus por área relevante
        relevance_bonus = (
            2.0 if self.edu_extractor.has_relevant_degree(candidate.education) else 0.0
        )

        # Penalidade leve se todas as formações estão incompletas
        all_incomplete = all(edu.status == "incomplete" for edu in candidate.education)
        completion_penalty = -2.0 if all_incomplete else 0.0

        # Score final
        total_score = (level_score + relevance_bonus + completion_penalty) * weight
        return max(round(total_score, 2), 0.0)  # Não permitir negativo

    def score_candidate(
        self, candidate: Candidate, job: Optional[JobProfile] = None
    ) -> Candidate:
        """Pontua um candidato e preenche score e score_breakdown."""
        # Hard skills
        hard_weight = self.category_weights.get("hard_skills", 0.6)
        hard_score, hard_breakdown = self._calculate_skills_score(
            candidate.hard_skills, hard_weight
        )

        # Soft skills
        soft_weight = self.category_weights.get("soft_skills", 0.2)
        soft_score, soft_breakdown = self._calculate_skills_score(
            candidate.soft_skills, soft_weight
        )

        # Experience (baseado em anos e senioridade)
        exp_weight = self.category_weights.get("experience", 0.15)
        exp_score = self._calculate_experience_score(candidate, exp_weight, job)

        # Education (baseado em nível e relevância)
        edu_weight = self.category_weights.get("education", 0.05)
        edu_score = self._calculate_education_score(candidate, edu_weight, job)

        # Score total
        total = hard_score + soft_score + exp_score + edu_score

        candidate.score = round(total, 2)
        candidate.score_breakdown = {
            "hard_skills": round(hard_score, 2),
            "soft_skills": round(soft_score, 2),
            "experience": round(exp_score, 2),
            "education": round(edu_score, 2),
            "hard_skills_detail": {k: round(v, 2) for k, v in hard_breakdown.items()},
            "soft_skills_detail": {k: round(v, 2) for k, v in soft_breakdown.items()},
        }

        # Log
        self._log_scoring(candidate)

        return candidate

    def _log_scoring(self, candidate: Candidate) -> None:
        """Registra pontuação em logs/scoring_events.log."""
        try:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            with self._log_file.open("a", encoding="utf-8") as f:
                ts = datetime.now().isoformat(timespec="seconds")
                fname = Path(candidate.file_path).name if candidate.file_path else "-"
                hard = candidate.score_breakdown.get("hard_skills", 0)
                soft = candidate.score_breakdown.get("soft_skills", 0)
                f.write(
                    f"{ts}\tname={candidate.name}\tfile={fname}\t"
                    f"score={candidate.score}\thard={hard}\tsoft={soft}\n"
                )
        except Exception:
            pass

    def rank_candidates(
        self, candidates: List[Candidate], job: Optional[JobProfile] = None
    ) -> List[Candidate]:
        """Pontua todos os candidatos e retorna lista ordenada (maior score primeiro)."""
        for cand in candidates:
            self.score_candidate(cand, job)

        ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
        return ranked

    def create_analysis_result(
        self,
        job: JobProfile,
        candidates: List[Candidate],
        llm_provider: Optional[str] = None,
    ) -> AnalysisResult:
        """Cria resultado completo da análise com ranking."""
        ranked = self.rank_candidates(candidates, job)

        result = AnalysisResult(
            job_profile=job,
            candidates=candidates,
            ranked_candidates=ranked,
            llm_provider=llm_provider,
        )

        return result
