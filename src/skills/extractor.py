"""Extração de skills (hard e soft) via dicionário + regex.

Método híbrido:
 - Dicionários e sinônimos configuráveis (data/config/skills.json)
 - Expressões regulares com tolerância para espaços e símbolos
 - Normalização esperada: texto já em lowercase e sem acentos

LLM pode ser integrado depois como fallback para casos ambíguos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Optional
from datetime import datetime
import re

from src.core.models import Skill, Candidate
from src.core.config import load_skills


def _compile_pattern(term: str) -> re.Pattern:
    """Compila um padrão que considera espaços flexíveis e limites de palavra.

    - Escapa caracteres especiais
    - Substitui espaços por \s+
    - Usa lookarounds para não pegar dentro de palavras
    """
    escaped = re.escape(term)
    # permitir espaços flexíveis entre tokens
    escaped = escaped.replace("\\ ", r"\s+")
    # limites aproximados: evitar dentro de palavra, mas permitir '/', '+' etc.
    pattern = rf"(?<!\w){escaped}(?!\w)"
    return re.compile(pattern, re.IGNORECASE)


@dataclass
class SkillMatch:
    canonical: str
    category: str  # 'hard' | 'soft'
    source: str  # 'dictionary' | 'synonym'
    count: int


class SkillExtractor:
    def __init__(self, skills_config: Optional[Dict] = None) -> None:
        self.config = skills_config or load_skills()
        self._hard_by_canonical, self._soft_by_canonical = self._build_canonical_sets()
        self._alias_map = self._build_alias_map()
        self._patterns = self._build_patterns()
        # arquivo de log de extração
        self._log_file = (
            Path(__file__).resolve().parents[2] / "logs" / "skill_events.log"
        )

    def _build_canonical_sets(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        hard = {}
        soft = {}
        hard_groups = self.config.get("hard_skills", {})
        for group, items in hard_groups.items():
            for it in items:
                hard[it.lower()] = "hard"
        soft_groups = self.config.get("soft_skills", {})
        for group, items in soft_groups.items():
            for it in items:
                soft[it.lower()] = "soft"
        return hard, soft

    def _build_alias_map(self) -> Dict[str, str]:
        alias_map: Dict[str, str] = {}
        synonyms = self.config.get("synonyms", {})
        for canonical, alist in synonyms.items():
            canon = canonical.lower()
            alias_map[canon] = canon
            for a in alist:
                alias_map[a.lower()] = canon
        # também mapeia cada skill canônica para si mesma
        for canon in list(self._hard_by_canonical.keys()) + list(
            self._soft_by_canonical.keys()
        ):
            alias_map.setdefault(canon, canon)
        return alias_map

    def _build_patterns(self) -> Dict[str, re.Pattern]:
        patterns: Dict[str, re.Pattern] = {}
        for alias in self._alias_map.keys():
            patterns[alias] = _compile_pattern(alias)
        return patterns

    def extract_from_text(self, text: str) -> List[Skill]:
        matches: Dict[str, SkillMatch] = {}

        for alias, pattern in self._patterns.items():
            hits = list(pattern.finditer(text))
            if not hits:
                continue
            canonical = self._alias_map[alias]
            category = (
                "hard"
                if canonical in self._hard_by_canonical
                else "soft" if canonical in self._soft_by_canonical else None
            )
            if not category:
                continue
            source = "synonym" if alias != canonical else "dictionary"
            prev = matches.get(canonical)
            count = (prev.count if prev else 0) + len(hits)
            matches[canonical] = SkillMatch(
                canonical=canonical, category=category, source=source, count=count
            )

        skills: List[Skill] = []
        for m in matches.values():
            confidence = 0.9 if m.source == "dictionary" else 0.85
            skills.append(
                Skill(
                    name=m.canonical,
                    category=m.category,
                    confidence=confidence,
                    source=m.source,
                )
            )
        return skills

    def extract_from_candidate(self, cand: Candidate) -> Candidate:
        base_text = cand.normalized_text or cand.raw_text.lower()
        extracted = self.extract_from_text(base_text)
        for sk in extracted:
            cand.add_skill(sk)
        # logging simples
        try:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            with self._log_file.open("a", encoding="utf-8") as f:
                ts = datetime.now().isoformat(timespec="seconds")
                fname = Path(cand.file_path).name if cand.file_path else "-"
                hard = ",".join(sorted({s.name for s in cand.hard_skills}))
                soft = ",".join(sorted({s.name for s in cand.soft_skills}))
                f.write(f"{ts}\tfile={fname}\thard=[{hard}]\tsoft=[{soft}]\n")
        except Exception:
            pass
        return cand
