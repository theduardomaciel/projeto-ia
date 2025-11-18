"""Extração de formação acadêmica de currículos.

Método híbrido:
 - Regex para detectar seções de educação
 - Heurísticas para grau, instituição, ano
 - Classificação de nível (técnico, graduação, pós)
 - Fallback LLM para casos complexos
"""

from __future__ import annotations

import re
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from src.core.models import Education, Candidate


class EducationExtractor:
    """Extrai formação acadêmica de texto de currículo."""

    # Padrões para identificar seções de educação
    SECTION_PATTERNS = [
        r"(?i)formação\s+acadêmica",
        r"(?i)formação",
        r"(?i)educação",
        r"(?i)education",
        r"(?i)academic\s+background",
        r"(?i)academic\s+history",
        r"(?i)escolaridade",
        r"(?i)academic\s+profile",
        r"(?i)studies",
    ]

    SECTION_END_PATTERNS = [
        r"(?i)experiência|experience",
        r"(?i)habilidades|skills",
        r"(?i)competências",
        r"(?i)certificações|certifications",
        r"(?i)projetos|projects",
        r"(?i)idiomas|languages",
        r"(?i)resumo|summary",
    ]

    # Graus acadêmicos (ordem de precedência)
    DEGREE_PATTERNS = {
        "doutorado": [
            "doutorado",
            "doctorado",
            "phd",
            "ph.d",
            "doctorate",
            "doctor of philosophy",
        ],
        "mestrado": [
            "mestrado",
            "master",
            "msc",
            "m.sc",
            "m.s",
            "ms",
            "master of science",
            "master of engineering",
        ],
        "mba": ["mba", "master of business", "executive mba"],
        "especialização": [
            "especialização",
            "pós-graduação",
            "postgraduate",
            "especialista",
            "lato sensu",
            "certificate program",
        ],
        "bacharelado": [
            "bacharelado",
            "bachelor",
            "b.sc",
            "b.s",
            "b.a",
            "b.s.",
            "b.a.",
            "graduação",
            "undergraduate",
            "superior completo",
        ],
        "licenciatura": [
            "licenciatura",
            "licentiate",
            "teaching degree",
            "b.ed",
        ],
        "tecnólogo": [
            "tecnólogo",
            "technology degree",
            "tecnologia",
            "cst",
            "curso superior de tecnologia",
            "associate of applied science",
            "aas",
        ],
        "técnico": [
            "técnico",
            "technical course",
            "ensino técnico",
            "vocational",
            "trade school",
        ],
        "ensino médio": [
            "ensino médio",
            "high school",
            "secondary",
            "secundário",
            "highschool",
        ],
    }

    # Status
    STATUS_PATTERNS = {
        "completed": [
            "completo",
            "concluído",
            "concluded",
            "completed",
            "formado",
            "graduated",
            "finished",
        ],
        "in_progress": [
            "cursando",
            "em andamento",
            "in progress",
            "current",
            "presente",
            "ongoing",
            "currently enrolled",
            "studying",
            "expected",
            "previsto",
        ],
        "incomplete": [
            "incompleto",
            "trancado",
            "incomplete",
            "discontinued",
            "dropped",
            "paused",
        ],
    }

    INSTITUTION_HINTS = [
        "universidade",
        "university",
        "faculdade",
        "college",
        "instituto",
        "institute",
        "school",
        "academy",
        "polytechnic",
        "centro universitário",
        "ifal",
        "uf",
        "puc",
        "federal",
    ]

    MONTH_PATTERN = r"(?:jan(?:eiro)?|feb|fev(?:ereiro)?|mar(?:ço|ch)?|apr|abr(?:il)?|may|mai(?:o)?|jun(?:ho|e)?|jul(?:ho|y)?|aug|ago(?:sto)?|sep|set(?:embro)?|oct|out(?:ubro)?|nov(?:embro)?|dec|dez(?:embro)?)"
    DATE_RANGE_PATTERN = re.compile(
        rf"(?P<start>{MONTH_PATTERN}?[\s/.-]*\d{{4}}|\d{{4}})\s*(?:[-–—]|até|a|to|until)\s*(?P<end>{MONTH_PATTERN}?[\s/.-]*\d{{4}}|\d{{4}}|atual|present|current|ongoing)",
        re.IGNORECASE,
    )
    SINGLE_YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")
    EXPECTED_YEAR_PATTERN = re.compile(
        r"(?:expected|previsto|prevista|graduation|class of)\D*((?:19|20)\d{2})",
        re.IGNORECASE,
    )

    # Áreas relevantes para tech
    RELEVANT_AREAS = [
        "ciência da computação",
        "computer science",
        "computação",
        "engenharia de software",
        "software engineering",
        "sistemas de informação",
        "information systems",
        "análise e desenvolvimento",
        "systems analysis",
        "engenharia da computação",
        "computer engineering",
        "tecnologia da informação",
        "information technology",
        "ciência de dados",
        "data science",
        "inteligência artificial",
        "artificial intelligence",
    ]

    def __init__(self, llm_client=None):
        """Inicializa extrator com cliente LLM opcional."""
        self.llm_client = llm_client
        self._log_file = (
            Path(__file__).resolve().parents[2] / "logs" / "education_events.log"
        )

    def _log(self, event: str, detail: str) -> None:
        """Registra evento de extração."""
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        with self._log_file.open("a", encoding="utf-8") as f:
            ts = datetime.now().isoformat(timespec="seconds")
            f.write(f"{ts}\t{event}\t{detail}\n")

    def extract_from_candidate(self, candidate: Candidate) -> List[Education]:
        """Extrai formações do texto do candidato."""
        fallback_text = candidate.raw_text or candidate.normalized_text or ""
        text_variants = []
        if candidate.raw_text:
            text_variants.append(candidate.raw_text)
        if candidate.normalized_text and candidate.normalized_text not in text_variants:
            text_variants.append(candidate.normalized_text)

        # 1. Tentar extração por regex/heurísticas
        educations: List[Education] = []
        for variant in text_variants:
            educations = self._extract_with_regex(variant)
            if educations:
                break

        # 2. Se não encontrou nada e temos LLM, usar como fallback
        if not educations and self.llm_client:
            self._log("fallback_llm", f"candidate={candidate.name}")
            educations = self._extract_with_llm(fallback_text, candidate.name)

        self._log("extracted", f"candidate={candidate.name} count={len(educations)}")
        return educations

    def _extract_with_regex(self, text: str) -> List[Education]:
        """Extração baseada em regex e heurísticas."""
        educations = []

        # Encontrar seção de educação
        section_text = self._find_education_section(text)
        if not section_text:
            return educations

        # Dividir em blocos de formação
        blocks = self._split_into_blocks(section_text)

        for block in blocks:
            edu = self._parse_education_block(block)
            if edu:
                educations.append(edu)

        return educations

    def _find_education_section(self, text: str) -> Optional[str]:
        """Encontra o texto da seção de educação."""
        lines = text.split("\n")

        # Procurar início da seção
        start_idx = None
        for i, line in enumerate(lines):
            for pattern in self.SECTION_PATTERNS:
                if re.search(pattern, line):
                    start_idx = i + 1
                    break
            if start_idx:
                break

        if start_idx is None:
            return None

        # Procurar fim da seção
        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            for pattern in self.SECTION_END_PATTERNS:
                if re.match(pattern, lines[i].strip()):
                    end_idx = i
                    break
            if end_idx < len(lines):
                break

        return "\n".join(lines[start_idx:end_idx])

    def _split_into_blocks(self, text: str) -> List[str]:
        """Divide texto em blocos de formação individual."""
        blocks = []
        current_block: List[str] = []

        lines = text.split("\n")

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if current_block and (
                self._contains_degree(stripped)
                or self._looks_like_structured_entry(stripped)
            ):
                blocks.append("\n".join(current_block))
                current_block = [stripped]
            else:
                current_block.append(stripped)

        if current_block:
            blocks.append("\n".join(current_block))

        return [b for b in blocks if b]

    def _looks_like_structured_entry(self, line: str) -> bool:
        if ("|" in line or " - " in line) and self._contains_degree(line):
            return True
        if line.startswith(("-", "•", "*")) and self._contains_degree(line):
            return True
        return False

    def _contains_degree(self, text: str) -> bool:
        """Verifica se texto contém menção a grau acadêmico."""
        text_lower = text.lower()
        for degree_type, patterns in self.DEGREE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return True
        return False

    def _parse_education_block(self, block: str) -> Optional[Education]:
        """Parse um bloco de texto em Education."""
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            return None

        structured_parts = [
            part.strip("-• ")
            for part in re.split(r"\s*[|•]\s*", lines[0])
            if part.strip()
        ]
        if len(structured_parts) >= 2:
            primary_line = " | ".join(structured_parts)
        else:
            primary_line = lines[0]

        # Identificar componentes
        degree = self._extract_degree(primary_line)
        institution = None
        year = self._extract_year(block)
        status = self._extract_status(block)

        if len(structured_parts) >= 2:
            if not degree:
                degree = structured_parts[0]
            if not institution:
                institution = structured_parts[1]
            if len(structured_parts) >= 3 and not year:
                year = self._extract_year(" ".join(structured_parts[2:]))

        if not institution:
            remaining_lines = lines[1:] if len(lines) > 1 else lines
            institution = self._extract_institution(remaining_lines)

        block_lower = " ".join(lines).lower()

        if not degree:
            return None

        if not institution and not year:
            noise_terms = [
                "conhecimento",
                "habilidade",
                "skill",
                "competência",
                "competencia",
            ]
            if any(term in block_lower for term in noise_terms):
                return None

        return Education(
            degree=degree, institution=institution, completion_year=year, status=status
        )

    def _extract_degree(self, text: str) -> Optional[str]:
        """Extrai grau/curso do texto."""
        text_lower = text.lower()

        # Tentar identificar tipo de grau e área
        degree_type = None
        for dtype, patterns in self.DEGREE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    degree_type = dtype
                    break
            if degree_type:
                break

        if not degree_type:
            return None

        # Tentar extrair linha completa que contém o grau
        lines = text.split("\n")
        for line in lines:
            if any(
                pattern in line.lower()
                for patterns in self.DEGREE_PATTERNS.values()
                for pattern in patterns
            ):
                # Limpar e retornar
                cleaned = line.strip()
                # Remover pipes e datas
                cleaned = re.sub(r"\|\s*\d{4}", "", cleaned)
                cleaned = re.sub(r"\d{4}\s*[-–—]\s*\d{4}", "", cleaned)
                return cleaned[:150]  # Limitar tamanho

        return degree_type.capitalize()

    def _extract_institution(self, lines: List[str]) -> Optional[str]:
        """Extrai instituição de ensino."""
        for line in lines:
            lowered = line.lower()
            if any(term in lowered for term in self.INSTITUTION_HINTS):
                cleaned = re.sub(r"\d{4}", "", line)
                cleaned = re.sub(r"[|\-–—]\s*$", "", cleaned)
                return cleaned.strip()[:120]

            # Siglas curtas em caixa alta (ex: MIT, USP)
            token = re.sub(r"[^A-Za-z]", "", line)
            if token.isupper() and 2 <= len(token) <= 6:
                return line.strip()[:60]

        return None

    def _extract_year(self, text: str) -> Optional[str]:
        """Extrai ano de conclusão ou período."""
        match = self.DATE_RANGE_PATTERN.search(text)
        if match:
            end_token = match.group("end")
            year = self._sanitize_year_token(end_token)
            if year:
                return year

        expected_match = self.EXPECTED_YEAR_PATTERN.search(text)
        if expected_match:
            year = self._sanitize_year_token(expected_match.group(1))
            if year:
                return year

        for token in reversed(self.SINGLE_YEAR_PATTERN.findall(text)):
            year = self._sanitize_year_token(token)
            if year:
                return year

        return None

    def _sanitize_year_token(self, token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        match = self.SINGLE_YEAR_PATTERN.search(token)
        if not match:
            return None
        year = int(match.group(0))
        current_year = datetime.now().year
        if 1960 <= year <= current_year + 5:
            return str(year)
        return None

    def _extract_status(self, text: str) -> str:
        """Extrai status da formação."""
        text_lower = text.lower()

        for status, patterns in self.STATUS_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return status

        # Default: se tem ano no passado, assumir completo
        year_str = self._extract_year(text)
        if year_str:
            year = int(year_str)
            if year <= datetime.now().year:
                return "completed"
            else:
                return "in_progress"

        return "completed"

    def _extract_with_llm(self, text: str, candidate_name: str) -> List[Education]:
        """Fallback usando LLM para extração estruturada."""
        if not self.llm_client:
            return []

        prompt = f"""Extraia a formação acadêmica do seguinte currículo.

Para cada formação, identifique:
- Grau/Curso (ex: Bacharelado em Ciência da Computação)
- Instituição
- Ano de conclusão
- Status (completo/cursando/incompleto)

Retorne em formato estruturado, uma formação por linha:
GRAU | INSTITUIÇÃO | ANO | STATUS

Currículo:
{text[:3000]}

Formações extraídas:"""

        try:
            response = self.llm_client.call(
                prompt=prompt,
                model="gemini-2.0-flash-exp",
                max_tokens=500,
                temperature=0.1,
            )

            if not response or "error" in response.lower():
                return []

            # Parse resposta do LLM
            educations = []
            for line in response.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2:
                    educations.append(
                        Education(
                            degree=parts[0],
                            institution=parts[1] if parts[1] else None,
                            completion_year=parts[2] if len(parts) > 2 else None,
                            status=parts[3].lower() if len(parts) > 3 else "completed",
                        )
                    )

            return educations

        except Exception as e:
            self._log("llm_error", f"candidate={candidate_name} error={str(e)}")
            return []

    def get_highest_degree_level(self, educations: List[Education]) -> int:
        """Retorna nível do maior grau (para scoring)."""
        if not educations:
            return 0

        level_map = {
            "doutorado": 6,
            "mestrado": 5,
            "mba": 5,
            "especialização": 4,
            "bacharelado": 3,
            "licenciatura": 3,
            "tecnólogo": 2,
            "técnico": 1,
            "ensino médio": 0,
        }

        max_level = 0
        for edu in educations:
            degree_lower = edu.degree.lower()
            for degree_type, level in level_map.items():
                if degree_type in degree_lower:
                    max_level = max(max_level, level)
                    break

        return max_level

    def has_relevant_degree(self, educations: List[Education]) -> bool:
        """Verifica se possui formação relevante para tech."""
        for edu in educations:
            degree_lower = edu.degree.lower()
            for area in self.RELEVANT_AREAS:
                if area in degree_lower:
                    return True
        return False
