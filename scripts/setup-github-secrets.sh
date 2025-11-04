#!/bin/bash

# Setup GitHub Secrets for EC2 Deployment
# Usage: ./setup-github-secrets.sh --pem-file /path/to/key.pem --ec2-host 54.123.456.789 --ec2-user ubuntu --owner your-org --repo Chrona_Core --db-url "postgresql://..." --allowed-origins "http://..."

set -euo pipefail

# Default values
EC2_USER="ubuntu"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --pem-file)
            PEM_FILE="$2"
            shift 2
            ;;
        --ec2-host)
            EC2_HOST="$2"
            shift 2
            ;;
        --ec2-user)
            EC2_USER="$2"
            shift 2
            ;;
        --owner)
            OWNER="$2"
            shift 2
            ;;
        --repo)
            REPO="$2"
            shift 2
            ;;
        --db-url)
            DATABASE_URL="$2"
            shift 2
            ;;
        --secret-key)
            SECRET_KEY="$2"
            shift 2
            ;;
        --allowed-origins)
            ALLOWED_ORIGINS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Verify required arguments
required_args=("PEM_FILE" "EC2_HOST" "OWNER" "REPO" "DATABASE_URL" "ALLOWED_ORIGINS")
for arg in "${required_args[@]}"; do
    if [[ -z "${!arg:-}" ]]; then
        echo "Error: --${arg,,} is required"
        exit 1
    fi
done

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Please install it from https://cli.github.com/"
    exit 1
fi

# Check if PEM file exists
if [[ ! -f "$PEM_FILE" ]]; then
    echo "Error: PEM file not found at: $PEM_FILE"
    exit 1
fi

# Generate SECRET_KEY if not provided
if [[ -z "${SECRET_KEY:-}" ]]; then
    SECRET_KEY=$(openssl rand -hex 32)
fi

# Read the PEM file content
echo "Reading PEM file..."
PEM_CONTENT=$(cat "$PEM_FILE")

# Set GitHub Secrets
echo "Setting GitHub Secrets for $OWNER/$REPO..."

echo "Setting EC2_HOST..."
echo "$EC2_HOST" | gh secret set EC2_HOST --repo "$OWNER/$REPO"

echo "Setting EC2_USER..."
echo "$EC2_USER" | gh secret set EC2_USER --repo "$OWNER/$REPO"

echo "Setting EC2_SSH_KEY..."
echo "$PEM_CONTENT" | gh secret set EC2_SSH_KEY --repo "$OWNER/$REPO"

echo "Setting DATABASE_URL..."
echo "$DATABASE_URL" | gh secret set DATABASE_URL --repo "$OWNER/$REPO"

echo "Setting SECRET_KEY..."
echo "$SECRET_KEY" | gh secret set SECRET_KEY --repo "$OWNER/$REPO"

echo "Setting ALLOWED_ORIGINS..."
echo "$ALLOWED_ORIGINS" | gh secret set ALLOWED_ORIGINS --repo "$OWNER/$REPO"

echo ""
echo -e "\033[32mGitHub Secrets configured successfully!\033[0m"
echo ""
echo "Configuration Summary:"
echo "  EC2_HOST: $EC2_HOST"
echo "  EC2_USER: $EC2_USER"
echo "  DATABASE_URL: $DATABASE_URL"
echo "  ALLOWED_ORIGINS: $ALLOWED_ORIGINS"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/$OWNER/$REPO/actions"
echo "2. Click on 'Deploy' workflow"
echo "3. Click 'Run workflow'"
echo "4. Configure the deployment parameters"
echo "5. Click 'Run workflow'"
