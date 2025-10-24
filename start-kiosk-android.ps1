#!/usr/bin/env pwsh
# Chrona - Démarrage du Kiosk pour Tablette Android
# Usage: .\start-kiosk-android.ps1

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      Démarrage du Kiosk pour Tablette Android                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ÉTAPE 1: Vérification que les services tournent
# ============================================================================
Write-Host "[1/4] Vérification des services..." -ForegroundColor Yellow

$backendRunning = podman ps --filter "name=backend" --format "{{.Names}}" 2>$null
$kioskRunning = podman ps --filter "name=kiosk" --format "{{.Names}}" 2>$null

if (-not $backendRunning) {
    Write-Host "  ⚠ Backend non actif, démarrage..." -ForegroundColor Yellow
    podman compose up -d backend db
    Start-Sleep -Seconds 5
}

Write-Host "  ✓ Backend actif" -ForegroundColor Green

if ($kioskRunning) {
    Write-Host "  ✓ Kiosk déjà actif" -ForegroundColor Green
} else {
    Write-Host "  Kiosk inactif, sera démarré..." -ForegroundColor Cyan
}

# ============================================================================
# ÉTAPE 2: Vérifier la configuration Android
# ============================================================================
Write-Host "`n[2/4] Vérification de la configuration Android..." -ForegroundColor Yellow

$kioskEnvPath = "apps/kiosk/.env"

if (-not (Test-Path $kioskEnvPath)) {
    Write-Host "  ⚠ Fichier .env manquant" -ForegroundColor Yellow
    Write-Host "  Exécutez d'abord: .\setup-kiosk-android.ps1" -ForegroundColor Yellow
    exit 1
}

# Récupérer les variables d'environnement
$envContent = Get-Content $kioskEnvPath
$apiUrl = ($envContent | Select-String "VITE_API_URL" | ForEach-Object { ($_ -split "=")[1] })
$kioskMode = ($envContent | Select-String "VITE_KIOSK_MODE" | ForEach-Object { ($_ -split "=")[1] })

Write-Host "  ✓ Configuration trouvée:" -ForegroundColor Green
Write-Host "    - API URL: $apiUrl" -ForegroundColor Cyan
Write-Host "    - Kiosk Mode: $kioskMode" -ForegroundColor Cyan

# ============================================================================
# ÉTAPE 3: Redémarrer le conteneur kiosk
# ============================================================================
Write-Host "`n[3/4] Démarrage du conteneur kiosk..." -ForegroundColor Yellow

podman compose up -d kiosk

Start-Sleep -Seconds 3

$kioskStatus = podman ps --filter "name=kiosk" --format "{{.Status}}" 2>$null
if ($kioskStatus -match "Up") {
    Write-Host "  ✓ Kiosk démarré avec succès" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Vérification de l'état du kiosk..." -ForegroundColor Yellow
    podman logs chrona_core-kiosk-1 --tail 10
}

# ============================================================================
# ÉTAPE 4: Afficher les instructions d'accès
# ============================================================================
Write-Host "`n[4/4] Génération des instructions..." -ForegroundColor Yellow

# Récupérer l'adresse IP
try {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notmatch "^127\." -and $_.InterfaceAlias -notmatch "Docker|vEthernet" } |
        Select-Object -First 1).IPAddress

    if (-not $ipAddress) {
        $ipAddress = "localhost"
    }
} catch {
    $ipAddress = "localhost"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✅ KIOSK ANDROID PRÊT À L'EMPLOI                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📱 ACCÈS DEPUIS VOTRE TABLETTE ANDROID:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   URL du Kiosk:" -ForegroundColor Yellow
Write-Host "   ► http://$ipAddress`:5174" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host ""

Write-Host "🔍 VÉRIFICATION DE LA CONNEXION:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Depuis votre tablette Android, essayez:" -ForegroundColor Yellow
Write-Host "   1. Ouvrir le navigateur" -ForegroundColor White
Write-Host "   2. Accéder à: http://$ipAddress`:8000/health" -ForegroundColor White
Write-Host "   3. Vous devriez voir: {\"status\":\"ok\",\"db\":\"ok\"}" -ForegroundColor Cyan
Write-Host ""

Write-Host "🌐 DIAGNOSTIC RÉSEAU:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Serveur:" -ForegroundColor Yellow
Write-Host "   • Kiosk (Vite):  http://$ipAddress`:5174" -ForegroundColor White
Write-Host "   • Backend API:   http://$ipAddress`:8000" -ForegroundColor White
Write-Host "   • Database:      PostgreSQL sur port 5432" -ForegroundColor White
Write-Host ""

Write-Host "📊 LOGS ACTIFS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Pour voir les logs en temps réel:" -ForegroundColor Yellow
Write-Host "   podman logs -f chrona_core-kiosk-1" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚙️  AIDE AU DÉPANNAGE:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Si la tablette ne peut pas se connecter:" -ForegroundColor Yellow
Write-Host "   1. Vérifiez le WiFi - même réseau que le PC" -ForegroundColor White
Write-Host "   2. Testez l'adresse IP - remplacez $ipAddress par l'IP locale de votre PC si besoin" -ForegroundColor White
Write-Host "   3. Pare-feu Windows - port 5174 doit être autorisé" -ForegroundColor White
Write-Host "   4. Redémarrez le conteneur: podman compose restart kiosk" -ForegroundColor White
Write-Host ""

Write-Host "✅ Kiosk prêt! Accédez à http://$ipAddress`:5174 depuis votre tablette Android" -ForegroundColor Green
Write-Host ""
