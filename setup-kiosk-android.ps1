#!/usr/bin/env pwsh
# Chrona - Configuration du Kiosk pour Tablette Android
# Usage: .\setup-kiosk-android.ps1
#
# Ce script configure le kiosk pour fonctionner sur une tablette Android
# en configurant le réseau et en générant les identifiants nécessaires

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Configuration du Kiosk pour Tablette Android              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# ÉTAPE 1: Vérification des prérequis
# ============================================================================
Write-Host "[1/6] Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier Podman
try {
    $podmanVersion = podman --version 2>$null
    Write-Host "  ✓ Podman détecté: $podmanVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Podman n'est pas installé" -ForegroundColor Red
    exit 1
}

# Vérifier que les services tournent
$backendRunning = podman ps --filter "name=backend" --format "{{.Names}}" 2>$null
if (-not $backendRunning) {
    Write-Host "  ✗ Le backend n'est pas démarré. Exécutez d'abord: .\setup-dev.ps1" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Services Chrona actifs" -ForegroundColor Green

# ============================================================================
# ÉTAPE 2: Déterminer l'adresse IP du serveur
# ============================================================================
Write-Host "`n[2/6] Configuration du réseau..." -ForegroundColor Yellow

# Récupérer l'adresse IP de la machine
try {
    # Essayer IPv4 d'abord
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notmatch "^127\." -and $_.InterfaceAlias -notmatch "Docker|vEthernet" } |
        Select-Object -First 1).IPAddress

    if (-not $ipAddress) {
        # Fallback pour localhost
        $ipAddress = "localhost"
    }

    Write-Host "  ✓ Adresse IP détectée: $ipAddress" -ForegroundColor Green
} catch {
    $ipAddress = "localhost"
    Write-Host "  ⚠ Impossible de déterminer l'IP, utilisant: $ipAddress" -ForegroundColor Yellow
}

# ============================================================================
# ÉTAPE 3: Générer/Récupérer la clé API du kiosk
# ============================================================================
Write-Host "`n[3/6] Génération de la clé API du kiosk..." -ForegroundColor Yellow

$kioskEnvPath = "apps/kiosk/.env"

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path $kioskEnvPath)) {
    New-Item -ItemType File -Path $kioskEnvPath -Force | Out-Null
    Write-Host "  ✓ Fichier .env créé" -ForegroundColor Green
}

# Vérifier si la clé API existe déjà
$existingKey = (Get-Content $kioskEnvPath -ErrorAction SilentlyContinue | Select-String "VITE_KIOSK_API_KEY")
if ($existingKey) {
    Write-Host "  ✓ Clé API existante trouvée" -ForegroundColor Green
    $kioskApiKey = ($existingKey -split "=")[1]
} else {
    # Générer une nouvelle clé API
    Write-Host "  Génération nouvelle clé API..." -ForegroundColor Cyan
    try {
        $apiKeyOutput = podman exec chrona_core-backend-1 python tools/generate_kiosk_api_key.py 1 2>&1
        $kioskApiKey = ($apiKeyOutput | Select-String "API KEY:") -replace ".*API KEY:\s*", "" | ForEach-Object { $_.ToString().Trim() }

        if ($kioskApiKey) {
            "VITE_KIOSK_API_KEY=$kioskApiKey" | Add-Content $kioskEnvPath
            Write-Host "  ✓ Clé API générée et sauvegardée" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ Erreur génération clé API: $_" -ForegroundColor Yellow
        $kioskApiKey = "À_GÉNÉRER_MANUELLEMENT"
    }
}

# ============================================================================
# ÉTAPE 4: Configurer les variables d'environnement pour Android
# ============================================================================
Write-Host "`n[4/6] Configuration du fichier .env pour Android..." -ForegroundColor Yellow

# URL du backend accessible depuis Android
$backendUrl = "http://$ipAddress`:8000"

# Vérifier/ajouter VITE_API_URL
if ((Get-Content $kioskEnvPath -ErrorAction SilentlyContinue) -notmatch "VITE_API_URL") {
    "VITE_API_URL=$backendUrl" | Add-Content $kioskEnvPath
    Write-Host "  ✓ VITE_API_URL définie: $backendUrl" -ForegroundColor Green
} else {
    Write-Host "  ✓ VITE_API_URL déjà configurée" -ForegroundColor Green
}

# Ajouter VITE_KIOSK_MODE pour mode kiosk
if ((Get-Content $kioskEnvPath -ErrorAction SilentlyContinue) -notmatch "VITE_KIOSK_MODE") {
    "VITE_KIOSK_MODE=true" | Add-Content $kioskEnvPath
    Write-Host "  ✓ Mode kiosk activé" -ForegroundColor Green
}

# ============================================================================
# ÉTAPE 5: Configuration du pare-feu Windows (si nécessaire)
# ============================================================================
Write-Host "`n[5/6] Configuration du pare-feu (optionnel)..." -ForegroundColor Yellow

# Vérifier si une règle existe déjà
$firewallRule = Get-NetFirewallRule -DisplayName "Chrona Backend API" -ErrorAction SilentlyContinue
if (-not $firewallRule) {
    Write-Host "  Note: Pour permettre à votre tablette Android d'accéder au backend," -ForegroundColor Cyan
    Write-Host "        vous devrez peut-être configurer le pare-feu Windows." -ForegroundColor Cyan
    Write-Host "        Exécutez cette commande en tant qu'administrateur:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "        netsh advfirewall firewall add rule name=""Chrona Backend API"" dir=in action=allow protocol=TCP localport=8000" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "  ✓ Règle pare-feu pour Chrona existante" -ForegroundColor Green
}

# ============================================================================
# ÉTAPE 6: Afficher les instructions pour Android
# ============================================================================
Write-Host "`n[6/6] Génération des instructions d'accès..." -ForegroundColor Yellow

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✅ CONFIGURATION KIOSK ANDROID COMPLÈTÉE              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📱 ACCÈS DEPUIS VOTRE TABLETTE ANDROID:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   URL du Kiosk:" -ForegroundColor Yellow
Write-Host "   ► http://$ipAddress`:5174" -ForegroundColor White
Write-Host ""
Write-Host "   API Backend:" -ForegroundColor Yellow
Write-Host "   ► http://$ipAddress`:8000" -ForegroundColor White
Write-Host ""

Write-Host "📋 INSTRUCTIONS D'ACCÈS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Sur votre tablette Android:" -ForegroundColor Yellow
Write-Host "      • Ouvrir un navigateur (Chrome, Firefox, etc.)" -ForegroundColor White
Write-Host "      • Accéder à: http://$ipAddress`:5174" -ForegroundColor White
Write-Host ""
Write-Host "   2. Configuration de la connexion:" -ForegroundColor Yellow
Write-Host "      • Assurez-vous que la tablette est sur le même réseau WiFi que le PC" -ForegroundColor White
Write-Host "      • Vérifiez que le pare-feu Windows autorise les connexions" -ForegroundColor White
Write-Host "      • Si la connexion échoue, consultez les logs:" -ForegroundColor White
Write-Host "        docker compose logs kiosk" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔑 IDENTIFIANTS KIOSK:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Clé API:" -ForegroundColor Yellow
Write-Host "   ► $kioskApiKey" -ForegroundColor White
Write-Host ""

Write-Host "🎯 CONFIGURATION SYSTÈME:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Fichier config: $kioskEnvPath" -ForegroundColor Yellow
Write-Host "   Variables:" -ForegroundColor White
Write-Host "   • VITE_API_URL=http://$ipAddress`:8000" -ForegroundColor Cyan
Write-Host "   • VITE_KIOSK_MODE=true" -ForegroundColor Cyan
Write-Host "   • VITE_KIOSK_API_KEY=$kioskApiKey" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚡ COMMANDES UTILES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   • Redémarrer le kiosk:" -ForegroundColor Yellow
Write-Host "     docker compose restart kiosk" -ForegroundColor Cyan
Write-Host ""
Write-Host "   • Voir les logs:" -ForegroundColor Yellow
Write-Host "     docker compose logs -f kiosk" -ForegroundColor Cyan
Write-Host ""
Write-Host "   • Tester la connexion depuis Android:" -ForegroundColor Yellow
Write-Host "     Sur Android, ouvrir: http://$ipAddress`:8000/health" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  REMARQUES IMPORTANTES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. Réseau: La tablette Android doit être sur le même réseau WiFi" -ForegroundColor White
Write-Host "   2. Firewall: Autorisez les ports 5174 et 8000 si demandé par Windows" -ForegroundColor White
Write-Host "   3. Adresse IP: Si $ipAddress ne fonctionne pas, essayez l'IP locale de votre PC" -ForegroundColor White
Write-Host "   4. Certificats: En développement, ignorez les avertissements HTTPS si présents" -ForegroundColor White
Write-Host ""

Write-Host "✅ Prêt à utiliser le kiosk sur tablette Android!" -ForegroundColor Green
Write-Host ""
