# EAS Credentials Setup Helper Script (PowerShell)
# This script guides you through setting up Android credentials for EAS builds

Write-Host "🔐 EAS Android Credentials Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Node/npm is available
Write-Host "📋 Step 1: Checking Node.js and npm..." -ForegroundColor Blue
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js/npm not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Check Expo authentication
Write-Host "📋 Step 2: Checking Expo authentication..." -ForegroundColor Blue
try {
    $easWhoami = npx eas@latest whoami 2>$null
    Write-Host "✅ Authenticated as: $easWhoami" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Not authenticated with Expo" -ForegroundColor Yellow
    Write-Host "🔗 Run: npx eas@latest login" -ForegroundColor Cyan
    Write-Host "   Then run this script again" -ForegroundColor Cyan
    exit 0
}
Write-Host ""

# Step 3: Check for existing credentials
Write-Host "📋 Step 3: Checking for existing Android credentials..." -ForegroundColor Blue
try {
    $credOutput = npx eas@latest credentials show --platform android 2>$null
    if ($credOutput) {
        Write-Host "ℹ️  Android credentials already exist" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Current credentials:" -ForegroundColor Yellow
        Write-Host $credOutput
        Write-Host ""
        $response = Read-Host "Do you want to reconfigure? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            npx eas@latest credentials configure --platform android
        }
    }
} catch {
    Write-Host "❌ No Android credentials found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Setting up Android credentials..." -ForegroundColor Cyan
    npx eas@latest credentials configure --platform android
}

Write-Host ""
Write-Host "✅ Android credentials setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Create EXPO_TOKEN at: https://expo.dev/accounts/$easWhoami/settings/access-tokens" -ForegroundColor Cyan
Write-Host "2. Add EXPO_TOKEN to GitHub Secrets (Settings → Secrets and variables → Actions)" -ForegroundColor Cyan
Write-Host "3. Test locally: eas build --platform android --profile preview --local" -ForegroundColor Cyan
Write-Host "4. Commit changes: git add apps/mobile/eas.json && git commit -m 'ci(mobile): configure EAS credentials'" -ForegroundColor Cyan
Write-Host ""
