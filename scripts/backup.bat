@echo off
REM Backup script for Windows (PowerShell alternative)

setlocal enabledelayedexpansion

set "BACKUP_DIR=backups"
set "CONTAINER_NAME=chatbot-backend"

REM Get date and time for filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "BACKUP_FILE=chatbot_backup_%datetime:~0,8%_%datetime:~8,6%.tar.gz"

echo Starting backup process...
echo.

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Check if container is running
docker ps | findstr /C:"%CONTAINER_NAME%" >nul
if errorlevel 1 (
    echo Error: Container %CONTAINER_NAME% is not running
    exit /b 1
)

REM Backup ChromaDB data
echo Backing up ChromaDB data...
docker exec %CONTAINER_NAME% tar -czf /tmp/data_backup.tar.gz /app/data

REM Copy to host
echo Copying backup to host...
docker cp %CONTAINER_NAME%:/tmp/data_backup.tar.gz %BACKUP_DIR%/%BACKUP_FILE%

REM Cleanup temporary file in container
docker exec %CONTAINER_NAME% rm /tmp/data_backup.tar.gz

echo.
echo Backup created successfully!
echo File: %BACKUP_DIR%\%BACKUP_FILE%
echo.

REM Keep only last 7 backups
echo Cleaning old backups (keeping last 7)...
for /f "skip=7 delims=" %%F in ('dir /b /o-d "%BACKUP_DIR%\chatbot_backup_*.tar.gz" 2^>nul') do (
    del "%BACKUP_DIR%\%%F"
)

echo Backup process completed!
pause
