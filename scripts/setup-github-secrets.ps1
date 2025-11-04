# Setup GitHub Secrets for EC2 Deployment
# Usage: .\setup-github-secrets.ps1 -PemFilePath "C:\path\to\key.pem" -EC2Host "54.123.456.789" -EC2User "ubuntu" -Owner "your-org" -Repo "Chrona_Core"

param(
    [Parameter(Mandatory=$true)]
    [string]$PemFilePath,

    [Parameter(Mandatory=$true)]
    [string]$EC2Host,

    [Parameter(Mandatory=$true)]
    [string]$EC2User = "ubuntu",

    [Parameter(Mandatory=$true)]
    [string]$Owner,

    [Parameter(Mandatory=$true)]
    [string]$Repo,

    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl,

    [Parameter(Mandatory=$false)]
    [string]$SecretKey = $(openssl rand -hex 32),

    [Parameter(Mandatory=$true)]
    [string]$AllowedOrigins
)

# Check if gh CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
    exit 1
}

# Check if PEM file exists
if (-not (Test-Path $PemFilePath)) {
    Write-Error "PEM file not found at: $PemFilePath"
    exit 1
}

# Read the PEM file content
Write-Host "Reading PEM file..."
$PemContent = Get-Content -Path $PemFilePath -Raw

# Set GitHub Secrets
Write-Host "Setting GitHub Secrets for $Owner/$Repo..."

# EC2_HOST
Write-Host "Setting EC2_HOST..."
$EC2Host | gh secret set EC2_HOST --repo "$Owner/$Repo"

# EC2_USER
Write-Host "Setting EC2_USER..."
$EC2User | gh secret set EC2_USER --repo "$Owner/$Repo"

# EC2_SSH_KEY
Write-Host "Setting EC2_SSH_KEY..."
$PemContent | gh secret set EC2_SSH_KEY --repo "$Owner/$Repo"

# DATABASE_URL
Write-Host "Setting DATABASE_URL..."
$DatabaseUrl | gh secret set DATABASE_URL --repo "$Owner/$Repo"

# SECRET_KEY
Write-Host "Setting SECRET_KEY..."
if (-not $SecretKey) {
    # Generate a random secret key
    $SecretKey = -join ((1..32) | ForEach-Object { [char](Get-Random -InputObject (33..126)) })
}
$SecretKey | gh secret set SECRET_KEY --repo "$Owner/$Repo"
Write-Host "Generated SECRET_KEY: $SecretKey"

# ALLOWED_ORIGINS
Write-Host "Setting ALLOWED_ORIGINS..."
$AllowedOrigins | gh secret set ALLOWED_ORIGINS --repo "$Owner/$Repo"

Write-Host ""
Write-Host "GitHub Secrets configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration Summary:"
Write-Host "  EC2_HOST: $EC2Host"
Write-Host "  EC2_USER: $EC2User"
Write-Host "  DATABASE_URL: $DatabaseUrl"
Write-Host "  ALLOWED_ORIGINS: $AllowedOrigins"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Go to https://github.com/$Owner/$Repo/actions"
Write-Host "2. Click on 'Deploy' workflow"
Write-Host "3. Click 'Run workflow'"
Write-Host "4. Configure the deployment parameters"
Write-Host "5. Click 'Run workflow'"
