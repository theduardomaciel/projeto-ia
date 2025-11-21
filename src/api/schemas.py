"""
Schemas Pydantic para validação de requisições e respostas da API.

Estes schemas definem o contrato da API e garantem type safety.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class StructuredJobRequest(BaseModel):
    """
    Schema para requisição de vaga estruturada (modo avançado).

    Permite ao usuário definir diretamente os requisitos da vaga
    sem precisar enviar um arquivo de texto.
    """

    area: str = Field(..., description="Área da vaga", min_length=1)
    position: str = Field(..., description="Cargo/posição", min_length=1)
    seniority: str = Field(
        ...,
        description="Nível de senioridade",
        pattern="^(estagio|junior|pleno|senior|especialista|lideranca)$",
    )
    hard_skills: List[str] = Field(
        ..., description="Lista de hard skills obrigatórias", min_length=1
    )
    soft_skills: List[str] = Field(
        default_factory=list, description="Lista de soft skills desejadas"
    )
    additional_info: str = Field(
        default="",
        description="Informações adicionais (cultura, benefícios, diferenciais)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "area": "Tecnologia",
                "position": "Desenvolvedor Backend Sênior",
                "seniority": "senior",
                "hard_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "soft_skills": ["Liderança", "Comunicação", "Trabalho em equipe"],
                "additional_info": "Startup em crescimento, cultura ágil, home office flexível",
            }
        }


class CandidateResult(BaseModel):
    """
    Resultado da análise de um candidato.

    Estrutura alinhada com CandidateResult do frontend (web/src/lib/types.ts).
    """

    candidate_name: str = Field(..., description="Nome do candidato")
    hard_skills: List[str] = Field(
        default_factory=list, description="Lista de hard skills identificadas"
    )
    soft_skills: List[str] = Field(
        default_factory=list, description="Lista de soft skills identificadas"
    )
    match_score: float = Field(..., description="Pontuação de aderência à vaga (0-100)")
    explanation: str = Field(
        ..., description="Justificativa da pontuação gerada por LLM"
    )
    ranking_position: int = Field(..., description="Posição no ranking (1-based)")
    global_score: float | None = Field(
        None, description="Score absoluto agregado (hard+soft+experience+education)"
    )
    final_score: float | None = Field(
        None,
        description="Score combinado calculado no frontend (ex: 0.6*match + 0.4*global_norm)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "candidate_name": "João Silva",
                "hard_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "soft_skills": ["Comunicação", "Trabalho em equipe", "Liderança"],
                "match_score": 87.5,
                "explanation": (
                    "João possui forte experiência em Python (5 anos) e domínio "
                    "de FastAPI, tecnologias essenciais para a vaga. Experiência "
                    "com Docker demonstra conhecimento em DevOps, um diferencial importante."
                ),
                "ranking_position": 1,
                "global_score": 7.1,
                "final_score": 0.6 * 87.5 + 0.4 * (7.1 / 10 * 100),
            }
        }


class AnalyzeResponse(BaseModel):
    """
    Resposta completa da análise de candidatos.

    Retorna lista ordenada de candidatos ranqueados.
    """

    data: List[CandidateResult] = Field(
        ..., description="Lista de candidatos ranqueados (melhor para pior)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "candidate_name": "João Silva",
                        "hard_skills": ["Python", "FastAPI"],
                        "soft_skills": ["Comunicação"],
                        "match_score": 87.5,
                        "explanation": "Forte experiência em Python...",
                        "ranking_position": 1,
                    },
                    {
                        "candidate_name": "Maria Santos",
                        "hard_skills": ["JavaScript", "React"],
                        "soft_skills": ["Trabalho em equipe"],
                        "match_score": 72.3,
                        "explanation": "Boa base em desenvolvimento web...",
                        "ranking_position": 2,
                    },
                ]
            }
        }


class HealthResponse(BaseModel):
    """Resposta do health check."""

    status: str
    service: Optional[str] = None
