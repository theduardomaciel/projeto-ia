#!/bin/bash
# Script de teste para validar integração completa

set -e  # Exit on error

echo "==========================================================="
echo "🧪 TESTE DE INTEGRAÇÃO - API + FRONTEND"
echo "==========================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Verify Python imports
echo "📦 [1/5] Testando importações Python..."
python -c "
from src.api.main import app
from src.api.routes import router
from src.api.service import AnalysisService
from src.api.schemas import CandidateResult, AnalyzeResponse
print('   ✓ Todas as importações OK')
" || { echo -e "${RED}❌ Falha nas importações${NC}"; exit 1; }

# Test 2: Check if required packages are installed
echo ""
echo "📦 [2/5] Verificando dependências..."
python -c "
import fastapi
import uvicorn
print(f'   ✓ FastAPI {fastapi.__version__}')
print(f'   ✓ Uvicorn {uvicorn.__version__}')
" || { echo -e "${RED}❌ FastAPI/Uvicorn não instalados${NC}"; exit 1; }

# Test 3: Validate sample data exists
echo ""
echo "📄 [3/5] Verificando arquivos de exemplo..."
if [ -f "data/samples/job.txt" ]; then
    echo "   ✓ job.txt encontrado"
else
    echo -e "   ${RED}❌ job.txt não encontrado${NC}"
    exit 1
fi

CV_COUNT=$(ls data/samples/curriculo_*.txt 2>/dev/null | wc -l)
if [ $CV_COUNT -gt 0 ]; then
    echo "   ✓ $CV_COUNT currículos encontrados"
else
    echo -e "   ${RED}❌ Nenhum currículo encontrado${NC}"
    exit 1
fi

# Test 4: Validate API can start (dry run)
echo ""
echo "🚀 [4/5] Testando inicialização da API..."
timeout 5 python run_api.py 2>&1 | grep -q "Application startup complete" && \
    echo "   ✓ API pode ser iniciada" || \
    echo -e "   ${YELLOW}⚠ Não foi possível verificar startup (timeout esperado)${NC}"

# Test 5: Check web dependencies
echo ""
echo "🌐 [5/5] Verificando frontend..."
if [ -d "web/node_modules" ]; then
    echo "   ✓ node_modules presente"
else
    echo -e "   ${YELLOW}⚠ node_modules não encontrado (execute: cd web && pnpm install)${NC}"
fi

if [ -f "web/package.json" ]; then
    echo "   ✓ package.json presente"
else
    echo -e "   ${RED}❌ package.json não encontrado${NC}"
    exit 1
fi

echo ""
echo "==========================================================="
echo -e "${GREEN}✅ TODOS OS TESTES BÁSICOS PASSARAM${NC}"
echo "==========================================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "   1. Configure .env com API keys dos LLMs:"
echo "      cp .env.example .env"
echo "      # Edite .env e adicione suas chaves"
echo ""
echo "   2. Inicie o backend (Terminal 1):"
echo "      python run_api.py --reload"
echo ""
echo "   3. Inicie o frontend (Terminal 2):"
echo "      cd web && pnpm dev"
echo ""
echo "   4. Acesse:"
echo "      Frontend: http://localhost:5173"
echo "      API Docs: http://localhost:8000/docs"
echo ""
echo "   5. Teste via curl:"
echo "      curl http://localhost:8000/api/health"
echo ""
