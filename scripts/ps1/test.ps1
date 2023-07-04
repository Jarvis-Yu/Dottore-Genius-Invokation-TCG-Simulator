
$env:RNG_PLAYS = 5
Write-host "#################### Unittest ####################\n" 
& ./venv/bin/coverage run -m unittest 
Write-host ""
Write-host "\n#################### Mypy ####################\n" 
& ./venv/bin/mypy src/ --check-untyped-defs 
Write-host ""
Write-host "\n#################### Coverage ####################\n"
& ./venv/bin/coverage report