"""CLI básica para validar parsing.

Uso:
  python -m src.ui.main --job data/samples/job.txt --cvs data/samples/
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from src.parsing import parse_all
from src.skills import SkillExtractor
from src.scoring import ScoringEngine
from src.explainability import ExplainabilityEngine
from src.llm.client import LLMClient


def preview(text: str, n: int = 200) -> str:
    text = text.replace("\n", " ")
    return (text[:n] + "…") if len(text) > n else text


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="CLI de verificação do módulo de parsing"
    )
    parser.add_argument(
        "--job", required=True, help="Caminho para o arquivo de vaga (job.txt)"
    )
    parser.add_argument("--cvs", required=True, help="Pasta contendo curriculo_*.txt")
    parser.add_argument(
        "--extract", action="store_true", help="Extrair e exibir skills por candidato"
    )
    parser.add_argument(
        "--rank", action="store_true", help="Pontuar e rankear candidatos"
    )
    parser.add_argument(
        "--explain", action="store_true", help="Gerar justificativas usando LLM"
    )
    parser.add_argument(
        "--provider", default="gemini", help="Provedor LLM (gemini, openrouter, groq)"
    )
    parser.add_argument("--model", default="gemini-2.0-flash-exp", help="Modelo do LLM")
    args = parser.parse_args(argv)

    job_path = Path(args.job)
    cvs_dir = Path(args.cvs)

    job, candidates = parse_all(job_path, cvs_dir)

    print("Vaga:")
    print(f"  Título: {job.title}")
    print(f"  Arquivo: {job.file_path}")
    print("")

    print(f"Candidatos carregados: {len(candidates)}")
    for i, c in enumerate(candidates, 1):
        norm_preview = preview(c.normalized_text or c.raw_text)
        print(
            f"{i:02d}. {c.name} — arquivo={Path(c.file_path).name if c.file_path else '-'}"
        )
        print(f"    preview: {norm_preview}")

    if args.extract:
        print("")
        print("Extraindo skills...")
        extractor = SkillExtractor()
        for i, c in enumerate(candidates, 1):
            extractor.extract_from_candidate(c)
            hard = sorted({s.name for s in c.hard_skills})
            soft = sorted({s.name for s in c.soft_skills})
            print(f"{i:02d}. {c.name}")
            print(f"    Hard skills: {', '.join(hard) if hard else '-'}")
            print(f"    Soft skills: {', '.join(soft) if soft else '-'}")

    if args.rank:
        print("")
        print("Pontuando e rankeando...")
        # Garantir extração de skills antes de pontuar
        extractor = SkillExtractor()
        for c in candidates:
            if not c.hard_skills and not c.soft_skills:
                extractor.extract_from_candidate(c)

        scorer = ScoringEngine()
        ranked = scorer.rank_candidates(candidates, job)

        print("")
        print("=" * 60)
        print("RANKING DE CANDIDATOS")
        print("=" * 60)
        for i, c in enumerate(ranked, 1):
            print(f"\n{i}º lugar: {c.name} — {c.score:.1f} pontos")
            if c.file_path:
                print(f"   Arquivo: {Path(c.file_path).name}")

            breakdown = c.score_breakdown
            print(f"   Hard skills: {breakdown.get('hard_skills', 0):.1f} pts")
            print(f"   Soft skills: {breakdown.get('soft_skills', 0):.1f} pts")
            print(f"   Experiência: {breakdown.get('experience', 0):.1f} pts")
            print(f"   Educação: {breakdown.get('education', 0):.1f} pts")

            # Detalhar experiência
            if c.experiences:
                print(f"   Experiencias: {len(c.experiences)}")
                for exp in c.experiences[:2]:  # Top 2
                    print(
                        f"      - {exp.role}"
                        + (f" @ {exp.company}" if exp.company else "")
                    )
                    if exp.duration:
                        print(f"        Duracao: {exp.duration}")
            else:
                print(f"   Experiencias: Nenhuma identificada")

            # Detalhar educação
            if c.education:
                print(f"   Formacao: {len(c.education)} curso(s)")
                for edu in c.education[:2]:  # Top 2
                    status_icon = "[OK]" if edu.status == "completed" else "[...]"
                    print(f"      {status_icon} {edu.degree}")
                    if edu.institution:
                        print(f"            {edu.institution}")
            else:
                print(f"   Formacao: Nenhuma identificada")

            # Top 3 hard skills por peso
            hard_detail = breakdown.get("hard_skills_detail", {})
            if hard_detail:
                top_hard = sorted(
                    hard_detail.items(), key=lambda x: x[1], reverse=True
                )[:3]
                print(
                    f"   Top skills: {', '.join(f'{k} ({v:.1f})' for k, v in top_hard)}"
                )

    if args.explain:
        if not args.rank:
            print("\nAviso: --explain requer --rank. Executando ranking primeiro...")
            # Garantir skills e scoring
            extractor = SkillExtractor()
            for c in candidates:
                if not c.hard_skills and not c.soft_skills:
                    extractor.extract_from_candidate(c)
            scorer = ScoringEngine()
            ranked = scorer.rank_candidates(candidates, job)

        print("\n" + "=" * 60)
        print("JUSTIFICATIVAS (geradas por LLM)")
        print("=" * 60)

        # Inicializar LLM
        try:
            from src.llm.client import GeminiClient
            import os
            from dotenv import load_dotenv

            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise ValueError("GEMINI_API_KEY não encontrada no .env")

            llm_client = GeminiClient(api_key=api_key, model=args.model)
            explainer = ExplainabilityEngine(llm_client=llm_client)

            # Gerar justificativas para top 3
            top_candidates = ranked[:3] if len(ranked) >= 3 else ranked

            for i, c in enumerate(top_candidates, 1):
                print(f"\n{'─' * 60}")
                print(f"{i}º lugar: {c.name} ({c.score:.1f} pts)")
                print(f"{'─' * 60}")

                explanation = explainer.explain_candidate(
                    candidate=c,
                    job=job,
                    position=i,
                    provider=args.provider,
                    model=args.model,
                )

                print(explanation)

            print(f"\n{'=' * 60}")
            print(
                f"[OK] Justificativas geradas com sucesso usando {args.provider}/{args.model}"
            )
            print(f"[OK] Logs salvos em logs/llm_session_*.jsonl")

        except Exception as e:
            print(f"\n[!] Erro ao gerar justificativas: {e}")
            print("Gerando justificativas com fallback (heuristicas)...\n")

            explainer = ExplainabilityEngine(llm_client=None)
            for i, c in enumerate(ranked[:3], 1):
                print(f"\n{i}º lugar: {c.name}")
                print("-" * 60)
                explanation = explainer._fallback_explanation(c, job, i)
                print(explanation)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
