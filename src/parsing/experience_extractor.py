"""Extração de experiências profissionais de currículos.

Método híbrido:
 - Regex para detectar seções de experiência
 - Heurísticas para cargo, empresa, período
 - Cálculo de anos totais de experiência
 - Fallback LLM para casos complexos
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from src.core.models import Experience, Candidate


class ExperienceExtractor:
    """Extrai experiências profissionais de texto de currículo."""

    # Padrões para identificar seções de experiência
    SECTION_PATTERNS = [
        r"(?i)experiência\s+profissional",
        r"(?i)experiências?\s+profissionais?",
        r"(?i)histórico\s+profissional",
        r"(?i)trajetória\s+profissional",
        r"(?i)experiência",
        r"(?i)professional\s+experience",
        r"(?i)experience",
        r"(?i)work\s+experience",
        r"(?i)employment\s+history",
        r"(?i)career\s+history",
        r"(?i)professional\s+background",
    ]

    SECTION_END_PATTERNS = [
        r"(?i)formação|education|academics?",
        r"(?i)habilidades|skills",
        r"(?i)competências",
        r"(?i)certificações|certifications",
        r"(?i)projetos|projects",
        r"(?i)idiomas|languages",
        r"(?i)resumo|summary",
    ]

    # Padrões para detectar cargo | empresa | período
    # Formato comum: "Cargo | Empresa | Data"
    JOB_LINE_PATTERN = re.compile(
        r"(?P<role>[\w\s]+?)\s*[|\-–—]\s*(?P<company>[\w\s]+?)\s*[|\-–—]\s*(?P<period>[\d/\w\s\-–—]+)",
        re.IGNORECASE,
    )

    # Padrões de período (ex: Jan/2020 - Dez/2022, 2019-2021, Atual)
    MONTH_PATTERN = r"(?:jan(?:eiro)?|feb|fev(?:ereiro)?|mar(?:ço|ch)?|apr|abr(?:il)?|may|mai(?:o)?|jun(?:ho|e)?|jul(?:ho|y)?|aug|ago(?:sto)?|sep|set(?:embro)?|oct|out(?:ubro)?|nov(?:embro)?|dec|dez(?:embro)?)"

    DATE_PATTERN = re.compile(
        rf"(?P<start>(?:{MONTH_PATTERN}[\s/.-]*)?\d{{4}}|\d{{4}})\s*(?:[-–—]|até|a|to)\s*(?P<end>(?:{MONTH_PATTERN}[\s/.-]*)?\d{{4}}|\d{{4}}|atual|present|current|ongoing)",
        re.IGNORECASE,
    )

    # Padrões de duração explícita (ex: "2 anos", "3 years")
    DURATION_PATTERN = re.compile(
        r"(?P<years>\d+(?:[.,]\d+)?)\s*(?:anos?|years?)", re.IGNORECASE
    )

    # Cargos comuns para validação
    COMMON_ROLES = [
        "desenvolvedor",
        "developer",
        "engenheiro",
        "engineer",
        "analista",
        "analyst",
        "programador",
        "programmer",
        "arquiteto",
        "architect",
        "tech lead",
        "líder técnico",
        "gerente",
        "manager",
        "coordenador",
        "coordinator",
        "consultor",
        "consultant",
        "especialista",
        "specialist",
        "estagiário",
        "intern",
        "trainee",
        "junior",
        "pleno",
        "sênior",
        "senior",
        "staff",
    ]

    BULLET_PREFIXES = ("- ", "-", "•", "* ", "*", "· ", "·", "• ", "– ", "–")
    COMPANY_SEPARATORS = re.compile(r"(?:@|\sem\s|\sat\s)", re.IGNORECASE)
    COMPANY_HINTS = [
        "empresa",
        "company",
        "corp",
        "inc",
        "ltda",
        "s.a",
        "startup",
        "solutions",
        "group",
        "consulting",
        "labs",
        "studio",
    ]

    def __init__(self, llm_client=None):
        """Inicializa extrator com cliente LLM opcional."""
        self.llm_client = llm_client
        self._log_file = (
            Path(__file__).resolve().parents[2] / "logs" / "experience_events.log"
        )

    def _log(self, event: str, detail: str) -> None:
        """Registra evento de extração."""
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        with self._log_file.open("a", encoding="utf-8") as f:
            ts = datetime.now().isoformat(timespec="seconds")
            f.write(f"{ts}\t{event}\t{detail}\n")

    def extract_from_candidate(self, candidate: Candidate) -> List[Experience]:
        """Extrai experiências do texto do candidato."""
        # Trabalhar preferindo texto bruto para preservar acentuação
        fallback_text = candidate.raw_text or candidate.normalized_text or ""
        text_variants = []
        if candidate.raw_text:
            text_variants.append(candidate.raw_text)
        if candidate.normalized_text and candidate.normalized_text not in text_variants:
            text_variants.append(candidate.normalized_text)

        # 1. Tentar extração por regex/heurísticas
        experiences: List[Experience] = []
        for variant in text_variants:
            experiences = self._extract_with_regex(variant)
            if experiences:
                break

        # 2. Se não encontrou nada e temos LLM, usar como fallback
        if not experiences and self.llm_client:
            self._log("fallback_llm", f"candidate={candidate.name}")
            experiences = self._extract_with_llm(fallback_text, candidate.name)

        self._log("extracted", f"candidate={candidate.name} count={len(experiences)}")
        return experiences

    def _extract_with_regex(self, text: str) -> List[Experience]:
        """Extração baseada em regex e heurísticas."""
        experiences = []

        # Encontrar seção de experiência
        section_text = self._find_experience_section(text)
        if not section_text:
            return experiences

        # Dividir em blocos de experiência (por linhas em branco ou bullets)
        blocks = self._split_into_blocks(section_text)

        for block in blocks:
            exp = self._parse_experience_block(block)
            if exp:
                experiences.append(exp)

        return experiences

    def _find_experience_section(self, text: str) -> Optional[str]:
        """Encontra o texto da seção de experiência."""
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

        # Procurar fim da seção (próximo título ou fim do documento)
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
        """Divide texto em blocos de experiência individual."""
        blocks = []
        current_block: List[str] = []

        lines = text.split("\n")

        for line in lines:
            stripped = line.strip()

            if not stripped:
                if current_block:
                    current_block.append("")
                continue

            if self._starts_new_block(stripped, current_block):
                blocks.append("\n".join(l for l in current_block if l.strip()))
                current_block = [stripped]
            else:
                current_block.append(stripped)

        if current_block:
            blocks.append("\n".join(l for l in current_block if l.strip()))

        return [b for b in blocks if b]

    def _starts_new_block(self, line: str, current_block: List[str]) -> bool:
        if not current_block:
            return False

        normalized = line.lstrip("-•*· ").strip()

        if self.JOB_LINE_PATTERN.match(line):
            return True

        # Linhas inteiras em maiúsculas tendem a ser novos cargos
        if normalized.isupper() and len(normalized) > 4:
            return True

        # Bullet indicando potencial novo bloco (exige estrutura mínima)
        if line.startswith(self.BULLET_PREFIXES):
            if self._has_role_keyword(normalized) and (
                self.DATE_PATTERN.search(line)
                or "|" in line
                or re.search(r"\d{4}", line)
            ):
                return True
            return False

        # Presença de palavras-chave de cargo seguida ou não de período
        if self._has_role_keyword(normalized):
            if re.search(r"\d{4}|atual|present|current", line, re.IGNORECASE):
                return True
            if "|" in line or "@" in line or " - " in line:
                return True
            if len(normalized.split()) <= 6:
                return True

        if self._is_likely_role(normalized) and re.search(r"\d{4}", line):
            return True

        return False

    def _has_role_keyword(self, text: str) -> bool:
        text_lower = text.lower()
        return any(role_keyword in text_lower for role_keyword in self.COMMON_ROLES)

    def _parse_experience_block(self, block: str) -> Optional[Experience]:
        """Parse um bloco de texto em Experience."""
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            return None

        first_line_clean = lines[0].lstrip("-•*· ").strip()
        if any(
            re.match(pattern, lines[0], re.IGNORECASE)
            for pattern in self.SECTION_PATTERNS
        ):
            return None
        if not first_line_clean:
            return None
        if lines[0].startswith(self.BULLET_PREFIXES) and not self._has_role_keyword(
            first_line_clean
        ):
            return None

        # Primeira linha normalmente contém cargo | empresa | período
        first_line = lines[0]

        # Tentar pattern estruturado
        match = self.JOB_LINE_PATTERN.match(first_line)
        role = None
        company = None
        period = None

        if match:
            role = match.group("role").strip()
            company = match.group("company").strip()
            period = match.group("period").strip()
        else:
            role, company, period = self._parse_unstructured_line(first_line)

        if not role:
            role = first_line

        # Validar se parece um cargo válido
        if not self._is_likely_role(role):
            return None

        if not company:
            company = self._extract_company_from_lines(lines)

        if not period:
            period = self._extract_period_from_lines(lines)

        # Descrição: resto do bloco
        description = "\n".join(lines[1:]) if len(lines) > 1 else None

        return Experience(
            role=role, company=company, duration=period, description=description
        )

    def _parse_unstructured_line(
        self, line: str
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse linha não estruturada tentando identificar componentes."""
        # Tentar separadores comuns
        parts = re.split(r"[|\-–—]", line)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 3:
            return parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            # Tentar decidir se segundo é empresa ou data
            if self.DATE_PATTERN.search(parts[1]):
                return parts[0], None, parts[1]
            else:
                return parts[0], parts[1], None
        elif len(parts) == 1:
            return parts[0], None, None

        return line, None, None

    def _extract_company_from_lines(self, lines: List[str]) -> Optional[str]:
        for line in lines[1:]:
            match = self.COMPANY_SEPARATORS.search(line)
            if match:
                candidate = line[match.end() :].strip(" -|,.")
                if candidate:
                    return candidate[:120]

            parts = re.split(r"[|,]", line)
            for part in parts:
                cleaned = part.strip()
                if not cleaned:
                    continue
                if any(hint in cleaned.lower() for hint in self.COMPANY_HINTS):
                    return cleaned[:120]

        return None

    def _extract_period_from_lines(self, lines: List[str]) -> Optional[str]:
        for line in lines:
            match = self.DATE_PATTERN.search(line)
            if match:
                return match.group(0).strip()

            if self.DURATION_PATTERN.search(line):
                return line.strip()

        # Procurar por anos isolados
        year_matches = re.findall(r"(?:19|20)\d{2}", " ".join(lines))
        if len(year_matches) >= 2:
            return "-".join(year_matches[:2])

        return None

    def _is_likely_role(self, text: str) -> bool:
        """Verifica se texto parece ser um cargo."""
        text_lower = text.lower()

        # Verificar se contém palavra-chave de cargo
        for role_keyword in self.COMMON_ROLES:
            if role_keyword in text_lower:
                return True

        # Rejeitar se for muito curto ou muito longo
        if len(text) < 5 or len(text) > 100:
            return False

        # Rejeitar se tiver caracteres estranhos demais
        if len(re.findall(r"[^\w\s\-/]", text)) > 5:
            return False

        return True

    def _extract_with_llm(self, text: str, candidate_name: str) -> List[Experience]:
        """Fallback usando LLM para extração estruturada."""
        if not self.llm_client:
            return []

        prompt = f"""Extraia as experiências profissionais do seguinte currículo.

Para cada experiência, identifique:
- Cargo/função
- Empresa
- Período (duração ou datas)
- Breve descrição (se houver)

Retorne em formato estruturado, uma experiência por linha:
CARGO | EMPRESA | PERÍODO | DESCRIÇÃO

Currículo:
{text[:3000]}

Experiências extraídas:"""

        try:
            response = self.llm_client.call(
                prompt=prompt,
                model="gemini-2.0-flash-exp",
                max_tokens=800,
                temperature=0.1,
            )

            if not response or "error" in response.lower():
                return []

            # Parse resposta do LLM
            experiences = []
            for line in response.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    experiences.append(
                        Experience(
                            role=parts[0],
                            company=parts[1] if parts[1] else None,
                            duration=parts[2] if parts[2] else None,
                            description=parts[3] if len(parts) > 3 else None,
                        )
                    )

            return experiences

        except Exception as e:
            self._log("llm_error", f"candidate={candidate_name} error={str(e)}")
            return []

    def calculate_total_years(self, experiences: List[Experience]) -> float:
        """Calcula total de anos de experiência."""
        total_years = 0.0

        for exp in experiences:
            years = self._parse_duration_to_years(exp.duration)
            total_years += years

        return round(total_years, 1)

    def _parse_duration_to_years(self, duration: Optional[str]) -> float:
        """Converte string de duração em anos."""
        if not duration:
            return 0.0

        # Tentar padrão explícito (ex: "2 anos")
        match = self.DURATION_PATTERN.search(duration)
        if match:
            value = match.group("years").replace(",", ".")
            try:
                return float(value)
            except ValueError:
                return 0.0

        # Tentar calcular de datas
        match = self.DATE_PATTERN.search(duration)
        if match:
            start = match.group("start")
            end = match.group("end")

            # Parse ano inicial
            start_year = self._extract_year(start)

            # Parse ano final (ou ano atual se "atual")
            if end.lower() in ["atual", "present", "current"]:
                end_year = datetime.now().year
            else:
                end_year = self._extract_year(end)

            if start_year and end_year:
                years = end_year - start_year
                # Se mesmo ano, considerar pelo menos 0.5
                return max(years, 0.5)

        # Fallback: assumir 1 ano se temos período mas não conseguimos parsear
        return 1.0

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extrai ano de string de data."""
        # Procurar 4 dígitos consecutivos
        match = re.search(r"(\d{4})", date_str)
        if match:
            return int(match.group(1))
        return None

    def infer_seniority(self, total_years: float, role: str) -> str:
        """Infere senioridade baseado em anos e cargo."""
        role_lower = role.lower()

        # Checar se cargo já indica senioridade
        if any(term in role_lower for term in ["sênior", "senior", "sr"]):
            return "senior"
        if any(term in role_lower for term in ["pleno", "mid", "middle"]):
            return "mid"
        if any(
            term in role_lower
            for term in ["júnior", "junior", "jr", "estagiário", "intern"]
        ):
            return "junior"

        # Inferir por anos de experiência
        if total_years >= 5:
            return "senior"
        elif total_years >= 2:
            return "mid"
        else:
            return "junior"
