@echo off
cd /d "%~dp0"
title AuraMatrix AI
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

set PY=python
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo Python not found. Install it from https://www.python.org
        echo and tick "Add Python to PATH" during setup.
        pause
        exit /b 1
    )
    set PY=py
)

%PY% -c "import streamlit, requests, numpy" >nul 2>nul
if errorlevel 1 (
    echo Installing required libraries, please wait...
    %PY% -m pip install -r requirements.txt
)

echo.
echo Starting AuraMatrix AI... The browser will open automatically.
echo Close this window to stop.
echo.
%PY% -m streamlit run app.py
pause
