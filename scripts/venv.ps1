$venvPath = ".\venv"
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (Test-Path -Path $venvPath) {
    Write-Host "venv is already setup!"
    Write-Host "Press any key to continue..."
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
} else {
    Write-Host "Setting up venv, this may take a minute..."

    # Create virtual environment
    try {
        python -m venv .\venv
    } catch {
        Write-Host "Could not create virtual environment"
        exit 1
    }

    # Activate virtual environment
    try {
        . $activateScript
    } catch {
        Write-Host "Could not activate virtual environment"
        exit 1
    }

    # Install requirements
    try {
        pip install -r requirements.txt
    } catch {
        Write-Host "Could not install requirements"
        deactivate
        exit 1
    }
    
    # Finish up
    deactivate
    Write-Host "venv setup complete!"
}

Write-Host "Press any key to continue..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
