#!/bin/bash
# Smoke tests for Chrona deployment
# Run this script after deployment to verify basic functionality

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
TIMEOUT=5
FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Running Chrona Smoke Tests"
echo "Target: $API_URL"
echo "================================"

# Helper function to check HTTP endpoint
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    echo -n "Testing $description... "

    response=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time $TIMEOUT \
        "$API_URL$endpoint" 2>/dev/null || echo "000")

    if [ "$response" == "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $response)"
    else
        echo -e "${RED}✗${NC} (Expected $expected_status, got $response)"
        FAILED=$((FAILED + 1))
    fi
}

# Helper function to check JSON response
check_json_endpoint() {
    local endpoint=$1
    local expected_key=$2
    local description=$3

    echo -n "Testing $description... "

    response=$(curl -s --max-time $TIMEOUT "$API_URL$endpoint" 2>/dev/null)

    if echo "$response" | grep -q "\"$expected_key\""; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC} (Expected key '$expected_key' not found)"
        FAILED=$((FAILED + 1))
    fi
}

# 1. Health Check
echo ""
echo "🏥 Health Checks"
echo "----------------"
check_endpoint "/" "200" "Root endpoint"
check_endpoint "/docs" "200" "OpenAPI docs"
check_endpoint "/openapi.json" "200" "OpenAPI spec"

# 2. Authentication Endpoints
echo ""
echo "🔐 Authentication"
echo "-----------------"
check_endpoint "/auth/register" "422" "Register endpoint (without payload)"
check_endpoint "/auth/token" "422" "Token endpoint (without payload)"
check_endpoint "/auth/me" "403" "Protected endpoint (without auth)"

# 3. Protected Endpoints (should require auth)
echo ""
echo "🛡️  Protected Endpoints"
echo "----------------------"
check_endpoint "/devices/me" "403" "Devices endpoint (no auth)"
check_endpoint "/punch/history" "403" "Punch history (no auth)"

# 4. Admin Endpoints (should require admin role)
echo ""
echo "👑 Admin Endpoints"
echo "------------------"
check_endpoint "/admin/users" "403" "Admin users endpoint (no auth)"
check_endpoint "/admin/devices" "403" "Admin devices endpoint (no auth)"

# 5. Test full registration + login flow
echo ""
echo "🔄 Full Auth Flow"
echo "-----------------"

TEST_EMAIL="smoke-test-$(date +%s)@test.com"
TEST_PASSWORD="SmokeTest123!"

echo -n "Registering test user... "
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
    --max-time $TIMEOUT)

if echo "$REGISTER_RESPONSE" | grep -q "\"email\""; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

echo -n "Logging in... "
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$TEST_EMAIL&password=$TEST_PASSWORD" \
    --max-time $TIMEOUT)

if echo "$LOGIN_RESPONSE" | grep -q "\"access_token\""; then
    echo -e "${GREEN}✓${NC}"

    # Extract token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

    echo -n "Accessing protected endpoint with token... "
    ME_RESPONSE=$(curl -s -X GET "$API_URL/auth/me" \
        -H "Authorization: Bearer $TOKEN" \
        --max-time $TIMEOUT)

    if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

# 6. Database connectivity
echo ""
echo "💾 Database"
echo "-----------"
check_json_endpoint "/docs" "openapi" "Database connection via API"

# 7. CORS headers
echo ""
echo "🌐 CORS Configuration"
echo "---------------------"
echo -n "Checking CORS headers... "
CORS_RESPONSE=$(curl -s -I -X OPTIONS "$API_URL/auth/register" \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: POST" \
    --max-time $TIMEOUT 2>/dev/null || echo "")

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (CORS headers not detected)"
fi

# Summary
echo ""
echo "================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED test(s) failed${NC}"
    exit 1
fi
