
if (-not (Test-Path "venv")){
  python -m venv venv
}
& .\venv\bin\activate
& .\venv\bin\python.exe -m pip install -r requirements.txt
