@echo off
title SchoolGPT Server - RSR Technologies
cd /d "%~dp0"
echo ====================================================================
echo  SchoolGPT - RSR Technologies ^| AI for Education
echo  Smart * Reliable * Instant Answers
echo ====================================================================
echo.
echo Active IPv4 Addresses on your machine:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    echo   -^> http:%%a:8000
)
echo.
echo ====================================================================
echo Starting SchoolGPT backend server on http://0.0.0.0:8000 ...
echo Keep this window open while using the mobile app or web!
echo ====================================================================
echo.
"C:\Users\HarishRuler\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
