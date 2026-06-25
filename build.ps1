Write-Host "[PyC-SOI] Preparing the environment..." -ForegroundColor Blue

Write-Host "Checking directory structure..."
New-Item -ItemType Directory -Force -Path lib, data, core, src_c | Out-Null

Write-Host "Compiling the math engine (src_c/category_grouper.c)..." -ForegroundColor Blue

gcc -shared -o lib/category_grouper_lib.dll -fPIC src_c/category_grouper.c -lm -O3 -march=native

if ($LastExitCode -eq 0) {
    Write-Host "[Success] The lib/category_grouper_lib.dll library is generated" -ForegroundColor Green
    
    Write-Host "Creating Python Virtual Environment (venv)..." -ForegroundColor Blue
    python -m venv venv

    Write-Host "Activating virtual environment and installing python libraries..." -ForegroundColor Blue
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
    } else {
        & .\venv\bin\Activate.ps1
    }
    pip install -r requirements.txt
    
    if ($LastExitCode -eq 0) {
        Write-Host "The environment is ready. To run, use: python main.py" -ForegroundColor Green
    } else {
        Write-Host "[Error] Error installing python libraries. Check python and pip." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[Error] Error compiling C code. Check GCC." -ForegroundColor Red
    exit 1
}