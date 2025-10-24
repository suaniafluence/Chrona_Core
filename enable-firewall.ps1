#!/usr/bin/env pwsh
# Script pour autoriser le kiosk Android dans le pare-feu Windows
# DOIT ÊTRE EXÉCUTÉ EN TANT QU'ADMINISTRATEUR

# Vérifier si l'administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERREUR: Ce script doit être exécuté en tant qu'administrateur" -ForegroundColor Red
    Write-Host ""
    Write-Host "Comment faire:" -ForegroundColor Yellow
    Write-Host "1. Clic-droit sur PowerShell" -ForegroundColor White
    Write-Host "2. Sélectionnez 'Exécuter en tant qu'administrateur'" -ForegroundColor White
    Write-Host "3. Puis exécutez à nouveau ce script" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "     Configuration du Pare-feu Windows pour Kiosk Android       " -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Exécuté en tant qu'administrateur" -ForegroundColor Green
Write-Host ""

# Ajouter règle pour le kiosk (port 5174)
Write-Host "[1/3] Ajout règle pare-feu pour Kiosk (port 5174)..." -ForegroundColor Yellow
try {
    netsh advfirewall firewall add rule name="Chrona Kiosk" dir=in action=allow protocol=TCP localport=5174 2>$null
    Write-Host "  [OK] Règle Kiosk ajoutée" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Règle peut déjà exister" -ForegroundColor Yellow
}

# Ajouter règle pour le backend API (port 8000)
Write-Host "[2/3] Ajout règle pare-feu pour Backend API (port 8000)..." -ForegroundColor Yellow
try {
    netsh advfirewall firewall add rule name="Chrona Backend API" dir=in action=allow protocol=TCP localport=8000 2>$null
    Write-Host "  [OK] Règle Backend API ajoutée" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Règle peut déjà exister" -ForegroundColor Yellow
}

# Ajouter règle pour Docker (port 5173 - backoffice)
Write-Host "[3/3] Ajout règle pare-feu pour Backoffice (port 5173)..." -ForegroundColor Yellow
try {
    netsh advfirewall firewall add rule name="Chrona Backoffice" dir=in action=allow protocol=TCP localport=5173 2>$null
    Write-Host "  [OK] Règle Backoffice ajoutée" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Règle peut déjà exister" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "         PARE-FEU CONFIGURÉ AVEC SUCCÈS                        " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Les règles suivantes ont été ajoutées:" -ForegroundColor Cyan
Write-Host "  * Chrona Kiosk (port 5174)" -ForegroundColor White
Write-Host "  * Chrona Backend API (port 8000)" -ForegroundColor White
Write-Host "  * Chrona Backoffice (port 5173)" -ForegroundColor White
Write-Host ""

Write-Host "Vous pouvez maintenant utiliser:" -ForegroundColor Yellow
Write-Host "  - Kiosk Android: http://10.115.127.67:5174" -ForegroundColor Cyan
Write-Host "  - Backend API: http://10.115.127.67:8000" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testez la connexion depuis votre tablette Android:" -ForegroundColor Yellow
Write-Host "  1. Ouvrez le navigateur" -ForegroundColor White
Write-Host "  2. Accédez à: http://10.115.127.67:5174" -ForegroundColor White
Write-Host "  3. Le kiosk doit s'afficher" -ForegroundColor White
Write-Host ""

Write-Host "Configuration complète!" -ForegroundColor Green
Write-Host ""
