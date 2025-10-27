# Setup EAS Credentials for Android Build
# This script configures Android keystore credentials for Expo EAS Build
# The credentials are stored on Expo servers and used for signing APKs

param(
    [Parameter(Mandatory=$false)]
    [switch]$Interactive,

    [Parameter(Mandatory=$false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   EAS Credentials Setup for Android Build     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
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

# Check authentication status
Write-Host ""
Write-Host "🔑 Vérification de l'authentification Expo..." -ForegroundColor Yellow
$whoami = eas whoami 2>&1

if ($whoami -match "Not logged in") {
    Write-Host "❌ Non connecté à Expo" -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 Connexion à Expo avec EXPO_TOKEN..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Vous avez 2 options:" -ForegroundColor Cyan
    Write-Host "  1. Si vous avez EXPO_TOKEN en variable d'env:" -ForegroundColor White
    Write-Host "     \$env:EXPO_TOKEN = 'votre-token'" -ForegroundColor Gray
    Write-Host "     puis relancez ce script" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Ou utilisez la connexion interactive:" -ForegroundColor White
    Write-Host "     eas login" -ForegroundColor Gray
    Write-Host ""
    Write-Host "ℹ️  Le token est disponible sur: https://expo.dev/settings/tokens" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "✅ Authentifié sur Expo: $whoami" -ForegroundColor Green
}

# Check if credentials already exist
Write-Host ""
Write-Host "🔐 Vérification des credentials Android existants..." -ForegroundColor Yellow

$credentialsOutput = eas credentials show --platform android 2>&1

if ($credentialsOutput -match "Keystore" -and -not $Force) {
    Write-Host "✅ Credentials Android déjà configurés" -ForegroundColor Green
    Write-Host ""
    $credentialsOutput | Write-Host
    Write-Host ""
    Write-Host "Pour reconfigurer les credentials, utilisez: -Force" -ForegroundColor Cyan
    exit 0
}

# Configure credentials
Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   Configuration des Credentials Android      ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Host "⚠️  Important:" -ForegroundColor Yellow
Write-Host "   • Un nouveau keystore va être généré" -ForegroundColor White
Write-Host "   • Il sera sauvegardé sur les serveurs Expo" -ForegroundColor White
Write-Host "   • Utilisable pour tous les futurs builds" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Lancement de la configuration interactive..." -ForegroundColor Cyan
Write-Host "   (Suivez les instructions à l'écran)" -ForegroundColor Gray
Write-Host ""

eas credentials configure --platform android

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Échec de la configuration des credentials" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ Credentials Configurés avec Succès !     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Vérification des credentials:" -ForegroundColor Cyan
eas credentials show --platform android

Write-Host ""
Write-Host "🎯 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Lancer le build avec: eas build --platform android --profile preview" -ForegroundColor White
Write-Host "   2. Ou utiliser le script: .\build-apk.ps1 -AutoDetectIP" -ForegroundColor White
Write-Host ""

Write-Host "💡 Conseil:" -ForegroundColor Cyan
Write-Host "   Le EXPO_TOKEN dans GitHub Secrets suffira pour les futurs builds CI/CD" -ForegroundColor Gray
Write-Host ""
