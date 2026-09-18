# =============================================================
# AI Medical Report Assistant — One-Command Startup
# Run this from the project ROOT directory:
#   .\run.ps1
# =============================================================

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  AI Medical Report Assistant - Startup  " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# --- Check .env exists ---
if (-not (Test-Path "backend\.env")) {
    Write-Host "[ERROR] backend\.env not found." -ForegroundColor Red
    Write-Host "  Copy backend\.env.example -> backend\.env and fill in your credentials." -ForegroundColor Yellow
    exit 1
}

# --- Activate virtual environment ---
$venvPaths = @(".\.venv\Scripts\Activate.ps1", ".\.venv310\Scripts\Activate.ps1", ".\venv\Scripts\Activate.ps1")
$activated = $false
foreach ($p in $venvPaths) {
    if (Test-Path $p) {
        Write-Host "[1/3] Activating virtual environment: $p" -ForegroundColor Green
        & $p
        $activated = $true
        break
    }
}
if (-not $activated) {
    Write-Host "[WARN] No virtual environment found. Using system Python." -ForegroundColor Yellow
}

# --- Start Backend in background ---
Write-Host "[2/3] Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn main:app --reload --port 8000" -PassThru

Start-Sleep -Seconds 3

# --- Start Frontend ---
Write-Host "[3/3] Starting React frontend on http://localhost:5173 ..." -ForegroundColor Green
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Both servers are starting up!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs -> http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend -> http://localhost:5173" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop both servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
Write-Host "Servers stopped." -ForegroundColor Green
