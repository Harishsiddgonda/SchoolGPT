# SchoolGPT Backend Launcher - RSR Technologies
Set-Location $PSScriptRoot
$PythonPath = "C:\Users\HarishRuler\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " SchoolGPT - RSR Technologies | AI for Education" -ForegroundColor Yellow
Write-Host " Smart * Reliable * Instant Answers" -ForegroundColor Yellow
Write-Host " Starting backend on http://0.0.0.0:8000 ..." -ForegroundColor Green
Write-Host " Mobile app connection address: http://192.168.1.2:8000" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

& $PythonPath -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
