# Guide de Test - Création et Affichage des Codes RH

## 📋 Objectif

Tester le flux complet de création d'un code RH et l'affichage de son QR code.

---

## 🚀 Prérequis

### 1. Backend en cours d'exécution

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Vérification:**
```bash
curl http://localhost:8000/docs
# Devrait afficher la page Swagger UI
```

### 2. Base de données initialisée

```bash
cd backend
alembic upgrade head
```

### 3. Compte admin créé

**Option A: Via script Python**
```bash
cd backend
python -c "
from src.models.user import User
from src.security import get_password_hash
from src.db import engine
from sqlmodel import Session

with Session(engine) as session:
    admin = User(
        email='admin@chrona.local',
        hashed_password=get_password_hash('admin123'),
        role='admin'
    )
    session.add(admin)
    session.commit()
    print(f'Admin créé: {admin.email}')
"
```

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@chrona.local",
    "password": "admin123"
  }'

# Puis promouvoir en admin dans la DB
```

---

## 🧪 Test #1: API Backend (curl)

### Étape 1: Login

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@chrona.local&password=admin123"
```

**Réponse attendue:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Sauvegarder le token:**
```bash
TOKEN="eyJhbGc..."  # Remplacer par le token reçu
```

### Étape 2: Créer un code RH

```bash
curl -X POST http://localhost:8000/admin/hr-codes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_email": "john.doe@example.com",
    "employee_name": "John Doe",
    "expires_in_days": 7
  }'
```

**Réponse attendue:**
```json
{
  "id": 1,
  "code": "EMPL-2025-A7K9X",
  "employee_email": "john.doe@example.com",
  "employee_name": "John Doe",
  "created_by_admin_id": 1,
  "created_at": "2025-01-06T12:00:00Z",
  "expires_at": "2025-01-13T12:00:00Z",
  "is_used": false,
  "used_at": null,
  "used_by_user_id": null
}
```

✅ **Succès:** Le code `EMPL-2025-A7K9X` est créé

❌ **Échec possible:**
- `401 Unauthorized` → Token invalide ou expiré
- `403 Forbidden` → L'utilisateur n'a pas le rôle admin
- `400 Bad Request` → Email invalide ou données manquantes

### Étape 3: Lister les codes RH

```bash
curl -X GET "http://localhost:8000/admin/hr-codes?include_used=false&include_expired=false" \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse attendue:**
```json
[
  {
    "id": 1,
    "code": "EMPL-2025-A7K9X",
    "employee_email": "john.doe@example.com",
    ...
  }
]
```

### Étape 4: Récupérer les données QR (optionnel)

```bash
curl -X GET "http://localhost:8000/admin/hr-codes/1/qr-data" \
  -H "Authorization: Bearer $TOKEN"
```

**Réponse attendue:**
```json
{
  "api_url": "http://localhost:8000",
  "hr_code": "EMPL-2025-A7K9X",
  "employee_email": "john.doe@example.com",
  "employee_name": "John Doe"
}
```

---

## 🧪 Test #2: Script automatisé

Exécuter le script de test fourni:

```bash
./test_hrcode_api.sh
```

**Résultat attendu:**
```
🧪 Test du flux de création de codes RH
========================================

📍 ÉTAPE 1: Login admin
✅ Token reçu: eyJhbGc...

📍 ÉTAPE 2: Créer un code RH
✅ Code RH créé
  ID: 1
  Code: EMPL-2025-A7K9X

📍 ÉTAPE 3: Lister les codes RH
✅ Liste récupérée: 1 code(s)

📍 ÉTAPE 4: Récupérer données QR
✅ Données QR récupérées

========================================
✅ TOUS LES TESTS RÉUSSIS
========================================
```

---

## 🧪 Test #3: Interface Back-Office

### Étape 1: Démarrer le frontend

```bash
cd apps/backoffice
npm install  # Si pas déjà fait
npm run dev
```

**URL:** http://localhost:5173

### Étape 2: Se connecter

- Email: `admin@chrona.local`
- Mot de passe: `admin123`

### Étape 3: Créer un code RH

1. Cliquer sur "Codes RH" dans le menu
2. Cliquer sur "Nouveau code RH" (bouton + en haut à droite)
3. Remplir le formulaire:
   - **Email employé:** `test@example.com`
   - **Nom complet:** `Test User`
   - **Expiration:** `7` jours
4. Cliquer sur "Créer le code"

**Vérification:**
- ✅ Le modal se ferme
- ✅ Le nouveau code apparaît dans la table
- ✅ Le statut est "Valide" (badge vert)

### Étape 4: Afficher le QR code

1. Dans la liste des codes, trouver le code créé
2. Cliquer sur le bouton "QR" à droite de la ligne

**Vérification:**
- ✅ Un modal s'ouvre avec le QR code
- ✅ Le QR code s'affiche (carrés noir et blanc)
- ✅ Le code RH est affiché en dessous: `EMPL-2025-XXXXX`
- ✅ Les informations employé sont correctes
- ✅ La date d'expiration est affichée

### Étape 5: Scanner le QR code

**Option A: Avec un téléphone**
1. Ouvrir l'application Appareil photo
2. Scanner le QR code affiché à l'écran
3. Vérifier le texte détecté: `EMPL-2025-XXXXX`

**Option B: Avec un site web**
1. Télécharger le QR code (bouton "Télécharger")
2. Aller sur https://zxing.org/w/decode
3. Upload l'image
4. Vérifier le texte décodé: `EMPL-2025-XXXXX`

### Étape 6: Télécharger/Imprimer

- ✅ Cliquer sur "Télécharger" → Le QR code est téléchargé en PNG
- ✅ Cliquer sur "Imprimer" → Une fenêtre d'impression s'ouvre avec le QR code formaté

---

## 🐛 Dépannage

### Erreur: "Erreur lors de la création du code RH"

**Vérifier:**

1. **Console navigateur (F12)**
   ```javascript
   // Rechercher les erreurs réseau
   // Onglet "Network" → Filtre "Fetch/XHR"
   // Cliquer sur la requête POST /admin/hr-codes
   // Vérifier le status code et la réponse
   ```

2. **Logs backend**
   ```bash
   # Dans le terminal où uvicorn tourne
   # Rechercher les erreurs Python
   ```

3. **Token JWT**
   ```bash
   # Vérifier si le token est valide
   curl -X GET http://localhost:8000/auth/me \
     -H "Authorization: Bearer $TOKEN"
   ```

### Erreur: "QR code ne s'affiche pas"

**Vérifier:**

1. **Console navigateur**
   ```
   Erreur possible: Failed to load script qrcodejs
   ```
   → Problème de connexion au CDN

2. **Réseau bloqué**
   ```javascript
   // Le script charge depuis:
   https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js
   ```
   → Vérifier pare-feu/proxy

3. **Contenu du QR**
   ```typescript
   // Le QR code encode le texte du code RH
   // Ex: "EMPL-2025-A7K9X"
   ```

### Erreur: "401 Unauthorized"

**Cause:** Token JWT expiré ou invalide

**Solution:**
```bash
# Se reconnecter pour obtenir un nouveau token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@chrona.local&password=admin123"
```

### Erreur: "403 Forbidden"

**Cause:** L'utilisateur n'a pas le rôle `admin`

**Solution:**
```sql
-- Vérifier le rôle dans la DB
SELECT id, email, role FROM users WHERE email = 'admin@chrona.local';

-- Promouvoir en admin si nécessaire
UPDATE users SET role = 'admin' WHERE email = 'admin@chrona.local';
```

---

## 📊 Vérification Base de Données

### Voir les codes RH créés

**PostgreSQL:**
```sql
SELECT
    id,
    code,
    employee_email,
    employee_name,
    created_at,
    expires_at,
    is_used
FROM hr_codes
ORDER BY created_at DESC;
```

**SQLite:**
```bash
sqlite3 backend/app.db "SELECT * FROM hr_codes;"
```

### Compter les codes valides

```sql
SELECT COUNT(*) as codes_valides
FROM hr_codes
WHERE is_used = FALSE
  AND expires_at > CURRENT_TIMESTAMP;
```

---

## ✅ Checklist de Validation

Après avoir suivi tous les tests:

- [ ] Backend démarre sans erreur
- [ ] Login admin réussit (API)
- [ ] Création code RH réussit (API)
- [ ] Liste codes RH réussit (API)
- [ ] Frontend démarre sans erreur
- [ ] Login admin réussit (UI)
- [ ] Création code RH réussit (UI)
- [ ] QR code s'affiche correctement
- [ ] QR code est scannable
- [ ] QR code contient le bon texte
- [ ] Téléchargement QR fonctionne
- [ ] Impression QR fonctionne
- [ ] Code RH visible dans la DB

---

## 🎯 Prochaines Étapes

Si tous les tests passent:
1. ✅ Le système fonctionne correctement
2. 🔄 Tester le flux d'onboarding mobile avec le QR code
3. 🔄 Tester la validation du code RH lors de l'onboarding
4. 🔄 Tester l'expiration des codes

Si des tests échouent:
1. ❌ Identifier l'étape qui échoue
2. 🔍 Consulter les logs (backend + console navigateur)
3. 🐛 Ouvrir une issue avec les logs d'erreur
4. 📧 Fournir les détails du test qui échoue

---

## 📞 Support

En cas de problème:
1. Consulter `HRCODE_FLOW_ANALYSIS.md` pour comprendre le flux
2. Vérifier les logs backend et frontend
3. Tester avec `curl` pour isoler le problème
4. Ouvrir une issue GitHub avec les détails
