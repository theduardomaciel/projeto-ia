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
            
            # Top 3 hard skills por peso
            hard_detail = breakdown.get('hard_skills_detail', {})
            if hard_detail:
                top_hard = sorted(hard_detail.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   Principais skills: {', '.join(f'{k} ({v:.1f})' for k, v in top_hard)}")
    
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
