$testsDir = ".\dgisim\tests"
$mypy_flags = "--check-untyped-defs"
$files_to_test = Get-ChildItem -Path $dir -Filter "test*.py"

Clear-Host

# Run tests
try {
    python -m unittest
} catch {
    Write-Error "Python unittest failed with the following error: $_"
    exit 1
}

# Loop through files and run mypy
foreach ($file in $files_to_test) {
    try {
        mypy "$dir\$file" $mypy_flags
    } catch {
        Write-Error "Mypy failed with the following error: $_"
        exit 1
    }
}
