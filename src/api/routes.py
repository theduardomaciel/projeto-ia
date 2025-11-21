"""
Rotas da API - endpoints para análise de currículos.
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.api.schemas import AnalyzeResponse, CandidateResult, StructuredJobRequest
from src.api.service import AnalysisService
from src.core.config import DATA_DIR

logger = logging.getLogger(__name__)

router = APIRouter()

# Singleton do serviço de análise
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """Factory para obter instância única do serviço de análise."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


@router.get("/health")
async def api_health():
    """Health check específico da API."""
    return {"status": "healthy", "api": "recruitment-pipeline"}


@router.get("/skills")
async def get_skills() -> Dict[str, List[str]]:
    """
    Retorna listas de hard skills e soft skills disponíveis no sistema.

    **Retorna:**
    - `hard_skills`: Lista de todas as hard skills cadastradas
    - `soft_skills`: Lista de todas as soft skills cadastradas
    """
    try:
        skills_path = DATA_DIR / "config" / "skills.json"

        if not skills_path.exists():
            logger.warning(f"skills.json não encontrado em {skills_path}")
            return {"hard_skills": [], "soft_skills": []}

        with open(skills_path, encoding="utf-8") as f:
            skills_data = json.load(f)

        # Coletar todas as hard skills de todas as categorias
        hard_skills = []
        for category_skills in skills_data.get("hard_skills", {}).values():
            if isinstance(category_skills, list):
                hard_skills.extend(category_skills)

        # Coletar todas as soft skills de todas as categorias
        soft_skills = []
        for category_skills in skills_data.get("soft_skills", {}).values():
            if isinstance(category_skills, list):
                soft_skills.extend(category_skills)

        # Remover duplicatas e ordenar
        hard_skills = sorted(set(hard_skills))
        soft_skills = sorted(set(soft_skills))

        logger.info(
            f"✅ Skills carregadas: {len(hard_skills)} hard, {len(soft_skills)} soft"
        )

        return {"hard_skills": hard_skills, "soft_skills": soft_skills}

    except Exception as e:
        logger.error(f"❌ Erro ao carregar skills: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Erro ao carregar skills: {str(e)}"
        )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_candidates(
    resumes: List[UploadFile] = File(
        ..., description="Arquivos de currículos (.txt ou .pdf)"
    ),
    job_text: Optional[str] = Form(None, description="Descrição da vaga como texto"),
    job_file: Optional[UploadFile] = File(
        None, description="Arquivo com descrição da vaga"
    ),
    structured_job: Optional[str] = Form(
        None, description="Vaga estruturada em JSON (modo avançado)"
    ),
) -> AnalyzeResponse:
    """
    Analisa currículos em relação a uma vaga e retorna ranking de candidatos.

    **Parâmetros:**
    - `resumes`: Lista de arquivos de currículos (texto ou PDF)
    - `job_text`: Descrição da vaga como string (opcional)
    - `job_file`: Arquivo com descrição da vaga (opcional)
    - `structured_job`: Vaga estruturada em JSON no formato StructuredJobRequest (modo avançado)

    **Nota:** Forneça job_text, job_file OU structured_job

    **Retorna:**
    - Lista de candidatos ranqueados com pontuações e justificativas
    """
    logger.info(f"📥 Recebida requisição de análise: {len(resumes)} currículos")

    # Validar entradas
    if not resumes:
        raise HTTPException(status_code=400, detail="Nenhum currículo fornecido")

    if not job_text and not job_file and not structured_job:
        raise HTTPException(
            status_code=400,
            detail="Forneça job_text, job_file ou structured_job com a descrição da vaga",
        )

    try:
        # Criar diretório temporário para processar arquivos
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Salvar currículos temporariamente
            resume_paths: List[Path] = []
            for i, resume in enumerate(resumes):
                # Validar tipo de arquivo
                if not resume.filename:
                    continue

                ext = Path(resume.filename).suffix.lower()
                if ext not in [".txt", ".pdf"]:
                    logger.warning(
                        f"⚠️  Arquivo {resume.filename} ignorado (formato não suportado)"
                    )
                    continue

                # Salvar arquivo
                resume_path = temp_path / f"curriculo_{i:02d}{ext}"
                content = await resume.read()
                resume_path.write_bytes(content)
                resume_paths.append(resume_path)
                logger.debug(f"   ✓ Salvo: {resume_path.name}")

            if not resume_paths:
                raise HTTPException(
                    status_code=400,
                    detail="Nenhum currículo válido (.txt ou .pdf) fornecido",
                )

            # Processar descrição da vaga
            job_path: Optional[Path] = None

            if structured_job:
                # Modo avançado: converter vaga estruturada em texto
                try:
                    job_data = json.loads(structured_job)
                    structured = StructuredJobRequest(**job_data)

                    # Gerar descrição textual da vaga estruturada usando
                    # cabeçalhos compatíveis com o RequirementsExtractor
                    # (padrões: Requisitos Obrigatórios / Requisitos Desejáveis / Diferenciais)
                    job_description_lines = [
                        f"Vaga: {structured.position}",
                        f"Área: {structured.area}",
                        f"Senioridade: {structured.seniority}",
                        "",
                        "Requisitos Obrigatórios:",
                    ]

                    # Hard skills consideradas obrigatórias
                    for skill in structured.hard_skills:
                        job_description_lines.append(f"- {skill}")

                    if structured.soft_skills:
                        job_description_lines.append("")
                        job_description_lines.append("Requisitos Desejáveis:")
                        for skill in structured.soft_skills:
                            job_description_lines.append(f"- {skill}")

                    if structured.additional_info:
                        job_description_lines.append("")
                        job_description_lines.append("Diferenciais:")
                        # Preserva texto adicional (pode conter skills extras)
                        job_description_lines.append(structured.additional_info)

                    job_description = "\n".join(job_description_lines) + "\n"

                    job_path = temp_path / "job_description.txt"
                    job_path.write_text(job_description, encoding="utf-8")
                    logger.debug(
                        f"   ✓ Vaga estruturada convertida ({len(structured.hard_skills)} hard skills, {len(structured.soft_skills)} soft skills)"
                    )

                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"JSON inválido em structured_job: {str(e)}",
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erro ao processar vaga estruturada: {str(e)}",
                    )

            elif job_file:
                job_path = temp_path / "job_description.txt"
                content = await job_file.read()
                job_path.write_bytes(content)
                logger.debug(f"   ✓ Vaga salva de arquivo: {job_file.filename}")
            elif job_text:
                job_path = temp_path / "job_description.txt"
                job_path.write_text(job_text, encoding="utf-8")
                logger.debug(f"   ✓ Vaga salva de texto ({len(job_text)} chars)")

            # Validar job_path
            if job_path is None:
                raise HTTPException(
                    status_code=500,
                    detail="Erro interno: job_path não foi definido corretamente",
                )

            # Executar pipeline de análise
            logger.info("🤖 Iniciando pipeline de análise...")
            service = get_analysis_service()
            results = await service.analyze(job_path, resume_paths)

            logger.info(f"✅ Análise concluída: {len(results)} candidatos processados")

            return AnalyzeResponse(data=results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro durante análise: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar análise: {str(e)}",
        )
