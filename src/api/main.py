"""
FastAPI application principal.

Expõe endpoints REST para o frontend web consumir o pipeline de análise.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia ciclo de vida da aplicação (startup/shutdown)."""
    logger.info("🚀 Iniciando API de Recrutamento Inteligente")
    yield
    logger.info("🛑 Encerrando API")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Apoio ao Recrutamento Inteligente",
    description=(
        "API para análise automatizada de currículos usando IA. "
        "Projeto acadêmico - UFAL IA 2025.1"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS para permitir acesso do frontend
# Em produção, ajustar origins para domínios específicos
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (Svelte)
        "http://localhost:4173",  # Vite preview
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Endpoint raiz - informações básicas da API."""
    return {
        "name": "Sistema de Apoio ao Recrutamento Inteligente - API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/health")
async def health_check():
    """Health check para monitoramento."""
    return {"status": "healthy", "service": "recruitment-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
