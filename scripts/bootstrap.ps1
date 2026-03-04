$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$venvPath = Join-Path $repoRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $pythonExe)) {
    python -m venv .venv
}

& $pythonExe -m pip install --upgrade pip
& $pipExe install -r requirements-dev.txt

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    }
    else {
        @(
            "FLASK_ENV=development"
            "FLASK_APP=run.py"
            "SECRET_KEY=change-this-secret"
            "MONGO_URI=mongodb://localhost:27017/jungle_soop"
        ) | Set-Content ".env"
    }
}
