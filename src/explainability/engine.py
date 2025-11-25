"""Motor de explicabilidade usando LLM.

Gera justificativas em linguagem natural para decisões do sistema:
 - Por que candidato X está em Yª posição?
 - Quais são os pontos fortes e fracos?
 - Como as skills se alinham com a vaga?
"""

from __future__ import annotations

from typing import List, Optional
from pathlib import Path

from src.core.models import Candidate, JobProfile, AnalysisResult
from src.llm.client import LLMClient
from src.llm.utils import get_llm_logger


class ExplainabilityEngine:
    """Responsável por gerar explicações das análises.

    Organização interna:
    - Constantes de thresholds e modelos
    - Helpers privados para formatar partes do prompt
    - Métodos públicos: explain_candidate / explain_all_candidates
    """

    HARD_STRONG_THRESHOLD = 3.0
    HARD_OK_THRESHOLD = 2.0
    RECOMMENDATION_STRONG = 7
    RECOMMENDATION_RECOMMENDED = 6.5
    RECOMMENDATION_RESSALVAS = 4.5

    DEFAULT_PROVIDER = "gemini"
    DEFAULT_MODEL = "gemini-2.5-flash-lite"
    DEFAULT_BATCH_MODEL = "gemini-2.0-flash-exp"

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client
        self.logger = get_llm_logger()

    # ------------------------ Helpers internos ------------------------
    def _format_skills_list(self, skills, empty_placeholder: str) -> str:
        names = sorted({s.name for s in skills})
        return ", ".join(names) if names else empty_placeholder

    def _extract_score_breakdown(self, candidate: Candidate) -> dict:
        breakdown = candidate.score_breakdown or {}
        return {
            "hard_score": breakdown.get("hard_skills", 0),
            "soft_score": breakdown.get("soft_skills", 0),
            "exp_score": breakdown.get("experience", 0),
            "edu_score": breakdown.get("education", 0),
            "hard_detail": breakdown.get("hard_skills_detail", {}),
        }

    def _compute_top_skills(self, hard_detail: dict, limit: int = 5) -> str:
        if not hard_detail:
            return "Nenhuma skill com peso alto detectada"
        top = sorted(hard_detail.items(), key=lambda x: x[1], reverse=True)[:limit]
        return (
            ", ".join(f"{k} ({v:.1f} pts)" for k, v in top)
            if top
            else "Nenhuma skill com peso alto detectada"
        )

    def _recommendation_label(self, score: float) -> str:
        if score >= self.RECOMMENDATION_STRONG:
            return "Fortemente recomendado"
        if score >= self.RECOMMENDATION_RECOMMENDED:
            return "Recomendado"
        if score >= self.RECOMMENDATION_RESSALVAS:
            return "Recomendado com ressalvas"
        return "Não recomendado"

    def _build_explanation_prompt(
        self, candidate: Candidate, job: JobProfile, position: Optional[int] = None
    ) -> str:
        """Constrói prompt para geração de justificativa."""
        hard_skills_list = self._format_skills_list(
            candidate.hard_skills, "Nenhuma hard skill detectada"
        )
        soft_skills_list = self._format_skills_list(
            candidate.soft_skills, "Nenhuma soft skill detectada"
        )

        sb = self._extract_score_breakdown(candidate)
        hard_score = sb["hard_score"]
        soft_score = sb["soft_score"]
        exp_score = sb["exp_score"]
        edu_score = sb["edu_score"]
        top_skills_str = self._compute_top_skills(sb["hard_detail"], limit=5)

        position_text = f"{position}ª posição no ranking" if position else "ranking"

        prompt = f"""Você é um gerente de RH experiente escrevendo feedback para candidatos.

Baseado na análise de um candidato para uma vaga específica, gere uma justificativa clara e objetiva explicando a pontuação obtida.

**Informações da vaga:**
Título: {job.title}
Descrição: {job.description[:300]}...

**Informações do candidato:**
Nome: {candidate.name}
Posição: {position_text}
Pontuação total: {candidate.score:.1f} pontos

**Skills identificadas:**
Hard skills: {hard_skills_list}
Soft skills: {soft_skills_list}

**Detalhamento da pontuação:**
- Hard skills: {hard_score:.1f} pontos
- Soft skills: {soft_score:.1f} pontos
- Experiência: {exp_score:.1f} pontos
- Formação: {edu_score:.1f} pontos

**Skills mais relevantes para a vaga:**
{top_skills_str if top_skills_str else "Nenhuma skill com peso alto detectada"}

**Tarefa:**
Gere uma justificativa de 2-4 parágrafos que:
1. Resuma os principais pontos fortes do candidato em relação à vaga
2. Explique como as competências técnicas e comportamentais se alinham com os requisitos
3. Mencione possíveis gaps ou áreas de desenvolvimento (se houver)
4. Conclua com uma recomendação clara (fortemente recomendado, recomendado, recomendado com ressalvas, ou não recomendado para esta vaga)

Mantenha tom profissional, objetivo e respeitoso. Seja conciso e direto."""

        return prompt

    def explain_candidate(
        self,
        candidate: Candidate,
        job: JobProfile,
        position: Optional[int] = None,
        provider: str = "gemini",
        model: str = "gemini-2.5-flash-lite",
    ) -> str:
        """Gera justificativa para um candidato usando LLM."""
        if not self.llm_client:
            return self._fallback_explanation(candidate, job, position)

        prompt = self._build_explanation_prompt(candidate, job, position)

        try:
            import time

            start = time.time()

            llm_response = self.llm_client.call(
                prompt=prompt, max_tokens=2500, temperature=0.7
            )

            if not llm_response.success:
                raise Exception(llm_response.error)

            response_text = llm_response.content
            latency = llm_response.latency or (time.time() - start)

            # Log da interação
            self.logger.log_interaction(
                prompt=prompt,
                response=response_text,
                provider=llm_response.provider,
                model=llm_response.model,
                purpose=f"explanation_{candidate.name}",
                tokens_used=llm_response.tokens_used,
                latency=latency,
                success=True,
                metadata={
                    "candidate": candidate.name,
                    "score": candidate.score,
                    "position": position,
                },
            )

            # Armazena no candidato
            candidate.explanation = response_text.strip()
            return candidate.explanation

        except Exception as e:
            self.logger.log_interaction(
                prompt=prompt,
                response="",
                provider=provider,
                model=model,
                purpose=f"explanation_{candidate.name}",
                success=False,
                error=str(e),
                metadata={"candidate": candidate.name},
            )
            print(f"Erro ao gerar explicação LLM: {e}")
            # Fallback em caso de erro
            return self._fallback_explanation(candidate, job, position)

    def _fallback_explanation(
        self, candidate: Candidate, job: JobProfile, position: Optional[int] = None
    ) -> str:
        """Gera explicação baseada em heurísticas quando LLM não disponível."""
        sb = self._extract_score_breakdown(candidate)
        hard_score = sb["hard_score"]
        soft_score = sb["soft_score"]
        hard_count = len(candidate.hard_skills)
        soft_count = len(candidate.soft_skills)

        position_text = f"está em {position}ª posição no ranking e" if position else ""
        explanation_parts = [
            f"{candidate.name} {position_text} obteve {candidate.score:.1f} pontos na análise.",
        ]

        if hard_score > self.HARD_STRONG_THRESHOLD:
            explanation_parts.append(
                f"Demonstra forte perfil técnico com {hard_count} hard skills identificadas ("
                f"{hard_score:.1f} pts)."
            )
        elif hard_score > self.HARD_OK_THRESHOLD:
            explanation_parts.append(
                f"Perfil técnico adequado com {hard_count} hard skills ("
                f"{hard_score:.1f} pts)."
            )
        else:
            explanation_parts.append(
                f"Perfil técnico limitado ({hard_count} skills, {hard_score:.1f} pts)."
            )

        if soft_count > 0:
            explanation_parts.append(
                f"Identificadas {soft_count} soft skills (" f"{soft_score:.1f} pts)."
            )
        else:
            explanation_parts.append(
                "Não foram identificadas soft skills explícitas no currículo."
            )

        recommendation = self._recommendation_label(candidate.score)
        explanation_parts.append(f"Recomendação: {recommendation} para a vaga.")

        candidate.explanation = "\n\n".join(explanation_parts)
        return candidate.explanation

    def explain_all_candidates(
        self,
        analysis_result: AnalysisResult,
        provider: str = "gemini",
        model: str = "gemini-2.0-flash-exp",
        use_llm: bool = True,
    ) -> AnalysisResult:
        """Gera justificativas para todos os candidatos rankeados."""
        if not use_llm:
            self.llm_client = None

        for i, candidate in enumerate(analysis_result.ranked_candidates, 1):
            self.explain_candidate(
                candidate=candidate,
                job=analysis_result.job_profile,
                position=i,
                provider=provider,
                model=model,
            )

        return analysis_result
