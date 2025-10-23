#!/usr/bin/env pwsh
# Chrona - Script d'installation automatique (Windows)
# Usage: .\setup-dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Chrona - Installation Développement  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les prérequis
Write-Host "[1/8] Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier Podman
try {
    $podmanVersion = podman --version
    Write-Host "  ✓ Podman détecté: $podmanVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erreur: Podman n'est pas installé" -ForegroundColor Red
    Write-Host "    Installez Podman depuis: https://podman.io/getting-started/installation" -ForegroundColor Yellow
    exit 1
}

# Vérifier si la machine Podman est démarrée
Write-Host "[2/8] Vérification de Podman machine..." -ForegroundColor Yellow
$podmanStatus = podman machine list 2>&1 | Select-String "running"
if (-not $podmanStatus) {
    Write-Host "  Démarrage de Podman machine..." -ForegroundColor Yellow
    podman machine start
}
Write-Host "  ✓ Podman machine active" -ForegroundColor Green

# Vérifier Python
try {
    $pythonVersion = python --version
    Write-Host "  ✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erreur: Python n'est pas installé" -ForegroundColor Red
    exit 1
}

# Vérifier Node.js
try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js détecté: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erreur: Node.js n'est pas installé" -ForegroundColor Red
    exit 1
}

# Générer les clés JWT
Write-Host "`n[3/8] Génération des clés JWT RS256..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "  Création de l'environnement virtuel Python..." -ForegroundColor Yellow
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
pip install -q cryptography python-dotenv

if (-not (Test-Path "jwt_private_key.pem")) {
    python tools/generate_keys.py
    Write-Host "  ✓ Clés JWT générées" -ForegroundColor Green
} else {
    Write-Host "  ✓ Clés JWT déjà présentes" -ForegroundColor Green
}

# Générer SECRET_KEY
Write-Host "`n[4/8] Génération de la SECRET_KEY..." -ForegroundColor Yellow
$secretKey = python tools/generate_secret_key.py
Write-Host "  ✓ SECRET_KEY générée" -ForegroundColor Green

# Créer les fichiers .env
Write-Host "`n[5/8] Configuration des variables d'environnement..." -ForegroundColor Yellow

# Backend .env
if (-not (Test-Path ".env")) {
    @"
DATABASE_URL=postgresql+asyncpg://chrona:chrona@db:5432/chrona
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
SECRET_KEY=$secretKey
LOG_LEVEL=debug
ALLOW_CREDENTIALS=false
ALLOWED_METHODS=*
ALLOWED_HEADERS=*
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/app/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/app/jwt_public_key.pem
EMAIL_PROVIDER=console
EMAIL_FROM_ADDRESS=noreply@chrona.dev
EMAIL_FROM_NAME=Chrona Dev
OTP_SUBJECT=Votre code de vérification Chrona
OTP_EXPIRY_MINUTES=10
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  ✓ backend/.env créé" -ForegroundColor Green
} else {
    Write-Host "  ✓ backend/.env déjà présent" -ForegroundColor Green
}

Set-Location ..

# Backoffice .env
if (-not (Test-Path "apps/backoffice/.env")) {
    "VITE_API_URL=http://localhost:8000" | Out-File -FilePath "apps/backoffice/.env" -Encoding UTF8
    Write-Host "  ✓ apps/backoffice/.env créé" -ForegroundColor Green
} else {
    Write-Host "  ✓ apps/backoffice/.env déjà présent" -ForegroundColor Green
}

# Kiosk .env
if (-not (Test-Path "apps/kiosk/.env")) {
    @"
VITE_API_URL=http://localhost:8000
VITE_KIOSK_ID=1
"@ | Out-File -FilePath "apps/kiosk/.env" -Encoding UTF8
    Write-Host "  ✓ apps/kiosk/.env créé" -ForegroundColor Green
} else {
    Write-Host "  ✓ apps/kiosk/.env déjà présent" -ForegroundColor Green
}

# Démarrer les services Podman
Write-Host "`n[6/8] Démarrage des services (Backend + PostgreSQL)..." -ForegroundColor Yellow
podman compose up -d db backend
Write-Host "  Attente du démarrage de la base de données..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "  ✓ Services démarrés" -ForegroundColor Green

# Appliquer les migrations
Write-Host "`n[7/8] Application des migrations de base de données..." -ForegroundColor Yellow
podman exec chrona_core-backend-1 alembic upgrade head
Write-Host "  ✓ Migrations appliquées" -ForegroundColor Green

# Créer un kiosk et générer sa clé API
Write-Host "`n[8/8] Configuration du kiosk..." -ForegroundColor Yellow
podman exec chrona_core-backend-1 python tools/seed_kiosk.py | Out-Null

# Générer la clé API du kiosk
$apiKeyOutput = podman exec chrona_core-backend-1 python tools/generate_kiosk_api_key.py 1
$apiKey = ($apiKeyOutput | Select-String "API KEY:").ToString() -replace ".*API KEY:\s*", ""

if ($apiKey) {
    # Ajouter la clé au .env du kiosk
    $kioskEnv = Get-Content "apps/kiosk/.env"
    if ($kioskEnv -notmatch "VITE_KIOSK_API_KEY") {
        "VITE_KIOSK_API_KEY=$apiKey" | Add-Content "apps/kiosk/.env"
    }
    Write-Host "  ✓ Clé API kiosk configurée" -ForegroundColor Green
}

# Créer un utilisateur admin
Write-Host "`nCréation de l'utilisateur administrateur..." -ForegroundColor Yellow
podman exec chrona_core-backend-1 python tools/create_admin_user.py --email "admin@example.com" --password "Passw0rd!" --role admin 2>&1 | Out-Null
Write-Host "  ✓ Admin créé (admin@example.com / Passw0rd!)" -ForegroundColor Green

# Obtenir l'adresse IP WiFi
$wifiIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*"}).IPAddress

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Installation terminée avec succès !   " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services disponibles:" -ForegroundColor Yellow
Write-Host "  • Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "  • Documentation:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "Compte administrateur:" -ForegroundColor Yellow
Write-Host "  • Email:    admin@example.com" -ForegroundColor White
Write-Host "  • Password: Passw0rd!" -ForegroundColor White
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host "  1. Démarrer le back-office:" -ForegroundColor White
Write-Host "     .\start-backoffice.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Démarrer le kiosk:" -ForegroundColor White
Write-Host "     .\start-kiosk.ps1" -ForegroundColor Cyan
Write-Host ""
if ($wifiIP) {
    Write-Host "  3. Pour l'app mobile, utilisez l'IP WiFi:" -ForegroundColor White
    Write-Host "     EXPO_PUBLIC_API_URL=http://$wifiIP:8000" -ForegroundColor Cyan
}
Write-Host ""
