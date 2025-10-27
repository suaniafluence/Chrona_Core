#!/bin/bash
# EAS Credentials Setup Helper Script
# This script guides you through setting up Android credentials for EAS builds

set -e

echo "🔐 EAS Android Credentials Setup"
echo "=================================="
echo ""

# Step 1: Check if EAS CLI is available
echo "📋 Step 1: Checking EAS CLI..."
if ! command -v npx &> /dev/null; then
    echo "❌ npm/npx not found. Please install Node.js 18+"
    exit 1
fi

# Verify EAS version
EAS_VERSION=$(npx eas@latest --version 2>/dev/null || echo "unknown")
echo "✅ EAS CLI version: $EAS_VERSION"
echo ""

# Step 2: Check Expo authentication
echo "📋 Step 2: Checking Expo authentication..."
if npx eas@latest whoami &> /dev/null; then
    EXPO_USER=$(npx eas@latest whoami)
    echo "✅ Authenticated as: $EXPO_USER"
else
    echo "⚠️  Not authenticated with Expo"
    echo "🔗 Run: npx eas@latest login"
    echo "   Then run this script again"
    exit 0
fi
echo ""

# Step 3: Check for existing credentials
echo "📋 Step 3: Checking for existing Android credentials..."
if npx eas@latest credentials show --platform android &> /dev/null; then
    echo "ℹ️  Android credentials already exist"
    echo ""
    echo "Current credentials:"
    npx eas@latest credentials show --platform android
    echo ""
    read -p "Do you want to reconfigure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npx eas@latest credentials configure --platform android
    fi
else
    echo "❌ No Android credentials found"
    echo ""
    echo "📝 Setting up Android credentials..."
    npx eas@latest credentials configure --platform android
fi

echo ""
echo "✅ Android credentials setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create EXPO_TOKEN: https://expo.dev/accounts/$EXPO_USER/settings/access-tokens"
echo "2. Add EXPO_TOKEN to GitHub Secrets"
echo "3. Test locally: eas build --platform android --profile preview --local"
echo "4. Commit changes: git add apps/mobile/eas.json && git commit -m 'ci(mobile): configure EAS credentials'"
echo ""
