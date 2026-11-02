# A project-local setup/start path for Windows PowerShell 5.1 and PowerShell 7.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)

function Invoke-Checked {
    param([scriptblock]$Action)
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "Command failed (exit $LASTEXITCODE). Read the message above." }
}

try {
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        Write-Host 'Creating the Python 3.12 environment...'
        Invoke-Checked { py -3.12 -m venv .venv }
    }
    $MizanPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
    $LockHash = (Get-FileHash 'requirements-windows.lock' -Algorithm SHA256).Hash
    $InstallMarker = '.venv\mizan-windows-lock.sha256'
    if (-not (Test-Path $InstallMarker) -or (Get-Content $InstallMarker -Raw).Trim() -ne $LockHash) {
        Write-Host 'Installing verified Windows dependencies. Please wait for completion...'
        Invoke-Checked { & $MizanPython -m pip install --require-hashes -r requirements-windows.lock }
        Set-Content -Path $InstallMarker -Value $LockHash -Encoding ASCII
    }
    Invoke-Checked { & $MizanPython -m pip install --no-deps -e . }
    $CheckModels = @'
from pathlib import Path
import sys
try:
    from nhanes_ai.inference import ModelRegistry
    ModelRegistry(Path('models'))
except Exception:
    sys.exit(1)
'@
    & $MizanPython -c $CheckModels
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Downloading and verifying the older public NHANES files...'
        Invoke-Checked { & $MizanPython scripts/download_data.py }
        Write-Host 'Training the eight-input models. Each algorithm will print its progress...'
        Invoke-Checked { & $MizanPython -m nhanes_ai.train --jobs 2 }
    }
    Write-Host 'Open http://localhost:8501 . Keep this window open; Ctrl+C stops the app.'
    Invoke-Checked { & $MizanPython -m streamlit run app/main.py }
} catch {
    Write-Host $_ -ForegroundColor Red
    exit 1
}
