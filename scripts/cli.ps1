$pythonScript = ".\dgisim\src\cli.py"
$env:PYTHONPATH = ";$(Get-Location)\dgisim"
$venvPath = ".\venv"

if (Test-Path -Path $venvPath) {
    # Run python script
    try {
        python $pythonScript
    } catch {
        Write-Host "Could not run python script"
        exit 1
    }

} else {
    Write-Host "Virtual environment not found. Please run venv.ps1"
    exit 1
}
