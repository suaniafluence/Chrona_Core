# Build APK Script for Chrona Mobile
# This script automates the build process for the employee mobile app

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("preview", "production")]
    [string]$Profile = "preview",

    [Parameter(Mandatory=$false)]
    [switch]$AutoDetectIP
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Chrona Mobile - APK Build Script           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to detect WiFi IP
function Get-WiFiIP {
    Write-Host "🔍 Détection de l'adresse IP WiFi..." -ForegroundColor Yellow

    $adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.InterfaceAlias -like "*Wi-Fi*" -or
        $_.InterfaceAlias -like "*Wireless*" -and
        $_.IPAddress -notlike "169.254.*"
    }

    if ($adapters) {
        $ip = $adapters[0].IPAddress
        Write-Host "✅ IP WiFi détectée: $ip" -ForegroundColor Green
        return $ip
    }

    Write-Host "❌ Impossible de détecter l'IP WiFi automatiquement" -ForegroundColor Red
    return $null
}

# Detect or validate API URL
if ($AutoDetectIP -or [string]::IsNullOrEmpty($ApiUrl)) {
    $detectedIP = Get-WiFiIP
    if ($detectedIP) {
        $ApiUrl = "http://${detectedIP}:8000"
        Write-Host "📡 URL de l'API configurée: $ApiUrl" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Veuillez spécifier l'URL de l'API avec -ApiUrl" -ForegroundColor Yellow
        Write-Host "Exemple: .\build-apk.ps1 -ApiUrl http://192.168.1.100:8000" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host "📋 Configuration du Build:" -ForegroundColor Magenta
Write-Host "   • Profil: $Profile" -ForegroundColor White
Write-Host "   • URL API: $ApiUrl" -ForegroundColor White
Write-Host ""

# Check if EAS CLI is installed
Write-Host "🔧 Vérification de EAS CLI..." -ForegroundColor Yellow
$easInstalled = Get-Command eas -ErrorAction SilentlyContinue

if (-not $easInstalled) {
    Write-Host "❌ EAS CLI n'est pas installé" -ForegroundColor Red
    Write-Host "📦 Installation de EAS CLI..." -ForegroundColor Yellow
    npm install -g eas-cli

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Échec de l'installation de EAS CLI" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ EAS CLI installé" -ForegroundColor Green
} else {
    Write-Host "✅ EAS CLI est installé" -ForegroundColor Green
}

# Check if logged in to Expo
Write-Host ""
Write-Host "🔑 Vérification de l'authentification Expo..." -ForegroundColor Yellow
$whoami = eas whoami 2>&1

if ($whoami -match "Not logged in") {
    Write-Host "❌ Non connecté à Expo" -ForegroundColor Red
    Write-Host "📝 Connexion à Expo..." -ForegroundColor Yellow
    eas login

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Échec de la connexion à Expo" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Authentifié sur Expo: $whoami" -ForegroundColor Green
}

# Update eas.json with API URL
Write-Host ""
Write-Host "📝 Mise à jour de eas.json..." -ForegroundColor Yellow

$easJsonPath = "eas.json"
$easJson = Get-Content $easJsonPath -Raw | ConvertFrom-Json

# Update the API URL for the selected profile
$easJson.build.$Profile.env.EXPO_PUBLIC_API_URL = $ApiUrl

$easJson | ConvertTo-Json -Depth 10 | Set-Content $easJsonPath

Write-Host "✅ eas.json mis à jour avec URL: $ApiUrl" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Échec de l'installation des dépendances" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dépendances installées" -ForegroundColor Green

# Start the build
Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   🚀 Démarrage du Build APK                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Le build va prendre environ 15-20 minutes..." -ForegroundColor Yellow
Write-Host "☁️  Le build s'exécute sur les serveurs Expo" -ForegroundColor Cyan
Write-Host ""

eas build --platform android --profile $Profile

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Échec du build" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Build Terminé avec Succès !             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📲 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Télécharger l'APK depuis le lien fourni" -ForegroundColor White
Write-Host "   2. Distribuer l'APK aux employés" -ForegroundColor White
Write-Host "   3. Installer sur les téléphones Android" -ForegroundColor White
Write-Host ""
Write-Host "📚 Guide d'installation: apps/mobile/APK_BUILD.md" -ForegroundColor Gray
Write-Host ""
