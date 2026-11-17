@echo off
title SchoolGPT Server - RSR Technologies
cd /d "%~dp0"
echo ====================================================================
echo  SchoolGPT - RSR Technologies ^| AI for Education
echo  Smart * Reliable * Instant Answers
echo  Starting backend on http://0.0.0.0:8000 ...
echo  Mobile app connection: http://192.168.1.2:8000
echo ====================================================================
"C:\Users\HarishRuler\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
