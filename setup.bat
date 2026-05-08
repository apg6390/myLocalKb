@echo off
setlocal enabledelayedexpansion

echo === myLocalKb Setup ===

REM Check Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama is not installed.
    echo Install it from: https://ollama.com/download/windows
    exit /b 1
)
echo [OK] Ollama found

REM Pull models
echo.
echo Pulling qwen3:4b (Apache 2.0, ~2.5 GB)...
ollama pull qwen3:4b

echo Pulling nomic-embed-text (Apache 2.0, ~274 MB)...
ollama pull nomic-embed-text

REM Python deps
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Data directories
if not exist "data\documents" mkdir data\documents
if not exist "data\chroma_db" mkdir data\chroma_db

echo.
echo === Setup complete ===
echo.
echo To start the app, open two PowerShell windows:
echo   Window 1: ollama serve
echo   Window 2: uvicorn backend.main:app --host 127.0.0.1 --port 8000
echo.
echo Then open: http://localhost:8000
