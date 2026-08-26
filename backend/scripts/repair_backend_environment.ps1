<#
Repairs VentureMind's local Python environment after Python has been upgraded,
moved, or removed. Run from PowerShell; it creates a stable venv outside OneDrive.
#>

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $env:USERPROFILE 'venvs\venturemind-backend'
$pythonPath = Join-Path $venvPath 'Scripts\python.exe'

Write-Host "Creating the VentureMind backend environment at: $venvPath" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $venvPath) | Out-Null

if (Test-Path $venvPath) {
    Remove-Item -LiteralPath $venvPath -Recurse -Force
}

py -3.12 -m venv $venvPath
& $pythonPath -m ensurepip --upgrade
& $pythonPath -m pip install --upgrade pip

Push-Location $projectRoot
try {
    & $pythonPath -m pip install -e .
    & $pythonPath -m alembic upgrade head
}
finally {
    Pop-Location
}

Write-Host ''
Write-Host 'Repair completed successfully.' -ForegroundColor Green
Write-Host 'Start the API with:' -ForegroundColor Green
Write-Host "& `"$pythonPath`" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
