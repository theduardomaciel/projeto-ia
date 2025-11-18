"""Utilitários para carregar configurações externas (JSON/TXT).

Centraliza leitura de:
 - data/config/skills.json
 - data/config/weights.json
 - data/config/prompt_templates.txt
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def project_root() -> Path:
    # src/core/config.py -> src/core -> src -> repo root
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    return project_root() / "data" / "config"


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_skills() -> Dict[str, Any]:
    """Retorna dicionário de skills a partir de skills.json."""
    path = project_root() / "data" / "config" / "skills.json"
    return _read_json(path)


def load_weights() -> Dict[str, float]:
    """Retorna pesos/configs de scoring a partir de weights.json."""
    path = project_root() / "data" / "config" / "weights.json"
    return _read_json(path)


def load_prompt_templates() -> List[str]:
    """Retorna lista de prompts (linhas não vazias) do prompt_templates.txt."""
    path = project_root() / "data" / "config" / "prompt_templates.txt"
    with path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    return [l for l in lines if l]
