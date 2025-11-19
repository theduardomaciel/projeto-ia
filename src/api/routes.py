"""
Rotas da API - endpoints para análise de currículos.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.api.schemas import AnalyzeResponse, CandidateResult
from src.api.service import AnalysisService

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


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_candidates(
    resumes: List[UploadFile] = File(
        ..., description="Arquivos de currículos (.txt ou .pdf)"
    ),
    job_text: Optional[str] = Form(None, description="Descrição da vaga como texto"),
    job_file: Optional[UploadFile] = File(
        None, description="Arquivo com descrição da vaga"
    ),
) -> AnalyzeResponse:
    """
    Analisa currículos em relação a uma vaga e retorna ranking de candidatos.

    **Parâmetros:**
    - `resumes`: Lista de arquivos de currículos (texto ou PDF)
    - `job_text`: Descrição da vaga como string (opcional se job_file fornecido)
    - `job_file`: Arquivo com descrição da vaga (opcional se job_text fornecido)

    **Retorna:**
    - Lista de candidatos ranqueados com pontuações e justificativas
    """
    logger.info(f"📥 Recebida requisição de análise: {len(resumes)} currículos")

    # Validar entradas
    if not resumes:
        raise HTTPException(status_code=400, detail="Nenhum currículo fornecido")

    if not job_text and not job_file:
        raise HTTPException(
            status_code=400,
            detail="Forneça job_text ou job_file com a descrição da vaga",
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

            if job_file:
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
