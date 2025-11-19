"""
Serviço de análise - orquestra o pipeline completo de processamento.

Este módulo é responsável por coordenar:
1. Parsing de currículos e vaga
2. Extração de skills
3. Scoring e ranking
4. Geração de explicações
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from src.api.schemas import CandidateResult
from src.core.models import Candidate, JobProfile
from src.explainability import ExplainabilityEngine
from src.llm.client import get_default_llm
from src.parsing import parse_all
from src.scoring import ScoringEngine
from src.skills import SkillExtractor

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Serviço de análise de candidatos.

    Encapsula a lógica de negócio do pipeline de recrutamento inteligente.
    """

    def __init__(self):
        """Inicializa componentes do pipeline."""
        self.skill_extractor = SkillExtractor()
        self.scoring_engine = ScoringEngine()

        # ExplainabilityEngine depende de LLMClient
        # Verificar se API keys estão configuradas será feito sob demanda
        self.explainability_engine: ExplainabilityEngine | None = None

        logger.info("✓ AnalysisService inicializado")

    def _ensure_explainability_engine(self) -> ExplainabilityEngine | None:
        """Lazy initialization do ExplainabilityEngine."""
        if self.explainability_engine is None:
            try:
                llm_client = get_default_llm()
                self.explainability_engine = ExplainabilityEngine(llm_client)
                logger.info("✓ ExplainabilityEngine inicializado com sucesso")
            except Exception as e:
                logger.warning(
                    f"⚠️  Não foi possível inicializar ExplainabilityEngine: {e}"
                )
                logger.warning(
                    "   Justificativas serão geradas em formato simplificado"
                )
        return self.explainability_engine

    async def analyze(
        self, job_path: Path, resume_paths: List[Path]
    ) -> List[CandidateResult]:
        """
        Executa pipeline completo de análise.

        Args:
            job_path: Caminho para arquivo com descrição da vaga
            resume_paths: Lista de caminhos para currículos

        Returns:
            Lista de CandidateResult ordenada por pontuação (maior para menor)
        """
        logger.info(f"📊 Iniciando análise: 1 vaga, {len(resume_paths)} currículos")

        # 1. Parsing
        logger.info("   [1/4] Parsing de documentos...")
        # Create temporary directory for parse_all (expects directory, not list)
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as cvs_temp_dir:
            # Copy resume files to temp directory
            for resume_path in resume_paths:
                shutil.copy(resume_path, cvs_temp_dir)

            job, candidates = parse_all(job_path, cvs_temp_dir)

        logger.info(f"      ✓ Vaga: {job.title}")
        logger.info(f"      ✓ Candidatos: {len(candidates)}")

        if not candidates:
            logger.warning("⚠️  Nenhum candidato foi carregado com sucesso")
            return []

        # 2. Extração de skills
        logger.info("   [2/4] Extraindo skills...")
        for candidate in candidates:
            self.skill_extractor.extract_from_candidate(candidate)
            logger.debug(
                f"      {candidate.name}: {len(candidate.hard_skills)} hard, "
                f"{len(candidate.soft_skills)} soft"
            )

        # 3. Scoring e ranking
        logger.info("   [3/4] Calculando pontuações...")
        ranked_candidates = self.scoring_engine.rank_candidates(candidates, job)
        logger.info(f"      ✓ {len(ranked_candidates)} candidatos ranqueados")

        # 4. Geração de explicações
        logger.info("   [4/4] Gerando justificativas...")
        explainability = self._ensure_explainability_engine()

        if explainability:
            try:
                # Use explain_candidate for each candidate
                for i, candidate in enumerate(ranked_candidates, 1):
                    candidate.explanation = explainability.explain_candidate(
                        candidate, job, position=i
                    )
                logger.info("      ✓ Justificativas geradas via LLM")
            except Exception as e:
                logger.warning(f"      ⚠️  Erro ao gerar explicações via LLM: {e}")
                logger.warning("      Usando fallback: explicações simplificadas")
                self._generate_fallback_explanations(ranked_candidates, job)
        else:
            logger.info("      → Usando explicações simplificadas (sem LLM)")
            self._generate_fallback_explanations(ranked_candidates, job)

        # 5. Converter para formato da API
        results = self._convert_to_results(ranked_candidates)

        logger.info(f"✅ Pipeline concluído: {len(results)} resultados gerados")
        return results

    def _generate_fallback_explanations(
        self, candidates: List[Candidate], job: JobProfile
    ) -> None:
        """
        Gera explicações simplificadas quando LLM não está disponível.

        Args:
            candidates: Lista de candidatos ranqueados
            job: Perfil da vaga
        """
        for candidate in candidates:
            breakdown = candidate.score_breakdown

            parts = [
                f"{candidate.name} obteve {candidate.score:.1f} pontos na análise."
            ]

            # Hard skills
            hard_score = breakdown.get("hard_skills", 0)
            hard_count = len(candidate.hard_skills)
            if hard_count > 0:
                top_skills = ", ".join([s.name for s in candidate.hard_skills[:3]])
                parts.append(
                    f"Identificadas {hard_count} hard skills ({hard_score:.1f} pts), "
                    f"incluindo: {top_skills}."
                )

            # Soft skills
            soft_score = breakdown.get("soft_skills", 0)
            soft_count = len(candidate.soft_skills)
            if soft_count > 0:
                parts.append(
                    f"Soft skills ({soft_count} identificadas) "
                    f"contribuíram com {soft_score:.1f} pts."
                )

            # Experiência
            exp_score = breakdown.get("experience", 0)
            if exp_score > 0:
                parts.append(f"Experiência profissional pontuou {exp_score:.1f} pts.")

            # Educação
            edu_score = breakdown.get("education", 0)
            if edu_score > 0:
                parts.append(f"Formação acadêmica contribuiu com {edu_score:.1f} pts.")

            candidate.explanation = " ".join(parts)

    def _convert_to_results(self, candidates: List[Candidate]) -> List[CandidateResult]:
        """
        Converte candidatos internos para formato da API.

        Args:
            candidates: Lista de candidatos (já ranqueados)

        Returns:
            Lista de CandidateResult no formato esperado pelo frontend
        """
        results = []

        for position, candidate in enumerate(candidates, start=1):
            result = CandidateResult(
                candidate_name=candidate.name,
                hard_skills=[skill.name for skill in candidate.hard_skills],
                soft_skills=[skill.name for skill in candidate.soft_skills],
                match_score=round(candidate.score, 2),
                explanation=candidate.explanation or "Análise não disponível.",
                ranking_position=position,
            )
            results.append(result)

        return results
