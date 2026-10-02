$ErrorActionPreference = 'Stop'

Write-Host "Starting AegisAI AutoForge backend..." -ForegroundColor Cyan
$backend = Start-Process powershell -PassThru -ArgumentList '-NoExit', '-Command', 'python -m uvicorn app.main:app --reload --app-dir backend'

Start-Sleep -Seconds 2

Write-Host "Starting AegisAI AutoForge frontend..." -ForegroundColor Cyan
npm start

try {
    Wait-Process -Id $backend.Id
}
finally {
    if (-not $backend.HasExited) {
        Stop-Process -Id $backend.Id -Force
    }
}
