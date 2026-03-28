# Bootstrap SAGE: venv + editable install (Windows PowerShell).
# Installs runtime + dev tools + optional Textual TUI (`sage tui`).
# Usage: .\startup.ps1 (from repo root)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
try {
    & $Python --version | Out-Null
} catch {
    Write-Error "[SAGE] Python not found. Install Python 3.10+ or set PYTHON to the executable."
    exit 1
}

if (-not (Test-Path .venv)) {
    Write-Host "[SAGE] Creating .venv with $Python ..."
    & $Python -m venv .venv
}

$Activate = Join-Path $Root ".venv\Scripts\Activate.ps1"
. $Activate

python -m pip install -U pip wheel setuptools
python -m pip install -e ".[dev,tui]"

Write-Host ""
Write-Host "[SAGE] OK — virtualenv ready at $Root\.venv"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "    sage doctor"
Write-Host "    sage                    # interactive shell"
Write-Host "    sage tui                # full-screen UI (Textual)"
Write-Host ""
Write-Host "Optional: `$env:SAGE_REPO_URL = 'https://github.com/your-org/your-fork'"
