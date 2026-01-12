# Auto commit and push with validation
param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Run quick check
.\scripts\quick_check.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

# Commit and push
git add -A
git commit -m $Message
git push origin main

Write-Host "✓ Committed and pushed" -ForegroundColor Green
