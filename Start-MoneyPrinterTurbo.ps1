param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = Join-Path $PSScriptRoot 'MoneyPrinterTurbo'
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$logs = Join-Path $projectRoot 'logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null

function Test-Endpoint([string]$Url) {
    try { return (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 }
    catch { return $false }
}

if (-not (Test-Path -LiteralPath $python)) {
    throw 'Python environment is missing. Run uv sync --frozen inside MoneyPrinterTurbo first.'
}
if (-not (Test-Endpoint 'http://127.0.0.1:11434/api/tags')) {
    $ollamaPath = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
    if (-not (Test-Path -LiteralPath $ollamaPath)) {
        $ollamaPath = (Get-Command ollama -ErrorAction Stop).Source
    }
    Start-Process -FilePath $ollamaPath -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput "$logs\ollama.stdout.log" -RedirectStandardError "$logs\ollama.stderr.log" | Out-Null
}
if (-not (Test-Endpoint 'http://127.0.0.1:8501/_stcore/health')) {
    Start-Process -FilePath $python -ArgumentList '-m','streamlit','run','webui/Main.py','--server.address=127.0.0.1','--server.port=8501','--server.headless=true','--browser.gatherUsageStats=false','--server.showEmailPrompt=false' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput "$logs\webui.stdout.log" -RedirectStandardError "$logs\webui.stderr.log" | Out-Null
}
if (-not (Test-Endpoint 'http://127.0.0.1:8080/docs')) {
    Start-Process -FilePath $python -ArgumentList 'main.py' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput "$logs\api.stdout.log" -RedirectStandardError "$logs\api.stderr.log" | Out-Null
}
$deadline = (Get-Date).AddSeconds(60)
do {
    $ready = (Test-Endpoint 'http://127.0.0.1:8501/_stcore/health') -and (Test-Endpoint 'http://127.0.0.1:8080/docs') -and (Test-Endpoint 'http://127.0.0.1:11434/api/tags')
    if ($ready) { break }
    Start-Sleep -Seconds 1
} while ((Get-Date) -lt $deadline)
if (-not $ready) { throw "A service did not start. See logs in $logs" }
Write-Host 'MoneyPrinterTurbo: http://127.0.0.1:8501'
Write-Host 'API documentation: http://127.0.0.1:8080/docs'
if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:8501' -WindowStyle Hidden }
