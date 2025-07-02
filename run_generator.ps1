# UQM Schema Generator - PowerShell Runner
# Usage: .\run_generator.ps1 [command] [args]

Write-Host "UQM Schema Generator" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    exit 1
}

# Setup virtual environment if needed
if (-not (Test-Path "venv")) {
    Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    & .\venv\Scripts\Activate.ps1
}

# Check if API key is set
if (-not $env:OPENROUTER_API_KEY) {
    Write-Host "⚠️  Warning: OPENROUTER_API_KEY environment variable not set" -ForegroundColor Yellow
    Write-Host "Please set it with: " -ForegroundColor Yellow -NoNewline
    Write-Host "`$env:OPENROUTER_API_KEY='your_api_key'" -ForegroundColor White
    Write-Host ""
}

# Handle different commands
switch ($args[0]) {
    "setup" {
        python setup.py
        break
    }
    "test" {
        python setup.py test
        break
    }
    "preview" {
        python setup.py preview
        break
    }
    "single" {
        if (-not $args[1]) {
            Write-Host "Usage: .\run_generator.ps1 single <query_id>" -ForegroundColor Yellow
            break
        }
        python uqm_schema_generator.py single $args[1]
        break
    }
    "range" {
        if (-not $args[2]) {
            Write-Host "Usage: .\run_generator.ps1 range <start_id> <count>" -ForegroundColor Yellow
            break
        }
        python uqm_schema_generator.py range $args[1] $args[2]
        break
    }
    "all" {
        Write-Host "Processing all queries..." -ForegroundColor Green
        python uqm_schema_generator.py range 1 100
        break
    }
    default {
        if ($args.Count -eq 0) {
            Write-Host "Running setup check..." -ForegroundColor Green
            python setup.py
            Write-Host ""
            Write-Host "Running generator with default settings (first 10 queries)..." -ForegroundColor Green
            python uqm_schema_generator.py
        } else {
            python uqm_schema_generator.py @args
        }
        break
    }
}

Write-Host ""
Write-Host "✅ Done! Check the jsonResult folder for generated files." -ForegroundColor Green

# Keep window open
Read-Host "Press Enter to continue"
