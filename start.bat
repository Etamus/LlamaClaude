@echo off
setlocal

cd /d "%~dp0"

:: ── 1. Iniciar llama-server (se necessário) ──────────────────────────────────
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-llamacpp.ps1"
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar llama-server. Verifique a saida acima.
    pause
    exit /b 1
)

:: ── 2. Obter nome do modelo carregado no llama-server ────────────────────────
for /f "usebackq delims=" %%M in (`powershell -NoProfile -Command "try { (Invoke-RestMethod -Uri http://localhost:8080/v1/models -TimeoutSec 5).data[0].id } catch { 'local-model' }" 2^>nul`) do set "OPENAI_MODEL=%%M"
if "%OPENAI_MODEL%"=="" set "OPENAI_MODEL=local-model"

:: ── 3. Configurar provider llama.cpp (OpenAI-compativel) ─────────────────────
set CLAUDE_CODE_USE_OPENAI=1
set OPENAI_BASE_URL=http://localhost:8080/v1
:: sem API key: llama-server nao exige autenticacao
set OPENAI_API_KEY=no-key

:: ── 4. Descobrir ctx-size REAL por slot (n_ctx / parallel) ──────────────────
:: Com --parallel 1, n_ctx_seq = n_ctx = 32768
:: A query retorna n_ctx total; com parallel=1 é igual ao por-slot
for /f "usebackq delims=" %%N in (`powershell -NoProfile -Command "try { $p = (New-Object System.Net.WebClient).DownloadString('http://127.0.0.1:8080/props') | ConvertFrom-Json; $p.n_ctx } catch { '32768' }"`) do set "OPENAI_CTX_SIZE=%%N"
if "%OPENAI_CTX_SIZE%"=="" set "OPENAI_CTX_SIZE=32768"

echo [llama.cpp] Provider: OPENAI_BASE_URL=%OPENAI_BASE_URL%  model=%OPENAI_MODEL%  ctx=%OPENAI_CTX_SIZE%

:: ── 4. Compilar se dist/cli.mjs nao existir ──────────────────────────────────
if not exist "%~dp0dist\cli.mjs" (
    echo [build] Compilando...
    call bun run build
    if errorlevel 1 (
        echo [ERRO] Falha na compilacao.
        pause
        exit /b 1
    )
)

:: ── 5. Executar o programa ────────────────────────────────────────────────────
node "%~dp0dist\cli.mjs" %*
