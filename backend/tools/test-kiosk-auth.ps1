#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test script for kiosk authentication feature
.DESCRIPTION
    This script demonstrates the kiosk authentication workflow:
    1. Create admin user
    2. Create kiosk
    3. Generate API key for kiosk
    4. Test authenticated requests
.PARAMETER Api
    Backend API URL (default: http://localhost:8000)
.EXAMPLE
    pwsh ./backend/tools/test-kiosk-auth.ps1 -Api http://localhost:8000
#>

param(
    [string]$Api = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Chrona Kiosk Authentication Test ===" -ForegroundColor Cyan
Write-Host "API: $Api" -ForegroundColor Gray
Write-Host ""

# Step 1: Create admin user
Write-Host "[1/5] Creating admin user..." -ForegroundColor Yellow
$adminEmail = "admin-$(Get-Random)@test.com"
$adminPassword = "Admin123!"

try {
    $registerResponse = Invoke-RestMethod -Uri "$Api/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body (@{
            email = $adminEmail
            password = $adminPassword
        } | ConvertTo-Json)

    Write-Host "  Admin user created: $adminEmail" -ForegroundColor Green
} catch {
    Write-Host "  Failed to create admin: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Login as admin
Write-Host "[2/5] Logging in as admin..." -ForegroundColor Yellow
try {
    $tokenResponse = Invoke-RestMethod -Uri "$Api/auth/token" `
        -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body "username=$adminEmail&password=$adminPassword"

    $adminToken = $tokenResponse.access_token
    Write-Host "  Admin token obtained" -ForegroundColor Green
} catch {
    Write-Host "  Failed to login: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Promote user to admin role
Write-Host "[3/5] Promoting user to admin..." -ForegroundColor Yellow
try {
    $userId = $registerResponse.id
    $roleResponse = Invoke-RestMethod -Uri "$Api/admin/users/$userId/role" `
        -Method Patch `
        -Headers @{Authorization = "Bearer $adminToken"} `
        -ContentType "application/json" `
        -Body (@{role = "admin"} | ConvertTo-Json)

    Write-Host "  User promoted to admin" -ForegroundColor Green
} catch {
    Write-Host "  Failed to promote user: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Create kiosk
Write-Host "[4/5] Creating kiosk..." -ForegroundColor Yellow
try {
    $kioskResponse = Invoke-RestMethod -Uri "$Api/admin/kiosks" `
        -Method Post `
        -Headers @{Authorization = "Bearer $adminToken"} `
        -ContentType "application/json" `
        -Body (@{
            kiosk_name = "Test-Kiosk-$(Get-Random)"
            location = "Test Location - Entrance"
            device_fingerprint = "test-fp-$(Get-Random)"
        } | ConvertTo-Json)

    $kioskId = $kioskResponse.id
    Write-Host "  Kiosk created with ID: $kioskId" -ForegroundColor Green
} catch {
    Write-Host "  Failed to create kiosk: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Generate API key for kiosk
Write-Host "[5/5] Generating API key for kiosk..." -ForegroundColor Yellow
try {
    $apiKeyResponse = Invoke-RestMethod -Uri "$Api/admin/kiosks/$kioskId/generate-api-key" `
        -Method Post `
        -Headers @{Authorization = "Bearer $adminToken"} `
        -ContentType "application/json"

    $apiKey = $apiKeyResponse.api_key
    Write-Host "  API key generated: $apiKey" -ForegroundColor Green
    Write-Host "  Message: $($apiKeyResponse.message)" -ForegroundColor Gray
} catch {
    Write-Host "  Failed to generate API key: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "  Kiosk ID: $kioskId" -ForegroundColor White
Write-Host "  API Key: $apiKey" -ForegroundColor White
Write-Host ""
Write-Host "Add these to your kiosk .env file:" -ForegroundColor Yellow
Write-Host "  VITE_KIOSK_ID=$kioskId" -ForegroundColor Gray
Write-Host "  VITE_KIOSK_API_KEY=$apiKey" -ForegroundColor Gray
Write-Host ""

# Test authentication with valid API key
Write-Host "Testing API key authentication..." -ForegroundColor Yellow
try {
    # This should fail because we don't have a valid QR token, but it should fail
    # AFTER authentication (400 Bad Request instead of 401 Unauthorized)
    $testResponse = Invoke-RestMethod -Uri "$Api/punch/validate" `
        -Method Post `
        -Headers @{"X-Kiosk-API-Key" = $apiKey} `
        -ContentType "application/json" `
        -Body (@{
            qr_token = "fake-token"
            kiosk_id = $kioskId
            punch_type = "clock_in"
        } | ConvertTo-Json)
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "  Authentication successful (400 Bad Request = authenticated but invalid token)" -ForegroundColor Green
    } elseif ($statusCode -eq 401) {
        Write-Host "  Authentication failed (401 Unauthorized)" -ForegroundColor Red
    } else {
        Write-Host "  Unexpected status code: $statusCode" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Green
