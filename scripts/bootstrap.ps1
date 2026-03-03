$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[bootstrap] $Message" -ForegroundColor Cyan
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Step "프로젝트 루트: $repoRoot"

$venvPath = Join-Path $repoRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Step "가상환경(.venv) 생성"
    python -m venv .venv
}
else {
    Write-Step "가상환경(.venv) 이미 존재"
}

Write-Step "pip 최신화"
& $pythonExe -m pip install --upgrade pip

Write-Step "개발 의존성 설치(requirements-dev.txt)"
& $pipExe install -r requirements-dev.txt

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Step ".env 파일 생성(.env.example 복사)"
        Copy-Item ".env.example" ".env"
    }
    else {
        Write-Step ".env.example 없음 -> 기본 .env 생성"
        @(
            "FLASK_ENV=development"
            "FLASK_APP=run.py"
            "SECRET_KEY=change-this-secret"
            "MONGO_URI=mongodb://localhost:27017/jungle_soop"
        ) | Set-Content ".env"
    }
}
else {
    Write-Step ".env 파일 이미 존재"
}

Write-Host ""
Write-Host "완료: 개발 시작 준비가 끝났습니다." -ForegroundColor Green
Write-Host "다음 명령(현재 PowerShell 세션): .\.venv\Scripts\Activate.ps1"
