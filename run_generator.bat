@echo off
REM UQM Schema Generator - Batch Runner
REM Usage: run_generator.bat [command] [args]

echo UQM Schema Generator
echo ====================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist "venv\" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check if API key is set
if "%OPENROUTER_API_KEY%"=="" (
    echo Warning: OPENROUTER_API_KEY environment variable not set
    echo Please set it with: set OPENROUTER_API_KEY=your_api_key
    echo Or run: $env:OPENROUTER_API_KEY='your_api_key' in PowerShell
    echo.
)

REM Run setup if no arguments provided
if "%1"=="" (
    echo Running setup check...
    python setup.py
    echo.
    echo Running generator with default settings (first 10 queries)...
    python uqm_schema_generator.py
    goto end
)

REM Handle different commands
if "%1"=="setup" (
    python setup.py
    goto end
)

if "%1"=="test" (
    python setup.py test
    goto end
)

if "%1"=="preview" (
    python setup.py preview
    goto end
)

if "%1"=="single" (
    if "%2"=="" (
        echo Usage: run_generator.bat single <query_id>
        goto end
    )
    python uqm_schema_generator.py single %2
    goto end
)

if "%1"=="range" (
    if "%3"=="" (
        echo Usage: run_generator.bat range <start_id> <count>
        goto end
    )
    python uqm_schema_generator.py range %2 %3
    goto end
)

if "%1"=="all" (
    echo Processing all queries...
    python uqm_schema_generator.py range 1 100
    goto end
)

REM Default: run generator with arguments
python uqm_schema_generator.py %*

:end
echo.
echo Done! Check the jsonResult folder for generated files.
pause
