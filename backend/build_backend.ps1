$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $root "backend"
$venvPython = Join-Path $backendPath "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
  $pythonExe = $venvPython
} else {
  $pythonExe = "python"
}

Push-Location $backendPath

& $pythonExe -m pip install --upgrade pip | Out-Null
& $pythonExe -m pip install -r requirements.txt | Out-Null
& $pythonExe -m pip install pyinstaller | Out-Null

& $pythonExe -m PyInstaller `
  --noconfirm `
  --onefile `
  --name damas-backend `
  run_backend.py

if (!(Test-Path ".\dist\damas-backend.exe")) {
  throw "No se genero dist\damas-backend.exe"
}

Pop-Location
