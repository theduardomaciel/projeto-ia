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


class ScoringEngine:
    def __init__(self, weights_config: Optional[Dict] = None) -> None:
        self.config = weights_config or load_weights()
        self.category_weights = self.config.get("category_weights", {})
        self.skill_weights = self.config.get("skill_weights", {})
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

        # Experience (placeholder - pode ser expandido)
        exp_weight = self.category_weights.get("experience", 0.15)
        exp_score = (
            len(candidate.experiences) * exp_weight * 5.0
            if candidate.experiences
            else 0.0
        )

        # Education (placeholder)
        edu_weight = self.category_weights.get("education", 0.05)
        edu_score = (
            len(candidate.education) * edu_weight * 5.0 if candidate.education else 0.0
        )

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
