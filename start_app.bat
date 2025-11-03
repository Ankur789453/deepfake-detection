@echo off
echo ================================================
echo    Deepfake Detection System - Full Startup
echo ================================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "python start_backend.py"

echo Waiting for backend to initialize...
timeout /t 10 /nobreak > nul

echo Starting Frontend...
start "Frontend" cmd /k "python start_frontend.py"

echo.
echo ================================================
echo Both servers are starting up!
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
echo.
echo Press any key to exit this window...
echo ================================================
pause > nul
