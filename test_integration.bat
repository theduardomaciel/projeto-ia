@echo off
REM Script de teste para Windows

echo ===========================================================
echo 🧪 TESTE DE INTEGRAÇÃO - API + FRONTEND
echo ===========================================================
echo.

REM Test 1: Verify Python imports
echo 📦 [1/5] Testando importações Python...
python -c "from src.api.main import app; from src.api.routes import router; from src.api.service import AnalysisService; from src.api.schemas import CandidateResult, AnalyzeResponse; print('   ✓ Todas as importações OK')"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Falha nas importações
    exit /b 1
)

REM Test 2: Check if required packages are installed
echo.
echo 📦 [2/5] Verificando dependências...
python -c "import fastapi; import uvicorn; print(f'   ✓ FastAPI {fastapi.__version__}'); print(f'   ✓ Uvicorn {uvicorn.__version__}')"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ FastAPI/Uvicorn não instalados
    exit /b 1
)

REM Test 3: Validate sample data exists
echo.
echo 📄 [3/5] Verificando arquivos de exemplo...
if exist "data\samples\job.txt" (
    echo    ✓ job.txt encontrado
) else (
    echo    ❌ job.txt não encontrado
    exit /b 1
)

dir /b "data\samples\curriculo_*.txt" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    ✓ Currículos encontrados
) else (
    echo    ❌ Nenhum currículo encontrado
    exit /b 1
)

REM Test 4: Check API script exists
echo.
echo 🚀 [4/5] Verificando script de API...
if exist "run_api.py" (
    echo    ✓ run_api.py presente
) else (
    echo    ❌ run_api.py não encontrado
    exit /b 1
)

REM Test 5: Check web dependencies
echo.
echo 🌐 [5/5] Verificando frontend...
if exist "web\node_modules" (
    echo    ✓ node_modules presente
) else (
    echo    ⚠ node_modules não encontrado (execute: cd web ^&^& pnpm install^)
)

if exist "web\package.json" (
    echo    ✓ package.json presente
) else (
    echo    ❌ package.json não encontrado
    exit /b 1
)

echo.
echo ===========================================================
echo ✅ TODOS OS TESTES BÁSICOS PASSARAM
echo ===========================================================
echo.
echo 📋 Próximos passos:
echo.
echo    1. Configure .env com API keys dos LLMs:
echo       copy .env.example .env
echo       REM Edite .env e adicione suas chaves
echo.
echo    2. Inicie o backend (Terminal 1^):
echo       python run_api.py --reload
echo.
echo    3. Inicie o frontend (Terminal 2^):
echo       cd web ^&^& pnpm dev
echo.
echo    4. Acesse:
echo       Frontend: http://localhost:5173
echo       API Docs: http://localhost:8000/docs
echo.
echo    5. Teste via curl (ou navegador^):
echo       curl http://localhost:8000/api/health
echo.
