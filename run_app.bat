@echo off
echo ========================================
echo   Nagarik Connect - Starting Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo   Starting Flask Application
echo ========================================
echo.
echo Server will start at: http://localhost:5000
echo.
echo Admin Login: http://localhost:5000/admin
echo   Username: admin
echo   Password: admin@123
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the Flask app
python app.py

pause
