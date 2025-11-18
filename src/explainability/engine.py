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
    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self.llm_client = llm_client
        self.logger = get_llm_logger()

    def _build_explanation_prompt(
        self, candidate: Candidate, job: JobProfile, position: Optional[int] = None
    ) -> str:
        """Constrói prompt para geração de justificativa."""
        # Hard skills formatadas
        hard_skills_list = ", ".join(sorted({s.name for s in candidate.hard_skills}))
        if not hard_skills_list:
            hard_skills_list = "Nenhuma hard skill detectada"

        # Soft skills formatadas
        soft_skills_list = ", ".join(sorted({s.name for s in candidate.soft_skills}))
        if not soft_skills_list:
            soft_skills_list = "Nenhuma soft skill detectada"

        # Breakdown
        breakdown = candidate.score_breakdown or {}
        hard_score = breakdown.get("hard_skills", 0)
        soft_score = breakdown.get("soft_skills", 0)
        exp_score = breakdown.get("experience", 0)
        edu_score = breakdown.get("education", 0)

        # Top 5 hard skills por peso
        hard_detail = breakdown.get("hard_skills_detail", {})
        top_skills = sorted(hard_detail.items(), key=lambda x: x[1], reverse=True)[:5]
        top_skills_str = ", ".join(f"{k} ({v:.1f} pts)" for k, v in top_skills)

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
            print("LLM Client não configurado, usando fallback heurístico.")
            # Fallback: justificativa baseada em heurísticas
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
            # Fallback em caso de erro
            return self._fallback_explanation(candidate, job, position)

    def _fallback_explanation(
        self, candidate: Candidate, job: JobProfile, position: Optional[int] = None
    ) -> str:
        """Gera explicação baseada em heurísticas quando LLM não disponível."""
        breakdown = candidate.score_breakdown or {}
        hard_score = breakdown.get("hard_skills", 0)
        soft_score = breakdown.get("soft_skills", 0)

        hard_count = len(candidate.hard_skills)
        soft_count = len(candidate.soft_skills)

        position_text = f"está em {position}ª posição no ranking e" if position else ""

        explanation = f"{candidate.name} {position_text} obteve {candidate.score:.1f} pontos na análise.\n\n"

        if hard_score > 3.0:
            explanation += f"O candidato demonstra forte perfil técnico com {hard_count} hard skills identificadas, "
            explanation += f"resultando em {hard_score:.1f} pontos nesta categoria. "
        elif hard_score > 2.0:
            explanation += f"O candidato possui um perfil técnico adequado com {hard_count} hard skills, "
            explanation += f"totalizando {hard_score:.1f} pontos. "
        else:
            explanation += f"O candidato apresenta perfil técnico limitado ({hard_count} skills, {hard_score:.1f} pts). "

        if soft_count > 0:
            explanation += f"Em termos de competências comportamentais, foram identificadas {soft_count} soft skills ({soft_score:.1f} pts).\n\n"
        else:
            explanation += (
                "Não foram identificadas soft skills explícitas no currículo.\n\n"
            )

        # Recomendação
        if candidate.score >= 4.0:
            explanation += "Recomendação: Fortemente recomendado para a vaga."
        elif candidate.score >= 3.0:
            explanation += "Recomendação: Recomendado para a vaga."
        elif candidate.score >= 2.0:
            explanation += (
                "Recomendação: Recomendado com ressalvas - verificar fit específico."
            )
        else:
            explanation += "Recomendação: Não recomendado para esta vaga específica."

        candidate.explanation = explanation
        return explanation

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
