param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[test-local] .venv가 없어 bootstrap 실행" -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "bootstrap.ps1")
}

if ($PytestArgs.Count -eq 0) {
    & $pythonExe -m pytest -q
}
else {
    & $pythonExe -m pytest @PytestArgs
}
