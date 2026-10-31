Set-Location (Join-Path $PSScriptRoot "..")
$env:CODEWORLD_UI_DIR = (Resolve-Path frontend\dist).Path
$env:PYTHONPATH = (Resolve-Path backend).Path
if (-not $env:CODEWORLD_ALLOW_LOCAL) { $env:CODEWORLD_ALLOW_LOCAL = "1" }
.\.venv\Scripts\python -m uvicorn codeworld.api.main:app --port 8000
