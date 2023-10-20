
$env:RNG_PLAYS = 5
$env:SHOW_PROGRESS=1
Write-host "#################### Unittest ####################\n" 
& ./venv/bin/coverage run -m unittest discover src/tests/
Write-host ""
Write-host "\n#################### Mypy ####################\n" 
& ./venv/bin/mypy src/ --check-untyped-defs 
Write-host ""
Write-host "\n#################### Coverage ####################\n"
& ./venv/bin/coverage report
& ./venv/bin/coverage html