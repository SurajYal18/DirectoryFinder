@echo off
title Directory Finder - Standalone Service
cd /d "%~dp0"
echo ========================================================
echo   Starting Directory Finder on http://127.0.0.1:8001
echo   Model: Gemini 3.5 Flash-Lite
echo ========================================================
start "" "http://127.0.0.1:8001"
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
pause
