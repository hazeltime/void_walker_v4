# ========================================================================
# Void Walker - Build Single EXE
# ========================================================================
# This script compiles the Python application into a standalone .exe file
# using PyInstaller, allowing you to run the app without Python installed.
# ========================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  VOID WALKER - EXE BUILD SCRIPT" -ForegroundColor Cyan
Write-Host "========================================================================`n" -ForegroundColor Cyan

# 1. Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "      ✗ Python not found in PATH!" -ForegroundColor Red
    Write-Host "      Install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# 2. Install PyInstaller
Write-Host "`n[2/5] Checking PyInstaller..." -ForegroundColor Yellow
$pipList = pip list 2>&1 | Out-String
if ($pipList -match "pyinstaller") {
    Write-Host "      ✓ PyInstaller already installed" -ForegroundColor Green
} else {
    Write-Host "      Installing PyInstaller..." -ForegroundColor Cyan
    pip install pyinstaller
    Write-Host "      ✓ PyInstaller installed" -ForegroundColor Green
}

# 3. Clean previous builds
Write-Host "`n[3/5] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "      ✓ Removed build/" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "      ✓ Removed dist/" -ForegroundColor Green
}
if (Test-Path "VoidWalker.exe") {
    Remove-Item -Force "VoidWalker.exe"
    Write-Host "      ✓ Removed old VoidWalker.exe" -ForegroundColor Green
}

# 4. Build executable
Write-Host "`n[4/5] Building single-file executable..." -ForegroundColor Yellow
Write-Host "      This may take 30-60 seconds..." -ForegroundColor Gray

try {
    pyinstaller --clean void_walker.spec 2>&1 | Out-Null
    Write-Host "      ✓ Build completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "      ✗ Build failed!" -ForegroundColor Red
    Write-Host "      Run 'pyinstaller void_walker.spec' manually to see errors" -ForegroundColor Red
    exit 1
}

# 5. Move and verify
Write-Host "`n[5/5] Finalizing..." -ForegroundColor Yellow
if (Test-Path "dist\VoidWalker.exe") {
    Move-Item "dist\VoidWalker.exe" "VoidWalker.exe" -Force
    $fileSize = (Get-Item "VoidWalker.exe").Length / 1MB
    Write-Host "      ✓ Executable ready: VoidWalker.exe ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "      ✗ Executable not found in dist/" -ForegroundColor Red
    exit 1
}

# Cleanup
Write-Host "`n[*] Cleaning up temporary files..." -ForegroundColor Gray
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

Write-Host "`n========================================================================" -ForegroundColor Cyan
Write-Host "  BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "`n  ✓ Executable: " -NoNewline -ForegroundColor Green
Write-Host "VoidWalker.exe" -ForegroundColor Yellow
Write-Host "  ✓ Size: " -NoNewline -ForegroundColor Green
Write-Host "$([math]::Round($fileSize, 2)) MB" -ForegroundColor Yellow
Write-Host "`n  Usage:" -ForegroundColor Cyan
Write-Host "    .\VoidWalker.exe              # Interactive menu" -ForegroundColor Gray
Write-Host "    .\VoidWalker.exe C:\path      # Direct scan" -ForegroundColor Gray
Write-Host "    .\VoidWalker.exe --help       # Show all options" -ForegroundColor Gray
Write-Host "`n========================================================================`n" -ForegroundColor Cyan
