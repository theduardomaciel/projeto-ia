"""Facade simples para parsing (export amigável).

Permite import direto: from parsing.service import parse_all
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, List

from src.core.models import Candidate, JobProfile
from .loader import ParserService


def parse_all(
    job_path: str | Path, cvs_dir: str | Path
) -> Tuple[JobProfile, List[Candidate]]:
    service = ParserService()
    return service.parse(job_path, cvs_dir)
