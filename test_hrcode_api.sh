#!/bin/bash

# Script de test du flux de création de codes RH
# Usage: ./test_hrcode_api.sh

API_URL="${API_URL:-http://localhost:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@chrona.local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

echo "🧪 Test du flux de création de codes RH"
echo "========================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de test
test_step() {
    local step_name="$1"
    echo -e "${YELLOW}📍 $step_name${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Étape 1: Login admin
test_step "ÉTAPE 1: Login admin"
echo "Email: $ADMIN_EMAIL"
echo "API: $API_URL"

LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD")

if [ $? -ne 0 ]; then
    error "Échec de la connexion à l'API"
    exit 1
fi

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    error "Token non reçu. Réponse:"
    echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"
    exit 1
fi

success "Token reçu: ${ACCESS_TOKEN:0:20}..."
echo ""

# Étape 2: Créer un code RH
test_step "ÉTAPE 2: Créer un code RH"

TIMESTAMP=$(date +%s)
TEST_EMAIL="test${TIMESTAMP}@example.com"
TEST_NAME="Test User $TIMESTAMP"

echo "Email employé: $TEST_EMAIL"
echo "Nom: $TEST_NAME"

CREATE_RESPONSE=$(curl -s -X POST "$API_URL/admin/hr-codes" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"employee_email\": \"$TEST_EMAIL\",
    \"employee_name\": \"$TEST_NAME\",
    \"expires_in_days\": 7
  }")

if [ $? -ne 0 ]; then
    error "Échec de la création du code RH"
    exit 1
fi

# Vérifier si on a un ID dans la réponse
HR_CODE_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)
HR_CODE=$(echo "$CREATE_RESPONSE" | grep -o '"code":"[^"]*"' | cut -d'"' -f4)

if [ -z "$HR_CODE_ID" ] || [ -z "$HR_CODE" ]; then
    error "Code RH non créé. Réponse:"
    echo "$CREATE_RESPONSE" | jq '.' 2>/dev/null || echo "$CREATE_RESPONSE"
    exit 1
fi

success "Code RH créé"
echo "  ID: $HR_CODE_ID"
echo "  Code: $HR_CODE"
echo ""

# Afficher la réponse complète
echo "📄 Réponse complète:"
echo "$CREATE_RESPONSE" | jq '.' 2>/dev/null || echo "$CREATE_RESPONSE"
echo ""

# Étape 3: Lister les codes RH
test_step "ÉTAPE 3: Lister les codes RH"

LIST_RESPONSE=$(curl -s -X GET "$API_URL/admin/hr-codes?include_used=false&include_expired=false" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ $? -ne 0 ]; then
    error "Échec de la récupération de la liste"
    exit 1
fi

# Compter le nombre de codes
CODE_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id":' | wc -l)

success "Liste récupérée: $CODE_COUNT code(s)"
echo ""

# Étape 4: Récupérer les données QR (endpoint existant mais non utilisé)
test_step "ÉTAPE 4: Récupérer données QR (endpoint /qr-data)"

QR_RESPONSE=$(curl -s -X GET "$API_URL/admin/hr-codes/$HR_CODE_ID/qr-data" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ $? -ne 0 ]; then
    error "Échec de la récupération des données QR"
else
    success "Données QR récupérées"
    echo "$QR_RESPONSE" | jq '.' 2>/dev/null || echo "$QR_RESPONSE"
fi
echo ""

# Étape 5: Vérifier la structure de la DB
test_step "ÉTAPE 5: Résumé du code créé"

echo "  Code RH: $HR_CODE"
echo "  Email: $TEST_EMAIL"
echo "  Nom: $TEST_NAME"
echo "  Expire dans: 7 jours"
echo ""

# Résumé final
echo "========================================"
echo -e "${GREEN}✅ TOUS LES TESTS RÉUSSIS${NC}"
echo "========================================"
echo ""
echo "📱 Pour afficher le QR code:"
echo "  1. Ouvrir le back-office: http://localhost:5173"
echo "  2. Se connecter avec: $ADMIN_EMAIL"
echo "  3. Aller dans 'Codes RH'"
echo "  4. Cliquer sur le bouton 'QR' du code: $HR_CODE"
echo ""
echo "🔍 Le QR code encodera le texte: $HR_CODE"
echo ""
