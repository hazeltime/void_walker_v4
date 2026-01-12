# Quick test and build automation
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[1/3] Testing..." -ForegroundColor Yellow
$testOutput = python tests/run_tests.py 2>&1 | Out-String
if ($testOutput -match "FAILED|ERROR") {
    Write-Host "TESTS FAILED" -ForegroundColor Red
    exit 1
}
$testOutput -match "Ran (\d+) tests"
Write-Host "✓ $($Matches[1]) tests passed" -ForegroundColor Green

Write-Host "[2/3] Syntax check..." -ForegroundColor Yellow
python -m py_compile ui/menu.py core/engine.py data/database.py
Write-Host "✓ Syntax OK" -ForegroundColor Green

Write-Host "[3/3] Building exe..." -ForegroundColor Yellow
.\build_exe.ps1 | Out-Null
Write-Host "✓ Build complete" -ForegroundColor Green
