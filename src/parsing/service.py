"""Facade simples para parsing (export amigável).

Permite import direto: from parsing.service import parse_all
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, List

from src.core.models import Candidate, JobProfile
from .loader import ParserService


def parse_all(
    job_path: str | Path,
    cvs_dir: str | Path,
    extract_experience: bool = True,
    extract_education: bool = True,
    extract_requirements: bool = True,
    llm_client=None,
) -> Tuple[JobProfile, List[Candidate]]:
    """Parse job and candidates with optional experience/education/requirements extraction.

    Args:
        job_path: Path to job description file
        cvs_dir: Directory containing resume files
        extract_experience: Enable experience extraction (default: True)
        extract_education: Enable education extraction (default: True)
        extract_requirements: Enable job requirements extraction (default: True)
        llm_client: Optional LLM client for fallback extraction
    """
    service = ParserService(
        extract_experience=extract_experience,
        extract_education=extract_education,
        extract_requirements=extract_requirements,
        llm_client=llm_client,
    )
    return service.parse(job_path, cvs_dir)
