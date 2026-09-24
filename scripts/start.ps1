# Quick Launcher for NhanThuat Executive Studio on Windows PowerShell
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "   KÍCH HOẠT NHÂN THUẬT & BUSINESSOS EXECUTIVE STUDIO     " -ForegroundColor Yellow
Write-Host "===========================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[WARNING] Không tìm thấy .venv/Scripts/python.exe. Sử dụng python từ PATH..." -ForegroundColor Yellow
    $VenvPython = "python"
}

Write-Host "[INFO] Sử dụng Python interpreter: $VenvPython" -ForegroundColor Green
& $VenvPython (Join-Path $RepoRoot "scripts\run_web_dashboard.py") @args
