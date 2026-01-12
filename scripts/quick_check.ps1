# Fast validation - syntax + tests
param([switch]$Verbose)

$files = @("ui/menu.py", "core/engine.py", "data/database.py", "config/settings.py", "main.py")
foreach ($f in $files) {
    python -m py_compile $f 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "✗ $f" -ForegroundColor Red; exit 1 }
}
Write-Host "✓ Syntax OK" -ForegroundColor Green

$output = python tests/run_tests.py 2>&1 | Out-String
if ($Verbose) { Write-Host $output }
if ($output -match "Ran (\d+) tests.*OK") {
    Write-Host "✓ $($Matches[1]) tests passed" -ForegroundColor Green
} else {
    Write-Host "✗ Tests failed" -ForegroundColor Red
    exit 1
}
