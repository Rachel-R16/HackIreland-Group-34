@echo off

echo Stopping any existing Flask processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq flask*" 2>NUL
timeout /t 1 /nobreak >NUL

echo Setting up environment variables...
set FLASK_APP=api
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONUNBUFFERED=1

echo Starting Flask server on port 5001...
flask run --port 5001 --debug --host=0.0.0.0
