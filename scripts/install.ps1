# Rozetka installer (PowerShell)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $root

Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv
& "$root\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$root\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# Desktop shortcut
$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = $WshShell.CreateShortcut("$desktop\Rozetka.lnk")
$shortcut.TargetPath = "$root\.venv\Scripts\pythonw.exe"
$shortcut.Arguments = "-m rozetka.main"
$shortcut.WorkingDirectory = $root
$shortcut.IconLocation = "$root\resources\icon.ico"
$shortcut.Save()

Write-Host "Installed. Shortcut created on Desktop." -ForegroundColor Green
