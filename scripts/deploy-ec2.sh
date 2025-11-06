#!/bin/bash
# EC2 Deployment Script with Alembic Migrations
# Usage: ./scripts/deploy-ec2.sh [check|migrate|deploy]

set -euo pipefail

DEPLOY_DIR="/opt/chrona"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on EC2 instance
check_environment() {
    if [ ! -d "$DEPLOY_DIR" ]; then
        log_error "Deployment directory $DEPLOY_DIR not found!"
        log_info "This script should be run on the EC2 instance after deployment."
        exit 1
    fi

    cd "$DEPLOY_DIR"

    if [ ! -f ".env" ]; then
        log_error ".env file not found in $DEPLOY_DIR"
        exit 1
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "$COMPOSE_FILE not found in $DEPLOY_DIR"
        exit 1
    fi

    log_info "Environment check passed"
}

# Check database connection
check_database() {
    log_info "Checking database connection..."

    # Source environment variables
    set -a
    source .env
    set +a

    if [ -z "${DATABASE_URL:-}" ]; then
        log_error "DATABASE_URL not set in .env file"
        return 1
    fi

    log_info "DATABASE_URL is configured"

    # Try to connect to database via backend container
    if docker-compose exec -T backend python3 -c "import os; print(os.getenv('DATABASE_URL', 'NOT SET'))" 2>/dev/null; then
        log_info "Backend container can access DATABASE_URL"
        return 0
    else
        log_warn "Could not verify database connection through backend container"
        return 1
    fi
}

# Check Alembic migration status
check_migrations() {
    log_info "Checking Alembic migration status..."

    if docker-compose exec -T backend alembic current 2>/dev/null; then
        log_info "Current migration status retrieved successfully"
        return 0
    else
        log_error "Failed to check migration status. Is the backend running?"
        return 1
    fi
}

# Run Alembic migrations to head
run_migrations() {
    log_info "Running Alembic migrations to head..."

    if docker-compose exec -T backend alembic upgrade head; then
        log_info "✓ Migrations completed successfully!"

        # Show current migration
        echo ""
        log_info "Current migration status:"
        docker-compose exec -T backend alembic current

        return 0
    else
        log_error "✗ Migrations failed!"
        log_info "Check the backend logs: docker-compose logs backend"
        return 1
    fi
}

# Full deployment process
deploy() {
    log_info "Starting deployment process..."

    check_environment

    log_info "Restarting services..."
    docker-compose up -d --build

    log_info "Waiting for services to be healthy..."
    sleep 15

    log_info "Service status:"
    docker-compose ps

    echo ""
    check_database

    echo ""
    run_migrations

    echo ""
    log_info "Creating admin user..."

    # Set default credentials if not provided
    ADMIN_EMAIL_DEFAULT="admin@chrona.local"
    ADMIN_PASSWORD_DEFAULT="ChangeMe123!"

    ADMIN_EMAIL_FINAL="${ADMIN_EMAIL:-$ADMIN_EMAIL_DEFAULT}"
    ADMIN_PASSWORD_FINAL="${ADMIN_PASSWORD:-$ADMIN_PASSWORD_DEFAULT}"

    if docker-compose exec -T backend python tools/create_admin_user.py \
      --email "$ADMIN_EMAIL_FINAL" \
      --password "$ADMIN_PASSWORD_FINAL" \
      --role admin; then
      log_info "✓ Admin user created/updated successfully!"
      if [ -z "$ADMIN_EMAIL" ]; then
        log_warn "Using default admin credentials:"
        echo "  Email: $ADMIN_EMAIL_DEFAULT"
        echo "  Password: $ADMIN_PASSWORD_DEFAULT"
        echo ""
        log_warn "CHANGE THESE CREDENTIALS IMMEDIATELY!"
      fi
    else
      log_error "Failed to create admin user"
      log_info "Create manually: docker-compose exec backend python tools/create_admin_user.py --email admin@example.com --password 'YourPassword' --role admin"
    fi

    echo ""
    log_info "=========================================="
    log_info "Deployment completed!"
    log_info "=========================================="

    # Show service URLs
    set -a
    source .env
    set +a

    echo ""
    echo "Backend API: http://${EC2_HOST:-localhost}:${EC2_PORT:-8000}"
    echo "Swagger UI: http://${EC2_HOST:-localhost}:${EC2_PORT:-8000}/docs"
    echo "Backoffice: http://${EC2_HOST:-localhost}:${BACKOFFICE_PORT:-5173}"
    echo ""
}

# Create admin user
create_admin() {
    log_info "Creating admin user..."

    check_environment

    # Set default credentials if not provided
    ADMIN_EMAIL_DEFAULT="admin@chrona.local"
    ADMIN_PASSWORD_DEFAULT="ChangeMe123!"

    ADMIN_EMAIL_FINAL="${ADMIN_EMAIL:-$ADMIN_EMAIL_DEFAULT}"
    ADMIN_PASSWORD_FINAL="${ADMIN_PASSWORD:-$ADMIN_PASSWORD_DEFAULT}"

    # Allow overriding via command line arguments
    if [ -n "${1:-}" ]; then
        ADMIN_EMAIL_FINAL="$1"
    fi
    if [ -n "${2:-}" ]; then
        ADMIN_PASSWORD_FINAL="$2"
    fi

    log_info "Email: $ADMIN_EMAIL_FINAL"

    if docker-compose exec -T backend python tools/create_admin_user.py \
      --email "$ADMIN_EMAIL_FINAL" \
      --password "$ADMIN_PASSWORD_FINAL" \
      --role admin; then
      log_info "✓ Admin user created/updated successfully!"
    else
      log_error "Failed to create admin user"
      return 1
    fi
}

# Show usage
usage() {
    cat <<EOF
Usage: $0 [command] [options]

Commands:
    check               Check environment and database connection
    migrate             Run Alembic migrations to head
    status              Show current migration status
    create-admin [email] [password]
                        Create or update admin user (uses defaults if not provided)
    deploy              Full deployment (restart services + migrate + create admin)
    help                Show this help message

Examples:
    $0 check            # Verify environment and database
    $0 status           # Show current migration version
    $0 migrate          # Run pending migrations
    $0 create-admin     # Create admin with default credentials
    $0 create-admin admin@company.com SecureP@ss123
                        # Create admin with custom credentials
    $0 deploy           # Full deployment with migrations and admin creation

Environment variables (optional):
    ADMIN_EMAIL         Admin email (default: admin@chrona.local)
    ADMIN_PASSWORD      Admin password (default: ChangeMe123!)

Note: This script should be run on the EC2 instance in /opt/chrona
EOF
}

# Main script
main() {
    local command="${1:-help}"

    case "$command" in
        check)
            check_environment
            check_database
            ;;
        status)
            check_environment
            check_migrations
            ;;
        migrate)
            check_environment
            run_migrations
            ;;
        create-admin)
            shift
            create_admin "$@"
            ;;
        deploy)
            deploy
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"
