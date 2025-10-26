# Create GitHub Release for Mobile APK
# This script creates a git tag and triggers the GitHub Actions workflow

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [Parameter(Mandatory=$false)]
    [string]$Message = "",

    [Parameter(Mandatory=$false)]
    [switch]$Push
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Chrona Mobile - GitHub Release Creator     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Validate version format (semver: X.Y.Z)
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "❌ Version invalide. Format requis: X.Y.Z (ex: 1.0.0)" -ForegroundColor Red
    exit 1
}

$TagName = "mobile-v$Version"

Write-Host "📋 Informations de la Release:" -ForegroundColor Magenta
Write-Host "   • Version: $Version" -ForegroundColor White
Write-Host "   • Tag: $TagName" -ForegroundColor White
Write-Host ""

# Check if tag already exists
$existingTag = git tag -l $TagName

if ($existingTag) {
    Write-Host "❌ Le tag $TagName existe déjà" -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "   1. Supprimer le tag existant:" -ForegroundColor Gray
    Write-Host "      git tag -d $TagName" -ForegroundColor Gray
    Write-Host "      git push origin :refs/tags/$TagName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Utiliser une nouvelle version (incrémenter)" -ForegroundColor Gray
    exit 1
}

# Check if we're in a git repository
$isGitRepo = git rev-parse --is-inside-work-tree 2>$null

if (-not $isGitRepo) {
    Write-Host "❌ Ce n'est pas un dépôt Git" -ForegroundColor Red
    exit 1
}

# Check for uncommitted changes
$status = git status --porcelain

if ($status) {
    Write-Host "⚠️  Changements non commités détectés:" -ForegroundColor Yellow
    Write-Host ""
    git status --short
    Write-Host ""

    $response = Read-Host "Continuer quand même? (o/N)"
    if ($response -ne 'o' -and $response -ne 'O') {
        Write-Host "❌ Annulé par l'utilisateur" -ForegroundColor Red
        exit 1
    }
}

# Update app.json with version
Write-Host "📝 Mise à jour de app.json..." -ForegroundColor Yellow

$appJsonPath = "app.json"
$appJson = Get-Content $appJsonPath -Raw | ConvertFrom-Json

$oldVersion = $appJson.expo.version
$appJson.expo.version = $Version

# Calculate versionCode from semver
$versionParts = $Version.Split('.')
$versionCode = [int]$versionParts[0] * 10000 + [int]$versionParts[1] * 100 + [int]$versionParts[2]
$appJson.expo.android.versionCode = $versionCode

$appJson | ConvertTo-Json -Depth 10 | Set-Content $appJsonPath

Write-Host "✅ Version mise à jour: $oldVersion → $Version" -ForegroundColor Green
Write-Host "✅ versionCode: $versionCode" -ForegroundColor Green

# Commit version change
Write-Host ""
Write-Host "📝 Création du commit de version..." -ForegroundColor Yellow

git add $appJsonPath

$commitMessage = if ($Message) { $Message } else { "chore(mobile): bump version to $Version" }
git commit -m $commitMessage

Write-Host "✅ Commit créé" -ForegroundColor Green

# Create tag
Write-Host ""
Write-Host "🏷️  Création du tag $TagName..." -ForegroundColor Yellow

$tagMessage = @"
Chrona Mobile v$Version

Release automatique de l'application mobile employé.

Téléchargement APK:
https://github.com/$(git config --get remote.origin.url | Select-String -Pattern '([^/:]+/[^/:]+?)(?:\.git)?$' | ForEach-Object { $_.Matches.Groups[1].Value })/releases/download/$TagName/chrona-mobile-v$Version.apk

Installation:
1. Télécharger l'APK
2. Installer sur Android
3. Se connecter avec vos identifiants

Documentation: apps/mobile/INSTALLATION.md
"@

git tag -a $TagName -m $tagMessage

Write-Host "✅ Tag créé: $TagName" -ForegroundColor Green

# Push to remote
if ($Push) {
    Write-Host ""
    Write-Host "📤 Push vers GitHub..." -ForegroundColor Yellow

    git push origin main
    git push origin $TagName

    Write-Host "✅ Push effectué" -ForegroundColor Green

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   🚀 Release Déclenchée !                    ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ Le workflow GitHub Actions va:" -ForegroundColor Cyan
    Write-Host "   1. Builder l'APK avec EAS (15-20 min)" -ForegroundColor White
    Write-Host "   2. Créer une release GitHub" -ForegroundColor White
    Write-Host "   3. Uploader l'APK comme asset" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Suivre le build:" -ForegroundColor Cyan

    $repoUrl = git config --get remote.origin.url
    $repoPath = $repoUrl | Select-String -Pattern '([^/:]+/[^/:]+?)(?:\.git)?$' | ForEach-Object { $_.Matches.Groups[1].Value }
    $actionsUrl = "https://github.com/$repoPath/actions"

    Write-Host "   $actionsUrl" -ForegroundColor Blue
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║   ⚠️  Tag Créé Localement                    ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour déclencher le build GitHub Actions:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   git push origin main" -ForegroundColor White
    Write-Host "   git push origin $TagName" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou relancez avec -Push:" -ForegroundColor Gray
    Write-Host "   .\create-release.ps1 -Version $Version -Push" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📚 Ressources:" -ForegroundColor Magenta
Write-Host "   • Guide: apps/mobile/GITHUB_RELEASES.md" -ForegroundColor Gray
Write-Host "   • Workflow: .github/workflows/build-mobile-apk.yml" -ForegroundColor Gray
Write-Host ""
