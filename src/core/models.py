"""
Modelos de dados principais do sistema
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Skill:
    """Representa uma habilidade (hard ou soft skill)"""

    name: str
    category: str  # 'hard' ou 'soft'
    confidence: float = 1.0  # Confiança da extração (0.0 a 1.0)
    source: str = "regex"  # 'regex', 'dictionary', 'llm'
    context: Optional[str] = None  # Contexto onde foi encontrada

    def __hash__(self):
        return hash(self.name.lower())

    def __eq__(self, other):
        if isinstance(other, Skill):
            return self.name.lower() == other.name.lower()
        return False


@dataclass
class Experience:
    """Representa uma experiência profissional"""

    role: str
    company: Optional[str] = None
    duration: Optional[str] = None  # Ex: "2 anos", "jan/2020 - dez/2022"
    description: Optional[str] = None
    skills_used: List[Skill] = field(default_factory=list)


@dataclass
class Education:
    """Representa formação acadêmica"""

    degree: str  # Ex: "Bacharelado em Ciência da Computação"
    institution: Optional[str] = None
    completion_year: Optional[str] = None
    status: str = "completed"  # 'completed', 'in_progress', 'incomplete'


@dataclass
class Candidate:
    """Representa um candidato completo"""

    name: str
    raw_text: str  # Texto original do currículo
    normalized_text: Optional[str] = None  # Texto normalizado para processamento

    # Informações extraídas
    contact: Optional[str] = None
    email: Optional[str] = None

    hard_skills: List[Skill] = field(default_factory=list)
    soft_skills: List[Skill] = field(default_factory=list)

    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)

    # Metadados
    file_path: Optional[str] = None
    parsed_at: datetime = field(default_factory=datetime.now)

    # Pontuação (preenchida pelo ScoringEngine)
    score: float = 0.0  # Score absoluto baseado em competências gerais
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    match_percentage: float = 0.0  # Percentual de match com requisitos da vaga (0-100)
    match_breakdown: Dict[str, float] = field(default_factory=dict)

    # Justificativa (preenchida pelo ExplainabilityEngine)
    explanation: Optional[str] = None

    def add_skill(self, skill: Skill) -> None:
        """Adiciona uma skill evitando duplicatas"""
        target_list = self.hard_skills if skill.category == "hard" else self.soft_skills
        if skill not in target_list:
            target_list.append(skill)

    def get_all_skills(self) -> List[Skill]:
        """Retorna todas as skills (hard + soft)"""
        return self.hard_skills + self.soft_skills

    def __str__(self) -> str:
        return f"Candidate(name='{self.name}', score={self.score:.1f}, skills={len(self.get_all_skills())})"


@dataclass
class JobRequirement:
    """Representa um requisito da vaga"""

    skill: str
    importance: str = "required"  # 'required', 'preferred', 'nice_to_have'
    weight: float = 1.0
    category: str = "hard"  # 'hard' ou 'soft'


@dataclass
class JobProfile:
    """Representa o perfil de uma vaga"""

    title: str
    description: str
    raw_text: str  # Texto original da vaga

    requirements: List[JobRequirement] = field(default_factory=list)

    # Configurações de pontuação
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "hard_skills": 0.6,
            "soft_skills": 0.2,
            "experience": 0.15,
            "education": 0.05,
        }
    )

    # Metadados
    file_path: Optional[str] = None
    parsed_at: datetime = field(default_factory=datetime.now)

    def add_requirement(
        self,
        skill: str,
        importance: str = "required",
        weight: float = 1.0,
        category: str = "hard",
    ) -> None:
        """Adiciona um requisito à vaga"""
        req = JobRequirement(
            skill=skill, importance=importance, weight=weight, category=category
        )
        self.requirements.append(req)

    def get_required_skills(self) -> List[str]:
        """Retorna lista de skills obrigatórias"""
        return [req.skill for req in self.requirements if req.importance == "required"]

    def get_preferred_skills(self) -> List[str]:
        """Retorna lista de skills preferenciais"""
        return [req.skill for req in self.requirements if req.importance == "preferred"]

    def __str__(self) -> str:
        return (
            f"JobProfile(title='{self.title}', requirements={len(self.requirements)})"
        )


@dataclass
class AnalysisResult:
    """Resultado completo da análise"""

    job_profile: JobProfile
    candidates: List[Candidate]
    ranked_candidates: List[Candidate] = field(default_factory=list)

    # Metadados da análise
    analyzed_at: datetime = field(default_factory=datetime.now)
    llm_provider: Optional[str] = None
    processing_time: Optional[float] = None  # em segundos

    def get_top_candidates(self, n: int = 5) -> List[Candidate]:
        """Retorna os top N candidatos"""
        return self.ranked_candidates[:n]

    def __str__(self) -> str:
        return f"AnalysisResult(job='{self.job_profile.title}', candidates={len(self.candidates)})"
