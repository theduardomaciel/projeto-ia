"""Carregamento de arquivos de vaga e currículos.

Responsabilidades:
 - Ler arquivos .txt (vaga e currículos)
 - Inferir nome do candidato a partir do conteúdo
 - Registrar eventos de parsing em log
 - Stub para suporte futuro a PDF
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import os
import re
import unicodedata
from datetime import datetime

from src.core.models import Candidate, JobProfile

# Import dos extractors (importação tardia para evitar ciclos)
try:
    from src.parsing.experience_extractor import ExperienceExtractor
    from src.parsing.education_extractor import EducationExtractor
except ImportError:
    ExperienceExtractor = None
    EducationExtractor = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = PROJECT_ROOT / "logs" / "parsing_events.log"


def _log(event: str, detail: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        ts = datetime.now().isoformat(timespec="seconds")
        f.write(f"{ts}\t{event}\t{detail}\n")


def _safe_read(path: Path) -> str:
    """Lê arquivo tentando utf-8 e fallback para latin-1."""
    try:
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        _log("file_read", f"path={path} bytes={len(data)} chars={len(text)}")
        return text
    except Exception as e:  # pragma: no cover - log de erro bruto
        _log("file_error", f"path={path} error={e}")
        raise


def _infer_name(raw_text: str, fallback: str) -> str:
    """Tenta inferir o nome do candidato pelas primeiras linhas.

    Heurística: linha com 2-5 tokens, cada um iniciando com letra maiúscula,
    evitando palavras puramente técnicas.
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()][:10]
    name_pattern = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+$")
    tech_keywords = {"python", "java", "desenvolvedor", "developer", "curriculo"}
    for line in lines:
        tokens = re.split(r"\s+", line)
        if 2 <= len(tokens) <= 5:
            if all(name_pattern.match(t) for t in tokens):
                lowered = {t.lower() for t in tokens}
                if lowered.isdisjoint(tech_keywords):
                    return line
    return fallback


def _normalize_whitespace(text: str) -> str:
    """Normaliza espaços em branco, preservando quebras de linha."""
    # Preservar quebras de linha, mas normalizar espaços em cada linha
    lines = text.split("\n")
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]
    return "\n".join(normalized_lines)


def remove_accents(text: str) -> str:
    """Remove acentos mantendo apenas caracteres base."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class FileLoader:
    def __init__(self) -> None:
        pass

    def load_job(self, job_path: str | Path) -> JobProfile:
        path = Path(job_path)
        raw = _safe_read(path)
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        title = lines[0][:120] if lines else "Vaga"
        description = raw
        job = JobProfile(
            title=title, description=description, raw_text=raw, file_path=str(path)
        )
        _log("job_loaded", f"title={title}")
        return job

    def load_candidates(self, cvs_dir: str | Path) -> List[Candidate]:
        dir_path = Path(cvs_dir)
        pattern = re.compile(r"curriculo_(\d+).txt", re.IGNORECASE)
        candidates: List[Candidate] = []
        for file in sorted(dir_path.glob("*.txt")):
            m = pattern.match(file.name)
            if not m:
                continue
            idx = int(m.group(1))
            raw = _safe_read(file)
            fallback_name = f"Candidato {idx:02d}"
            name = _infer_name(raw, fallback=fallback_name)
            cand = Candidate(name=name, raw_text=raw, file_path=str(file))
            candidates.append(cand)
            _log("candidate_loaded", f"name='{name}' file={file.name}")
        return candidates

    # Stub futuro para PDF
    def parse_pdf(self, pdf_path: str | Path) -> None:  # pragma: no cover - futuro
        raise NotImplementedError("Suporte a PDF não implementado ainda.")


class TextNormalizer:
    def __init__(
        self, lower: bool = True, remove_acc: bool = True, collapse_ws: bool = True
    ) -> None:
        self.lower = lower
        self.remove_acc = remove_acc
        self.collapse_ws = collapse_ws

    def normalize(self, text: str) -> str:
        processed = text
        if self.lower:
            processed = processed.lower()
        if self.remove_acc:
            processed = remove_accents(processed)
        if self.collapse_ws:
            processed = _normalize_whitespace(processed)
        return processed


class ParserService:
    def __init__(
        self,
        loader: FileLoader | None = None,
        normalizer: TextNormalizer | None = None,
        extract_experience: bool = True,
        extract_education: bool = True,
        llm_client=None,
    ) -> None:
        self.loader = loader or FileLoader()
        self.normalizer = normalizer or TextNormalizer()
        self.extract_experience = extract_experience
        self.extract_education = extract_education

        # Inicializar extractors se habilitados
        self.exp_extractor = None
        self.edu_extractor = None

        if extract_experience and ExperienceExtractor:
            self.exp_extractor = ExperienceExtractor(llm_client=llm_client)

        if extract_education and EducationExtractor:
            self.edu_extractor = EducationExtractor(llm_client=llm_client)

    def parse(self, job_path: str | Path, cvs_dir: str | Path):
        job = self.loader.load_job(job_path)
        candidates = self.loader.load_candidates(cvs_dir)

        # Normalizar texto e extrair informações estruturadas
        for cand in candidates:
            cand.normalized_text = self.normalizer.normalize(cand.raw_text)

            # Extrair experiência profissional
            if self.exp_extractor:
                cand.experiences = self.exp_extractor.extract_from_candidate(cand)

            # Extrair formação acadêmica
            if self.edu_extractor:
                cand.education = self.edu_extractor.extract_from_candidate(cand)

        return job, candidates
