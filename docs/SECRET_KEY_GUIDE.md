# Guide Complet: Configuration de la SECRET_KEY

## Qu'est-ce que la SECRET_KEY?

La `SECRET_KEY` est une clé cryptographique utilisée pour:

1. **Signer les JWT tokens** (HS256 - Legacy, si utilisé)
2. **Chiffrer les sessions utilisateur**
3. **Protéger les données sensibles** (cookies de session, CSRF tokens)
4. **Générer des hashes sécurisés**

Exemple dans le code:
```python
# backend/src/security.py
from jose import jwt

# Création d'un token avec SECRET_KEY
token = jwt.encode(
    {"sub": user_id},
    SECRET_KEY,  # ← Utilisé pour signer
    algorithm="HS256"
)
```

**⚠️ Importance:** Si la SECRET_KEY est compromise, tous les tokens et données chiffrées le sont aussi.

---

## Générer une SECRET_KEY Sécurisée

### Recommandations de Base

| Paramètre | Valeur |
|-----------|--------|
| **Longueur minimum** | 32 caractères |
| **Longueur recommandée** | 64+ caractères |
| **Encoding** | Base64 ou URL-safe base64 |
| **Source** | Cryptographiquement sécurisée (`secrets` ou `/dev/urandom`) |
| **Aléatoire** | Non prédictible, unique par environnement |

### Méthode 1: Script Python (Recommandé)

```bash
# Installation: Aucune dépendance externe requise (utilise secrets stdlib)

# Générer et afficher
python backend/tools/generate_secret_key.py

# Générer et ajouter directement au .env.dev
python backend/tools/generate_secret_key.py --env dev

# Générer et ajouter au .env.prod
python backend/tools/generate_secret_key.py --env prod

# Générer avec longueur personnalisée (128 caractères)
python backend/tools/generate_secret_key.py --length 128

# Générer en format base64 (comme openssl rand -base64)
python backend/tools/generate_secret_key.py --no-urlsafe
```

**Avantages:**
- ✅ Pas de dépendances externes
- ✅ Utilise `secrets` module (cryptographiquement sécurisé)
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Peut écrire directement dans le fichier

### Méthode 2: OpenSSL (Natif sur Linux/macOS)

```bash
# Générer en base64 (64 caractères + padding)
openssl rand -base64 64

# Résultat:
# T3F9kL2mN8X5jQ1pR4vY9wZ6aB7cD0eF1gH2iJ3kL4mN5oP6qR7sT8uV9wX0yZ1aB2cD3eF4gH5iJ6kL7m

# Ajouter au fichier .env
openssl rand -base64 64 | tr -d '\n' | xargs -I {} echo "SECRET_KEY={}" >> backend/.env
```

### Méthode 3: Python Built-in (Sans dépendances)

```bash
# Utiliser directement python sans script
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Ajouter au fichier
python3 -c "import secrets; key = secrets.token_urlsafe(64); print('SECRET_KEY=' + key)" >> backend/.env
```

### Méthode 4: PowerShell (Windows)

```powershell
# Générer avec RNGCryptoServiceProvider
$bytes = New-Object byte[] 64
(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
$key = [Convert]::ToBase64String($bytes)
Write-Host "SECRET_KEY=$key"

# Ajouter au fichier .env
Add-Content backend\.env "`nSECRET_KEY=$key"
```

---

## Configuration par Environnement

### Développement (`.env` ou `.env.dev`)

```bash
# Générer une clé pour le développement local
python backend/tools/generate_secret_key.py --env dev

# Résultat dans backend/.env.dev:
# SECRET_KEY=RxJaCXMAm2cR58vJL-VmBy39alcXFSDlbCSKkLCJmflhH8mSQwQVVyCBxRtVoDEgP-3Uzg2zwDue9Vw3pcqZwQ
```

**Spécificités du développement:**
- Peut être moins complexe que la production
- Peut être stockée dans `.env` gitignored
- Peut être partagée entre développeurs (mais pas en production!)
- Doit être régénérée périodiquement

### Staging (`.env.staging`)

```bash
# Générer une clé DIFFÉRENTE pour staging
python backend/tools/generate_secret_key.py --env staging

# Ou manuellement:
openssl rand -base64 64
```

**Règles:**
- ✅ DOIT être différente de celle de développement
- ✅ DOIT être stockée de manière sécurisée (secrets manager)
- ✅ Ne JAMAIS la même que la production

### Production (`.env.production`)

**⚠️ CRITIQUE - Processus Sécurisé:**

```bash
# Sur le serveur de production UNIQUEMENT

# Option 1: Générer directement sur le serveur
ssh admin@prod-server
cd /opt/chrona
SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
echo "SECRET_KEY=$SECRET_KEY" >> .env.production

# Vérifier les permissions
chmod 600 .env.production
chown root:root .env.production
```

**OU Option 2: Avec un Secrets Manager (RECOMMANDÉ)**

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name chrona/production/secret-key \
  --secret-string "$(openssl rand -base64 64)" \
  --kms-key-id arn:aws:kms:region:account:key/id

# Azure Key Vault
az keyvault secret set \
  --vault-name chrona-prod \
  --name secret-key \
  --value "$(openssl rand -base64 64)"

# HashiCorp Vault
vault kv put secret/chrona/production/backend \
  secret_key="$(openssl rand -base64 64)"
```

**OU Option 3: Configuration via Docker Secrets (Swarm):**

```bash
echo "$(openssl rand -base64 64)" | docker secret create chrona_secret_key -
```

---

## Vérification et Validation

### Longueur de la Clé

```bash
# Vérifier la longueur
SECRET_KEY="RxJaCXMAm2cR58vJL-VmBy39alcXFSDlbCSKkLCJmflhH8mSQwQVVyCBxRtVoDEgP-3Uzg2zwDue9Vw3pcqZwQ"
echo ${#SECRET_KEY}  # Affiche: 86

# Vérifier minimum 32 caractères
if [ ${#SECRET_KEY} -lt 32 ]; then
  echo "ERROR: SECRET_KEY too short (minimum 32 chars)"
  exit 1
fi
```

### Vérifier dans le fichier .env

```bash
# Vérifier que la clé est dans le fichier
grep SECRET_KEY backend/.env

# Vérifier la longueur dans le fichier
grep SECRET_KEY backend/.env | cut -d= -f2 | wc -c
```

### Tester le Démarrage de l'Application

```bash
# Vérifier que l'app démarre correctement avec la clé
cd backend
export $(cat .env | xargs)
python -c "
from src.security import get_secret_key
key = get_secret_key()
print(f'✓ SECRET_KEY loaded: {len(key)} chars')
"
```

---

## Erreurs Courantes et Solutions

### Erreur: "Secret key not set" au démarrage

```
ValueError: Secret key must be set in environment or .env file
```

**Solution:**
```bash
# 1. Vérifier que .env existe
ls -la backend/.env

# 2. Vérifier que SECRET_KEY est présente
grep SECRET_KEY backend/.env

# 3. Générer si absente
python backend/tools/generate_secret_key.py --env dev

# 4. Relancer l'app
cd backend && uvicorn src.main:app --reload
```

### Erreur: "Invalid secret key format"

```
ValueError: Secret key must be at least 32 characters
```

**Solution:**
```bash
# La clé est trop courte. Régénérer avec au moins 64 caractères
python backend/tools/generate_secret_key.py --length 64 --env dev
```

### Erreur: "Token verification failed"

```
JWTError: Could not validate credentials
```

**Causes possibles:**
1. La `SECRET_KEY` a changé depuis la création du token
2. Utilisation de clés différentes entre instances

**Solution:**
```bash
# Ne JAMAIS changer la SECRET_KEY sans expirer les tokens existants

# Si vous DEVEZ changer la clé:
# 1. Garder l'ancienne clé pour valider les anciens tokens
# 2. Générer une nouvelle clé pour les nouveaux tokens
# 3. Implémenter un système de rotation
# 4. Attendre l'expiration de tous les anciens tokens
```

---

## Bonnes Pratiques

### ✅ À Faire

- ✅ Générer une clé unique pour chaque environnement
- ✅ Utiliser au moins 64 caractères
- ✅ Stocker dans `.env` ou secrets manager
- ✅ Ne JAMAIS mettre en dur dans le code
- ✅ Ne JAMAIS commiter dans Git
- ✅ Protéger les fichiers `.env` avec chmod 600
- ✅ Rotationner la clé annuellement (ou si compromise)
- ✅ Utiliser des secrets managers en production

### ❌ À Éviter

- ❌ Utiliser la même clé pour tous les environnements
- ❌ Utiliser des clés simples ou prédictibles
- ❌ Stocker dans le code source
- ❌ Commiter dans Git
- ❌ Envoyer par email
- ❌ Logguer ou afficher dans les logs
- ❌ Partager via Slack, email, ou chat non-chiffré
- ❌ Changer fréquemment sans plan de rotation

---

## Gestion des Secrets en Production

### Optio A: Variables d'Environnement

```bash
# Définir via docker-compose
docker compose \
  --env-file .env.production \
  up -d
```

### Option B: Docker Secrets (Swarm)

```yaml
# docker-compose.prod.yml
services:
  backend:
    secrets:
      - chrona_secret_key
    environment:
      SECRET_KEY_FILE: /run/secrets/chrona_secret_key

secrets:
  chrona_secret_key:
    external: true  # Créé avec: echo "key" | docker secret create ...
```

### Option C: AWS Secrets Manager

```python
# backend/src/config.py
import boto3
import json

def get_secret_from_aws():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='chrona/production/secret-key')
    return response['SecretString']

SECRET_KEY = get_secret_from_aws()
```

### Option D: Azure Key Vault

```python
# backend/src/config.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_azure():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url="https://chrona-vault.vault.azure.net/", credential=credential)
    secret = client.get_secret("secret-key")
    return secret.value

SECRET_KEY = get_secret_from_azure()
```

### Option E: HashiCorp Vault

```python
# backend/src/config.py
import hvac

def get_secret_from_vault():
    client = hvac.Client(url='https://vault.chrona.com:8200')
    secret = client.secrets.kv.read_secret_version(path='chrona/production/backend')
    return secret['data']['data']['secret_key']

SECRET_KEY = get_secret_from_vault()
```

---

## Référence Rapide

| Scénario | Commande |
|----------|----------|
| **Dev - Générer et afficher** | `python backend/tools/generate_secret_key.py` |
| **Dev - Ajouter au .env** | `python backend/tools/generate_secret_key.py --env dev` |
| **Prod - Générer sur serveur** | `openssl rand -base64 64` |
| **Prod - Ajouter au .env** | `echo "SECRET_KEY=..." >> .env.production` |
| **Vérifier longueur** | `echo $SECRET_KEY \| wc -c` |
| **Tester l'app** | `cd backend && python -m uvicorn src.main:app --reload` |
| **Voir dans fichier** | `grep SECRET_KEY backend/.env` |

---

## Ressources

- **CLAUDE.md** - Architecture et sécurité globale
- **GUIDE_DEPLOIEMENT.md** - Instructions de déploiement complètes
- **Python `secrets` module** - https://docs.python.org/3/library/secrets.html
- **RFC 2898** - PBKDF2 (password hashing)
- **JWT.io** - Explications JWT

---

**Version:** 1.0
**Dernière mise à jour:** 23 octobre 2025
**Auteur:** Équipe Chrona
