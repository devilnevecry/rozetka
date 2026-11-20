# Build standalone exe with PyInstaller
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $root
& "$root\.venv\Scripts\python.exe" -m pip install pyinstaller
& "$root\.venv\Scripts\pyinstaller.exe" --noconfirm --windowed --icon=resources\icon.ico --name Rozetka --add-data "resources;resources" --paths src src/rozetka/main.py
Write-Host "Build complete. See dist\Rozetka\" -ForegroundColor Green
