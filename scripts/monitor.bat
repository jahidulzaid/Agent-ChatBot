@echo off
REM Monitoring script for Windows

echo ================================================
echo    Agentic RAG Chatbot - System Status
echo ================================================
echo.

REM Container Status
echo === Container Status ===
docker-compose ps
echo.

REM Resource Usage
echo === Resource Usage ===
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo.

REM Backend Health Check
echo === Backend Health ===
curl -s http://localhost:8000/health
if %errorlevel% equ 0 (
    echo Backend is healthy
) else (
    echo Backend is not responding
)
echo.

REM Frontend Health Check
echo === Frontend Health ===
curl -s -o nul -w "Status: %%{http_code}" http://localhost:3000
echo.
echo.

REM Recent Backend Logs
echo === Recent Backend Logs (last 10 lines) ===
docker-compose logs --tail=10 backend
echo.

REM Disk Usage
echo === Disk Usage ===
dir /s backend\data
echo.

echo ================================================
echo Monitoring complete!
echo ================================================
pause
