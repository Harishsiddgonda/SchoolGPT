# SchoolGPT Backend Server Launcher - RSR Technologies
Set-Location $PSScriptRoot
$PythonPath = "C:\Users\HarishRuler\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " SchoolGPT - RSR Technologies | AI for Education" -ForegroundColor Yellow
Write-Host " Smart * Reliable * Instant Answers" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Active IPv4 Addresses for Mobile App Connection:" -ForegroundColor Green
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254*" } | ForEach-Object {
    Write-Host "   -> http://$($_.IPAddress):8000" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Starting backend server on http://0.0.0.0:8000 ..." -ForegroundColor Yellow
Write-Host "Keep this terminal window open while using the mobile app or web!" -ForegroundColor White
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

& $PythonPath -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
