@echo off
echo ============================================================
echo    AI Study Assistant - Installation Script
echo ============================================================
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo.
echo Step 2: Creating virtual environment (optional but recommended)...
echo Do you want to create a virtual environment? (Y/N)
set /p CREATE_VENV=
if /i "%CREATE_VENV%"=="Y" (
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated
)

echo.
echo Step 3: Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Step 4: Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo Step 5: Creating configuration file...
if not exist ".env" (
    copy .env.example .env
    echo Created .env configuration file
) else (
    echo .env already exists, skipping...
)

echo.
echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo IMPORTANT: You need to install OLLAMA separately
echo.
echo 1. Download OLLAMA from: https://ollama.ai/download
echo 2. Install OLLAMA
echo 3. Open a NEW terminal and run: ollama pull phi3:mini
echo.
echo For Core i3 laptops, use one of these models:
echo    - phi3:mini (3.8GB) - RECOMMENDED - Good balance
echo    - llama3.2:1b (1.3GB) - Lighter, faster but less capable
echo.
echo After installing OLLAMA, you can:
echo    - Run: python setup.py     (to verify everything)
echo    - Run: python main.py      (to start the assistant)
echo    - Run: python demo.py      (to see examples)
echo.
pause
