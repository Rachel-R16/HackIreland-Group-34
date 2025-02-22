@echo off
echo Setting up environment variables...
set FLASK_APP=wsgi.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONUNBUFFERED=1

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python and try again.
    pause
    exit /b 1
)

REM Install requirements if needed
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
)

echo Starting Flask server...
python wsgi.py
