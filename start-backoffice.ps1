#!/usr/bin/env pwsh
# Chrona - Démarrage rapide du Back-office
# Usage: .\start-backoffice.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Démarrage du Back-office Chrona     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que le backend tourne
Write-Host "[1/2] Vérification du backend..." -ForegroundColor Yellow
$backendRunning = podman ps --filter "name=backend" --format "{{.Names}}"
if (-not $backendRunning) {
    Write-Host "  ⚠ Backend non démarré. Lancement..." -ForegroundColor Yellow
    podman compose up -d backend db
    Start-Sleep -Seconds 5
}
Write-Host "  ✓ Backend actif" -ForegroundColor Green

# Démarrer le back-office via Podman
Write-Host "`n[2/2] Démarrage du conteneur back-office..." -ForegroundColor Yellow
podman compose up -d backoffice

Start-Sleep -Seconds 3

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Back-office démarré avec succès !    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Accès back-office:" -ForegroundColor Yellow
Write-Host "  • URL:      http://localhost:5173" -ForegroundColor White
Write-Host "  • Email:    admin@example.com" -ForegroundColor White
Write-Host "  • Password: Passw0rd!" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  • Voir les logs:   podman logs -f chrona_core-backoffice-1" -ForegroundColor Cyan
Write-Host "  • Arrêter:         podman compose stop backoffice" -ForegroundColor Cyan
Write-Host "  • Redémarrer:      podman compose restart backoffice" -ForegroundColor Cyan
Write-Host ""
