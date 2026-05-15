@echo off
:: FRIDAY Windows installer

echo [FRIDAY Installer]
echo ==================

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.11+ from python.org
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install FRIDAY
echo Installing FRIDAY...
pip install -e ".[dev]"

:: Create default config
echo Creating default config...
echo agent:
echo   model: gpt-4 > friday.yaml
echo   temperature: 0.7 >> friday.yaml
echo gateway: >> friday.yaml
echo   channels: >> friday.yaml
echo     - telegram >> friday.yaml
echo memory: >> friday.yaml
echo   db_path: friday_memory.db >> friday.yaml

echo.
echo [FRIDAY installed successfully!]
echo.
echo Next steps:
echo   1. Edit friday.yaml with your API keys
echo   2. Run: friday --setup
echo   3. Run: friday --chat
echo.
pause
