#!/usr/bin/env pwsh
# Chrona - Configuration automatique de l'app mobile
# Usage: .\setup-mobile.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration App Mobile Chrona      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Détecter l'IP WiFi
Write-Host "[1/4] Détection de l'adresse IP..." -ForegroundColor Yellow
$wifiIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*"}).IPAddress

if ($wifiIP) {
    Write-Host "  ✓ IP WiFi détectée: $wifiIP" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Impossible de détecter l'IP WiFi" -ForegroundColor Yellow
    $wifiIP = Read-Host "  Entrez votre adresse IP manuellement"
}

# Créer le fichier .env pour mobile
Write-Host "`n[2/4] Configuration de l'app mobile..." -ForegroundColor Yellow
$mobileEnvPath = "apps/mobile/.env"

@"
# Configuration API Backend
EXPO_PUBLIC_API_URL=http://${wifiIP}:8000

# Environnement
EXPO_PUBLIC_ENV=development
"@ | Out-File -FilePath $mobileEnvPath -Encoding UTF8

Write-Host "  ✓ Fichier .env créé: $mobileEnvPath" -ForegroundColor Green

# Vérifier Node.js et npm
Write-Host "`n[3/4] Vérification des dépendances..." -ForegroundColor Yellow
Set-Location apps/mobile

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installation des packages npm..." -ForegroundColor Yellow
    npm install
    Write-Host "  ✓ Packages installés" -ForegroundColor Green
} else {
    Write-Host "  ✓ Packages déjà installés" -ForegroundColor Green
}

# Configurer le pare-feu Windows
Write-Host "`n[4/4] Configuration du pare-feu..." -ForegroundColor Yellow
Write-Host "  ⚠ Nécessite les droits administrateur" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Exécutez cette commande en tant qu'Administrateur:" -ForegroundColor Cyan
Write-Host "  netsh advfirewall firewall add rule name=`"Chrona Backend API`" dir=in action=allow protocol=TCP localport=8000" -ForegroundColor White
Write-Host ""

Set-Location ../..

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Configuration terminée !              " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Configurez le pare-feu (commande ci-dessus)" -ForegroundColor White
Write-Host ""
Write-Host "  2. Démarrez l'app mobile:" -ForegroundColor White
Write-Host "     cd apps/mobile" -ForegroundColor Cyan
Write-Host "     npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Pour Android émulateur:" -ForegroundColor White
Write-Host "     npm run android" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Pour appareil physique:" -ForegroundColor White
Write-Host "     • Scannez le QR code avec Expo Go" -ForegroundColor White
Write-Host "     • Backend accessible sur: http://${wifiIP}:8000" -ForegroundColor White
Write-Host ""
Write-Host "Test de connexion:" -ForegroundColor Yellow
Write-Host "  Depuis votre téléphone, ouvrez:" -ForegroundColor White
Write-Host "  http://${wifiIP}:8000/health" -ForegroundColor Cyan
Write-Host "  Résultat attendu: {`"status`":`"ok`",`"db`":`"ok`"}" -ForegroundColor White
Write-Host ""
