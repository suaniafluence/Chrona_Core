#!/usr/bin/env pwsh
# Chrona - Démarrage rapide du Kiosk
# Usage: .\start-kiosk.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "     Démarrage du Kiosk Chrona         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le backend tourne
Write-Host "[1/3] Vérification du backend..." -ForegroundColor Yellow
$backendRunning = podman ps --filter "name=backend" --format "{{.Names}}"
if (-not $backendRunning) {
    Write-Host "  ⚠ Backend non démarré. Lancement..." -ForegroundColor Yellow
    podman compose up -d backend db
    Start-Sleep -Seconds 5
}
Write-Host "  ✓ Backend actif" -ForegroundColor Green

# Vérifier la clé API du kiosk
Write-Host "`n[2/3] Vérification de la configuration kiosk..." -ForegroundColor Yellow
$envContent = Get-Content "apps/kiosk/.env" -ErrorAction SilentlyContinue
if ($envContent -notmatch "VITE_KIOSK_API_KEY") {
    Write-Host "  ⚠ Clé API manquante, génération..." -ForegroundColor Yellow
    $apiKeyOutput = podman exec chrona_core-backend-1 python tools/generate_kiosk_api_key.py 1
    $apiKey = ($apiKeyOutput | Select-String "API KEY:").ToString() -replace ".*API KEY:\s*", ""

    if ($apiKey) {
        "VITE_KIOSK_API_KEY=$apiKey" | Add-Content "apps/kiosk/.env"
        Write-Host "  ✓ Clé API ajoutée" -ForegroundColor Green
    }
}

# Démarrer le kiosk via Podman
Write-Host "`n[3/3] Démarrage du conteneur kiosk..." -ForegroundColor Yellow
podman compose up -d kiosk

Start-Sleep -Seconds 3

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   Kiosk démarré avec succès !         " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Accès kiosk:" -ForegroundColor Yellow
Write-Host "  • URL locale:  http://localhost:5174" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  • Voir les logs:   podman logs -f chrona_core-kiosk-1" -ForegroundColor Cyan
Write-Host "  • Arrêter:         podman compose stop kiosk" -ForegroundColor Cyan
Write-Host "  • Redémarrer:      podman compose restart kiosk" -ForegroundColor Cyan
Write-Host ""
