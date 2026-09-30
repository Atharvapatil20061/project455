@echo off
title Online Study Hub
echo ===================================================
echo     Starting 📚 Online Study Hub Web Platform...
echo ===================================================
echo.
echo Checking dependencies...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask not found. Installing requirements...
    python -m pip install -r requirements.txt
)

echo Starting Flask server...
echo Access the website at: http://127.0.0.1:5000
echo.
python app.py
pause
