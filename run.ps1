# run.ps1 — ativa o venv e executa a aplicação Flask
# Uso: abra o PowerShell na raiz do projeto e execute: .\run.ps1

# Verifica se o venv existe
if (-not (Test-Path .\venv\Scripts\Activate.ps1)) {
    Write-Error "Ambiente virtual não encontrado. Crie-o com: python -m venv venv"
    exit 1
}

# Ativa o venv
. .\venv\Scripts\Activate.ps1

# Exporta variável FLASK_APP e executa a app
$env:FLASK_APP = 'app.py'
Write-Host "Executando Flask (FLASK_APP=$env:FLASK_APP)..."
flask run
