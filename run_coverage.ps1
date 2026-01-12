# ========================================================================
# Run Tests with Coverage Report
# ========================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  VOID WALKER - TEST & COVERAGE RUNNER" -ForegroundColor Cyan
Write-Host "========================================================================`n" -ForegroundColor Cyan

# Check if coverage is installed
$pipList = pip list 2>&1 | Out-String
if ($pipList -notmatch "coverage") {
    Write-Host "[*] Installing coverage.py..." -ForegroundColor Yellow
    pip install coverage
}

# Run tests with coverage
Write-Host "[1/3] Running tests with coverage..." -ForegroundColor Yellow
coverage run -m pytest tests/ -v

# Generate coverage report
Write-Host "`n[2/3] Generating coverage report..." -ForegroundColor Yellow
coverage report -m

# Generate HTML report
Write-Host "`n[3/3] Creating HTML coverage report..." -ForegroundColor Yellow
coverage html
Write-Host "      ✓ HTML report: htmlcov/index.html" -ForegroundColor Green

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  COVERAGE COMPLETE!" -ForegroundColor Green
Write-Host "========================================================================`n" -ForegroundColor Cyan
