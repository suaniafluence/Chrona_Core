#!/usr/bin/env pwsh
# Configuration VPN Optionnelle pour Chrona
# Usage: .\setup-vpn-optional.ps1
#
# Ce script:
# 1. Teste l'accès direct à Chrona (port 5174/8000)
# 2. Si accès direct OK → VPN non nécessaire
# 3. Si accès bloqué → Propose d'activer VPN Wireguard
# 4. Génère clés VPN et QR codes pour Android

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Configuration VPN Optionnelle pour Chrona                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ÉTAPE 1: Détecter l'adresse IP locale
# ============================================================================
Write-Host "[1/4] Détection de l'adresse IP locale..." -ForegroundColor Yellow

try {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notmatch "^127\." -and $_.InterfaceAlias -notmatch "Docker|vEthernet" } |
        Select-Object -First 1).IPAddress

    if (-not $ipAddress) {
        $ipAddress = "localhost"
    }
    Write-Host "  ✓ IP détectée: $ipAddress" -ForegroundColor Green
} catch {
    $ipAddress = "localhost"
    Write-Host "  ⚠ Impossible de déterminer l'IP, utilisant: $ipAddress" -ForegroundColor Yellow
}

# ============================================================================
# ÉTAPE 2: Tester l'accès direct à Chrona
# ============================================================================
Write-Host ""
Write-Host "[2/4] Test d'accès direct à Chrona..." -ForegroundColor Yellow

$directAccessWorks = $false

# Test API Backend
try {
    $healthCheck = curl.exe -s -m 5 "http://localhost:8000/health" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Accès Backend API (localhost:8000) : OK" -ForegroundColor Green
        $directAccessWorks = $true
    }
} catch {
    Write-Host "  ✗ Accès Backend API (localhost:8000) : ÉCHOUÉ" -ForegroundColor Red
}

# Test Kiosk (localhost)
try {
    $kioskCheck = curl.exe -s -m 5 "http://localhost:5174" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Accès Kiosk (localhost:5174) : OK" -ForegroundColor Green
        $directAccessWorks = $true
    }
} catch {
    Write-Host "  ✗ Accès Kiosk (localhost:5174) : ÉCHOUÉ" -ForegroundColor Red
}

# ============================================================================
# ÉTAPE 3: Décision VPN
# ============================================================================
Write-Host ""
Write-Host "[3/4] Analyse d'accès réseau..." -ForegroundColor Yellow
Write-Host ""

if ($directAccessWorks) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ ACCÈS DIRECT FONCTIONNEL                                  ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez accéder à Chrona directement:" -ForegroundColor Green
    Write-Host "  • Kiosk:   http://$ipAddress`:5174" -ForegroundColor Cyan
    Write-Host "  • Backend: http://$ipAddress`:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "VPN n'est pas nécessaire pour le moment." -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  ⚠ ACCÈS DIRECT IMPOSSIBLE                                    ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possibilités:" -ForegroundColor Yellow
    Write-Host "  1. Le réseau bloque les ports 5174/8000" -ForegroundColor White
    Write-Host "  2. Docker n'est pas en cours d'exécution" -ForegroundColor White
    Write-Host "  3. Besoin d'accès VPN pour contourner les restrictions" -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# ÉTAPE 4: Proposer VPN
# ============================================================================
Write-Host "[4/4] Configuration VPN (Optionnel)..." -ForegroundColor Yellow
Write-Host ""

$vpnChoice = Read-Host "Voulez-vous configurer un VPN Wireguard? (oui/non)"

if ($vpnChoice -ne "oui") {
    Write-Host ""
    Write-Host "Configuration VPN annulée." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Si vous avez besoin du VPN plus tard, exécutez:" -ForegroundColor Cyan
    Write-Host "  docker compose -f docker-compose.yml -f docker-compose.vpn.yml up -d" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# ============================================================================
# LANCER VPN WIREGUARD
# ============================================================================
Write-Host ""
Write-Host "Démarrage du VPN Wireguard..." -ForegroundColor Yellow
Write-Host ""

# Créer répertoire config si nécessaire
if (-not (Test-Path "wireguard")) {
    New-Item -ItemType Directory -Path "wireguard" | Out-Null
    Write-Host "  ✓ Répertoire wireguard/ créé" -ForegroundColor Green
}

# Vérifier que docker-compose.vpn.yml existe
if (-not (Test-Path "docker-compose.vpn.yml")) {
    Write-Host "  ✗ Fichier docker-compose.vpn.yml manquant!" -ForegroundColor Red
    exit 1
}

# Lancer Docker Compose avec VPN
try {
    Write-Host "  Lancement de Wireguard..." -ForegroundColor Cyan
    docker compose -f docker-compose.yml -f docker-compose.vpn.yml up -d wireguard

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Wireguard démarré avec succès" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Erreur lors du lancement de Wireguard" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Erreur: $_" -ForegroundColor Red
    exit 1
}

# Attendre que Wireguard soit prêt
Write-Host ""
Write-Host "Attente du démarrage de Wireguard..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# ============================================================================
# RÉCUPÉRER QR CODES WIREGUARD
# ============================================================================
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ WIREGUARD CONFIGURÉ AVEC SUCCÈS                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📱 Configuration VPN pour Android:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Port VPN: 51820 (UDP)" -ForegroundColor White
Write-Host "  Serveur: $ipAddress" -ForegroundColor White
Write-Host ""

Write-Host "🔑 Clés générées pour:" -ForegroundColor Cyan
Write-Host "  • android-pixel7" -ForegroundColor White
Write-Host "  • android-backup" -ForegroundColor White
Write-Host ""

# Attendre un peu pour que les configs soient générées
Start-Sleep -Seconds 3

# Vérifier si les fichiers sont générés
$peersPath = "wireguard"
if (Test-Path "$peersPath/peer_android-pixel7/wg0.conf") {
    Write-Host "✓ Configuration Android Pixel7 générée" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Contenu du fichier (wg0.conf):" -ForegroundColor Yellow
    Get-Content "$peersPath/peer_android-pixel7/wg0.conf" | ForEach-Object {
        Write-Host "  $_"
    }
} else {
    Write-Host "⚠ Les configs VPN ne sont pas encore générées." -ForegroundColor Yellow
    Write-Host "  Attendez quelques secondes et vérifiez le dossier wireguard/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📱 Instructions pour Android:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Installer l'app Wireguard depuis Play Store" -ForegroundColor White
Write-Host "  2. Copier le fichier wireguard/peer_android-pixel7/wg0.conf" -ForegroundColor White
Write-Host "  3. Ou scanner le QR code dans wireguard/peer_android-pixel7/" -ForegroundColor White
Write-Host "  4. Importer dans l'app Wireguard" -ForegroundColor White
Write-Host "  5. Activer la connexion VPN" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Tester la connexion:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Une fois VPN connecté sur Android:" -ForegroundColor White
Write-Host "  1. Ouvrir: http://$ipAddress`:5174 (Kiosk)" -ForegroundColor White
Write-Host "  2. Ou:     http://$ipAddress`:8000/health (Backend)" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  Important:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  • Adapté SERVERURL dans docker-compose.vpn.yml:" -ForegroundColor White
Write-Host "    Remplacer '192.168.211.14' par votre IP réelle" -ForegroundColor Cyan
Write-Host ""
Write-Host "  • Firewall Windows: Autoriser port 51820/UDP" -ForegroundColor White
Write-Host "    netsh advfirewall firewall add rule name=\"Wireguard VPN\" `" -ForegroundColor Cyan
Write-Host "      dir=in action=allow protocol=udp localport=51820" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Configuration VPN complétée!" -ForegroundColor Green
Write-Host ""
