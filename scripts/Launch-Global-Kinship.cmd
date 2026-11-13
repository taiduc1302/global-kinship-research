@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10 or newer is required. Install Python from python.org.
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
)
set "PYTHONPATH=%CD%\src"
echo Starting Global Kinship Research locally on http://127.0.0.1:8765
echo This window must stay open. Close it to stop the local research server.
echo No family data is uploaded by the application.
%PYTHON_CMD% -m kinship serve --port 8765 --browser
if errorlevel 1 (
  echo Could not start the local server. Another app might already be using port 8765.
  pause
)
