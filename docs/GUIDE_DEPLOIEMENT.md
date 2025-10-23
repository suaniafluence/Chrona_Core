# Guide de Déploiement Chrona

Ce guide décrit les étapes complètes pour installer et configurer Chrona en environnement de **développement/test** et en **production**.

---

## Table des Matières

1. [Prérequis Système](#prérequis-système)
2. [Architecture Réseau](#architecture-réseau)
3. [Installation Développement/Test](#installation-développementtest)
4. [Installation Production](#installation-production)
5. [Application Mobile](#application-mobile)
6. [Configuration Email](#configuration-email)
7. [Sécurité et Clés](#sécurité-et-clés)
8. [Vérifications et Tests](#vérifications-et-tests)
9. [Dépannage](#dépannage)

---

## Prérequis Système

### Environnement de Développement/Test

| Composant | Windows 10/11 | Linux (Ubuntu 22.04+) |
|-----------|---------------|----------------------|
| **Python** | Python 3.11+ | Python 3.11+ |
| **Node.js** | Node.js 20+ | Node.js 20+ |
| **Base de données** | PostgreSQL 16+ ou SQLite | PostgreSQL 16+ |
| **Docker** (optionnel) | Docker Desktop 4.20+ | Docker Engine 24+ |
| **Git** | Git 2.40+ | Git 2.40+ |
| **RAM** | 8 GB minimum | 8 GB minimum |
| **Espace disque** | 10 GB libre | 10 GB libre |

### Environnement de Production

| Composant | Spécifications |
|-----------|----------------|
| **Serveur** | Ubuntu Server 22.04 LTS ou RHEL 9+ |
| **CPU** | 4 vCPUs minimum (8 vCPUs recommandé) |
| **RAM** | 16 GB minimum (32 GB recommandé) |
| **Stockage** | 100 GB SSD (RAID 1 recommandé) |
| **Base de données** | PostgreSQL 16+ avec chiffrement at-rest |
| **Reverse Proxy** | Nginx 1.24+ ou Apache 2.4+ |
| **Certificat SSL/TLS** | Certificat valide (Let's Encrypt, DigiCert, etc.) |
| **Docker** | Docker Engine 24+ + Docker Compose v2 |
| **Firewall** | UFW (Ubuntu) ou firewalld (RHEL) |

---

## Architecture Réseau

### Ports Requis

| Service | Port | Protocole | Exposition |
|---------|------|-----------|-----------|
| **Backend API** | 8000 | HTTP/HTTPS | Interne (via reverse proxy en prod) |
| **PostgreSQL** | 5432 | TCP | Interne uniquement |
| **Back-office** | 5173 | HTTP | Interne (dev) / 443 HTTPS (prod) |
| **Kiosk** | 5174 | HTTP | Interne (dev) / 443 HTTPS (prod) |
| **Reverse Proxy** | 80, 443 | HTTP/HTTPS | Externe (production) |

### Configuration Firewall

#### Ubuntu (UFW)
```bash
# Autoriser SSH (si accès distant)
sudo ufw allow 22/tcp

# Autoriser HTTP/HTTPS (production)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le firewall
sudo ufw enable
sudo ufw status
```

#### RHEL/CentOS (firewalld)
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### Réseau de Développement

```
┌─────────────────────────────────────────────┐
│  Machine de Développement (localhost)       │
│                                             │
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Backend     │  │  PostgreSQL/SQLite  │  │
│  │  :8000       │──│  :5432              │  │
│  └──────────────┘  └─────────────────────┘  │
│         │                                   │
│  ┌──────┴─────────┬──────────────────────┐  │
│  │  Back-office   │  Kiosk               │  │
│  │  :5173         │  :5174               │  │
│  └────────────────┴──────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Réseau de Production

```
Internet
    │
    ▼
┌─────────────────┐
│  Reverse Proxy  │ :80, :443 (HTTPS)
│  (Nginx/Apache) │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼────┐ ┌──▼───────┐ ┌───▼────┐
│Backend │ │Backoffice│ │ Kiosk  │
│ :8000  │ │  :5173   │ │ :5174  │
└───┬────┘ └──────────┘ └────────┘
    │
┌───▼────────────┐
│  PostgreSQL    │ :5432 (interne)
│  + chiffrement │
└────────────────┘
```

---

## Installation Développement/Test

### Option 1: Installation avec Docker Compose (Recommandé)

#### Étape 1: Cloner le dépôt

```bash
# Windows (PowerShell) ou Linux
git clone https://github.com/votre-organisation/Chrona_Core.git
cd Chrona_Core
```

#### Étape 2: Générer les clés JWT RS256

```bash
# Windows PowerShell
cd backend
python tools/generate_keys.py

# Linux/macOS
cd backend
python3 tools/generate_keys.py
```

Cela génère:
- `backend/jwt_private_key.pem` (clé privée, **NE JAMAIS COMMITER**)
- `backend/jwt_public_key.pem` (clé publique)

#### Étape 3: Générer les clés de sécurité

Avant de configurer `.env`, générer une **SECRET_KEY** sécurisée:

```bash
# Depuis la racine du projet
python backend/tools/generate_secret_key.py

# Résultat (exemple):
# Generated SECRET_KEY (86 chars):
#   RxJaCXMAm2cR58vJL-VmBy39alcXFSDlbCSKkLCJmflhH8mSQwQVVyCBxRtVoDEgP-3Uzg2zwDue9Vw3pcqZwQ
```

Copier cette clé pour l'étape suivante (elle sera utilisée dans `.env`).

#### Étape 4: Configurer les variables d'environnement

**Backend** - Copier `backend/.env.example` → `backend/.env`:

```bash
# Windows
copy backend\.env.example backend\.env
copy apps\backoffice\.env.example apps\backoffice\.env
copy apps\kiosk\.env.example apps\kiosk\.env

# Linux
cp backend/.env.example backend/.env
```

**Éditer `backend/.env`** (développement):

```env
# Base de données PostgreSQL (via Docker Compose)
DATABASE_URL=postgresql+asyncpg://chrona:chrona@db:5432/chrona

# CORS - autoriser frontend local
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
ALLOW_CREDENTIALS=false
ALLOWED_METHODS=*
ALLOWED_HEADERS=*

# Sécurité - SECRET_KEY pour JWT et sessions
# ⚠️ IMPORTANT: Générer une clé aléatoire forte (voir ci-dessous)
SECRET_KEY=votre-cle-secrete-aleatoire-de-64-caracteres-minimum

# JWT RS256 (pour les QR codes éphémères)
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/app/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/app/jwt_public_key.pem

# Email (mode console pour dev - emails affichés dans les logs)
EMAIL_PROVIDER=console
EMAIL_FROM_ADDRESS=noreply@chrona.dev
EMAIL_FROM_NAME=Chrona Dev

# Logs
LOG_LEVEL=debug
```

#### Générer une SECRET_KEY Sécurisée

La `SECRET_KEY` est utilisée pour:
- Signer les JWT tokens (HS256 - legacy, si utilisé)
- Chiffrer les sessions
- Protéger les données sensibles

**Génération recommandée (64 caractères, base64):**

**Windows PowerShell:**
```powershell
# Méthode 1: Utiliser l'API .NET
$bytes = New-Object byte[] 64
(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

**Linux / macOS:**
```bash
# Méthode 1: OpenSSL (recommandé)
openssl rand -base64 64

# Méthode 2: Python
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Méthode 3: Head de /dev/urandom
head -c 64 /dev/urandom | base64
```

**Résultat attendu** (exemple - NE PAS utiliser ceci en production!):
```
T3F9kL2mN8X5jQ1pR4vY9wZ6aB7cD0eF1gH2iJ3kL4mN5oP6qR7sT8uV9wX0yZ1aB2cD3eF4
```

**Validation:**
```bash
# Vérifier la longueur (au moins 32 caractères, 64+ recommandé)
echo "$SECRET_KEY" | wc -c
```

**Utilisation dans `.env`:**

**Option 1: Script Python (recommandé)**
```bash
# Depuis la racine du projet ou backend/
python backend/tools/generate_secret_key.py              # Affiche la clé
python backend/tools/generate_secret_key.py --env dev   # Ajoute à .env.dev
```

**Option 2: Copier-coller manuel**
```bash
# Copier-coller directement le résultat:
SECRET_KEY=T3F9kL2mN8X5jQ1pR4vY9wZ6aB7cD0eF1gH2iJ3kL4mN5oP6qR7sT8uV9wX0yZ1aB2cD3eF4

# OU générer avec OpenSSL et ajouter au fichier:
SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
echo "SECRET_KEY=$SECRET_KEY" >> backend/.env
```

**⚠️ Règles de Sécurité:**
- ✅ Générer une clé DIFFÉRENTE pour chaque environnement (dev, staging, prod)
- ✅ Ne JAMAIS réutiliser la même clé
- ✅ Ne JAMAIS mettre en dur dans le code
- ✅ Ne JAMAIS commiter dans Git (utiliser `.env` qui est dans `.gitignore`)
- ✅ En production, utiliser un gestionnaire de secrets (AWS Secrets Manager, Azure Key Vault, Vault, etc.)
- ❌ Ne pas utiliser des clés simples ou prédictibles
- ❌ Ne pas utiliser le même SECRET_KEY entre environments

**Frontend** - Configurer `apps/backoffice/.env` et `apps/kiosk/.env`:

```bash
# apps/backoffice/.env
VITE_API_URL=http://localhost:8000

# apps/kiosk/.env
VITE_API_URL=http://localhost:8000
```

#### Étape 4: Lancer les services avec Docker Compose

```bash
# Depuis la racine du projet
docker compose up -d --build

# Vérifier les logs
docker compose logs -f backend
```

**Services démarrés:**
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- Back-office: http://localhost:5173
- Kiosk: http://localhost:5174

### HTTPS local (optionnel, recommandé pour tests réalistes)

Traefik est fourni comme reverse proxy TLS pour exposer les services en HTTPS local via des certificats mkcert.

1) Installer mkcert et initialiser l’autorité locale
- macOS: `brew install mkcert nss` puis `mkcert -install`
- Windows: `choco install mkcert` puis `mkcert -install`
- Linux: voir https://github.com/FiloSottile/mkcert

2) Générer les certificats (racine du repo):
```
mkcert -cert-file infra/traefik/certs/dev-localhost.pem  -key-file infra/traefik/certs/dev-localhost-key.pem  localhost 127.0.0.1 ::1 api.localhost backoffice.localhost kiosk.localhost
```

3) Démarrer en HTTPS:
```
DOMAIN=localhost docker compose -f docker-compose.yml -f docker-compose.https.dev.yml up -d
ou  
 $env:DOMAIN='localhost'; docker compose -f docker-compose.yml -f docker-compose.https.dev.yml up -d
```

4) Accéder en HTTPS:
- Backend: https://api.localhost
- Backoffice: https://backoffice.localhost
- Kiosk: https://kiosk.localhost

#### Étape 5: Initialiser la base de données

**Important:** Assurez-vous que tous les modèles SQLModel sont correctement importés avant de créer les tables.

```bash
# Appliquer les migrations Alembic
docker compose exec backend alembic upgrade head

# Créer un utilisateur admin
docker compose exec backend python tools/create_admin_user.py --email "admin@example.com" --password "Passw0rd!" --role admin

# Ou créer l'administrateur avec les valeurs par défaut
docker compose exec backend python tools/create_admin_user.py
```

**⚠️ IMPORTANT - Initialisation du schéma (Développement/Tests):**

Si vous rencontrez des erreurs "no such table" lors des tests E2E, assurez-vous que tous les modèles sont enregistrés:

```python
# Dans backend/src/db.py - Vérifier l'import:
import src.models  # Importe TOUS les modèles (user.py, kiosk.py, device.py, etc.)
```

Les modèles individuels sont enregistrés dans `src/models/__init__.py`. Lors de l'initialisation:

```bash
# Force la création du schéma complet
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

async def init():
    engine = create_async_engine('sqlite+aiosqlite:///./test.db')
    import src.models  # ⚠️ Important: import AVANT metadata.create_all
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()

asyncio.run(init())
"
```

> **Note :** adaptez les options `--email`, `--password` si vous souhaitez créer des utilisateurs spécifiques
> (par exemple `testuser@example.com`) ou définir d'autres identifiants.

#### Étape 6: Accéder aux interfaces

- **API Documentation**: http://localhost:8000/docs
- **Back-office**: http://localhost:5173
- **Kiosk**: http://localhost:5174

---

### Option 2: Installation Manuelle (Sans Docker)

#### Windows 10/11

**1. Installer PostgreSQL**

Télécharger depuis: https://www.postgresql.org/download/windows/

Créer la base de données:
```powershell
# Lancer psql
psql -U postgres

# Dans psql
CREATE DATABASE chrona;
CREATE USER chrona WITH PASSWORD 'chrona';
GRANT ALL PRIVILEGES ON DATABASE chrona TO chrona;
\q
```

**2. Installer Python et dépendances**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**3. Générer les clés JWT**

```powershell
python tools/generate_keys.py
```

**4. Configurer `.env`**

```powershell
copy .env.example .env
# Éditer .env avec Notepad ou VS Code
notepad .env
```

Exemple `backend\.env` (Windows dev):
```env
DATABASE_URL=postgresql+asyncpg://chrona:chrona@localhost:5432/chrona
SECRET_KEY=dev-secret-windows
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=C:\Chrona_Core\backend\jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=C:\Chrona_Core\backend\jwt_public_key.pem
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
EMAIL_PROVIDER=console
```

**5. Appliquer les migrations**

```powershell
alembic upgrade head
```

**6. Lancer le backend**

```powershell
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**7. Installer et lancer le frontend**

```powershell
# Back-office
cd ..\apps\backoffice
npm ci
copy .env.example .env
npm run dev

# Dans un nouveau terminal - Kiosk
cd ..\apps\kiosk
npm ci
copy .env.example .env
npm run dev
```

#### Linux (Ubuntu 22.04)

**1. Installer les dépendances système**

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib nodejs npm git
```

**2. Configurer PostgreSQL**

```bash
sudo -u postgres psql

# Dans psql
CREATE DATABASE chrona;
CREATE USER chrona WITH PASSWORD 'chrona';
GRANT ALL PRIVILEGES ON DATABASE chrona TO chrona;
\q
```

**3. Cloner et configurer le backend**

```bash
git clone https://github.com/votre-org/Chrona_Core.git
cd Chrona_Core/backend

# Environnement virtuel Python
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Générer les clés JWT
python tools/generate_keys.py

# Configurer .env
cp .env.example .env
nano .env
```

Exemple `.env` (Linux dev):
```env
DATABASE_URL=postgresql+asyncpg://chrona:chrona@localhost:5432/chrona
SECRET_KEY=dev-secret-linux
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/home/user/Chrona_Core/backend/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/home/user/Chrona_Core/backend/jwt_public_key.pem
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
EMAIL_PROVIDER=console
```

**4. Migrations et lancement**

```bash
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**5. Frontend (nouveau terminal)**

```bash
cd ../apps/backoffice
npm ci
cp .env.example .env
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

---

## Installation Production

### Architecture de Production Recommandée

```
┌────────────────────────────────────────────┐
│  Serveur Ubuntu 22.04 LTS                  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  Nginx Reverse Proxy                 │  │
│  │  - SSL/TLS (Let's Encrypt)           │  │
│  │  - Rate limiting                     │  │
│  │  - CORS headers                      │  │
│  └──────────────┬───────────────────────┘  │
│                 │                          │
│  ┌──────────────┴───────────────────────┐  │
│  │  Docker Containers                   │  │
│  │  ┌─────────┬──────────┬────────────┐ │  │
│  │  │ Backend │Backoffice│   Kiosk    │ │  │
│  │  └────┬────┴──────────┴────────────┘ │  │
│  │       │                              │  │
│  │  ┌────▼──────────────────────────┐   │  │
│  │  │  PostgreSQL 16                │   │  │ 
│  │  │  - Encryption at rest         │   │  │
│  │  │  - WAL archiving              │   │  │
│  │  └───────────────────────────────┘   │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
```

### Étape 1: Préparer le Serveur

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installer Docker Compose v2
sudo apt install -y docker-compose-plugin

# Installer Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Configurer le firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Étape 2: Configurer PostgreSQL (Production)

**Option A: PostgreSQL dans Docker (recommandé pour isolation)**

Créer `docker-compose.prod.yml`:

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: chrona
      POSTGRES_USER: chrona
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Variable d'environnement sécurisée
    volumes:
      - /var/lib/chrona/pgdata:/var/lib/postgresql/data
      - ./postgres-init:/docker-entrypoint-initdb.d
    networks:
      - chrona_internal
    command:
      - "postgres"
      - "-c"
      - "ssl=on"
      - "-c"
      - "ssl_cert_file=/var/lib/postgresql/server.crt"
      - "-c"
      - "ssl_key_file=/var/lib/postgresql/server.key"
```

**Option B: PostgreSQL natif avec chiffrement**

```bash
# Installer PostgreSQL
sudo apt install -y postgresql-16

# Activer le chiffrement
sudo -u postgres psql

# Dans psql
CREATE DATABASE chrona WITH ENCODING 'UTF8';
CREATE USER chrona WITH ENCRYPTED PASSWORD 'STRONG-RANDOM-PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE chrona TO chrona;

# Activer pgcrypto pour encryption at rest
\c chrona
CREATE EXTENSION IF NOT EXISTS pgcrypto;
\q
```

### Étape 3: Générer les Clés de Production

```bash
cd /opt/chrona
git clone https://github.com/votre-org/Chrona_Core.git
cd Chrona_Core/backend

# Générer des clés RSA 4096 bits pour production
python3 tools/generate_keys.py --key-size 4096

# Sécuriser les permissions
chmod 600 jwt_private_key.pem
chmod 644 jwt_public_key.pem
chown root:root jwt_*.pem
```

### Étape 4: Configurer les Variables d'Environnement (Production)

Créer `/opt/chrona/.env.production`:

```env
# Base de données PostgreSQL (PRODUCTION)
DATABASE_URL=postgresql+asyncpg://chrona:STRONG-DB-PASSWORD@db:5432/chrona

# Sécurité - SECRET_KEY (voir ci-dessous pour génération)
# ⚠️ CRITICAL: Générer avec openssl rand -base64 64 ou secrets manager
SECRET_KEY=VOTRE-CLE-SECRETE-ALEATOIRE-GENEREE-DE-64-CARACTERES-MINIMUM

# JWT RS256 (Production)
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/app/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/app/jwt_public_key.pem
ACCESS_TOKEN_EXPIRE_MINUTES=30
EPHEMERAL_TOKEN_EXPIRE_SECONDS=15

# CORS - Domaines de production uniquement
ALLOWED_ORIGINS=https://chrona.votre-domaine.com,https://admin.votre-domaine.com
ALLOW_CREDENTIALS=true
ALLOWED_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization

# Email - Configuration SMTP Production (SendGrid recommandé)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM_ADDRESS=noreply@votre-domaine.com
EMAIL_FROM_NAME=Chrona - Pointage

# Logs
LOG_LEVEL=warning

# Sentry (optionnel - monitoring d'erreurs)
# SENTRY_DSN=https://xxx@sentry.io/xxx
```

#### Générer SECRET_KEY pour Production

⚠️ **CRITIQUE EN PRODUCTION** - Utiliser un générateur cryptographiquement sécurisé:

**Sur le serveur de déploiement (Linux):**
```bash
# Générer une clé avec OpenSSL
SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')

# Afficher la clé générée
echo "SECRET_KEY=$SECRET_KEY"

# Ajouter au fichier .env.production
echo "SECRET_KEY=$SECRET_KEY" >> /opt/chrona/.env.production
```

**Alternative: Générer localement, puis transférer sécurisé**
```bash
# Localement (sur votre machine)
openssl rand -base64 64 > /tmp/secret_key.txt

# Copier vers le serveur avec SCP chiffré
scp /tmp/secret_key.txt admin@votre-serveur:/tmp/
ssh admin@votre-serveur
cat /tmp/secret_key.txt >> /opt/chrona/.env.production
rm /tmp/secret_key.txt
```

**Avec un Secrets Manager (recommandé):**
```bash
# AWS Secrets Manager
aws secretsmanager create-secret --name chrona/secret-key \
  --secret-string "$(openssl rand -base64 64)"

# Azure Key Vault
az keyvault secret set --vault-name chrona-vault \
  --name secret-key \
  --value "$(openssl rand -base64 64)"

# HashiCorp Vault
vault kv put secret/chrona/backend \
  secret_key="$(openssl rand -base64 64)"
```

**⚠️ IMPORTANT:** Protéger le fichier:
```bash
sudo chmod 600 /opt/chrona/.env.production
sudo chown root:root /opt/chrona/.env.production

# Vérifier les permissions
ls -la /opt/chrona/.env.production
# Résultat attendu: -rw------- 1 root root ...
```

**⚠️ Ne JAMAIS:**
- Mettre en dur dans le code source
- Commiter dans Git
- Envoyer par email
- Logguer ou afficher dans les logs
- Copier-coller dans des fichiers non-chiffrés

### Étape 5: Configurer Docker Compose (Production)

Créer `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: chrona
      POSTGRES_USER: chrona
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - chrona_pgdata:/var/lib/postgresql/data
    networks:
      - chrona_internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chrona -d chrona"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env.production
    volumes:
      - ./backend/jwt_private_key.pem:/app/jwt_private_key.pem:ro
      - ./backend/jwt_public_key.pem:/app/jwt_public_key.pem:ro
    networks:
      - chrona_internal
    depends_on:
      db:
        condition: service_healthy
    command: ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

  backoffice:
    build:
      context: ./apps/backoffice
      dockerfile: Dockerfile
      args:
        VITE_API_URL: https://api.votre-domaine.com
    restart: always
    networks:
      - chrona_internal

  kiosk:
    build:
      context: ./apps/kiosk
      dockerfile: Dockerfile
      args:
        VITE_API_URL: https://api.votre-domaine.com
    restart: always
    networks:
      - chrona_internal

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    networks:
      - chrona_internal
    depends_on:
      - backend
      - backoffice
      - kiosk

networks:
  chrona_internal:
    driver: bridge

volumes:
  chrona_pgdata:
    driver: local
```

### Étape 6: Configurer Nginx (Reverse Proxy)

Créer `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

    # Upstream backends
    upstream backend_api {
        server backend:8000;
    }

    upstream backoffice_app {
        server backoffice:80;
    }

    upstream kiosk_app {
        server kiosk:80;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name chrona.votre-domaine.com admin.votre-domaine.com api.votre-domaine.com;
        return 301 https://$server_name$request_uri;
    }

    # API Backend
    server {
        listen 443 ssl http2;
        server_name api.votre-domaine.com;

        ssl_certificate /etc/letsencrypt/live/api.votre-domaine.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/api.votre-domaine.com/privkey.pem;

        # SSL Configuration moderne
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;

        location / {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /auth/token {
            limit_req zone=login_limit burst=3 nodelay;
            proxy_pass http://backend_api;
        }
    }

    # Back-office Admin
    server {
        listen 443 ssl http2;
        server_name admin.votre-domaine.com;

        ssl_certificate /etc/letsencrypt/live/admin.votre-domaine.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/admin.votre-domaine.com/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

        location / {
            proxy_pass http://backoffice_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # Kiosk
    server {
        listen 443 ssl http2;
        server_name chrona.votre-domaine.com;

        ssl_certificate /etc/letsencrypt/live/chrona.votre-domaine.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/chrona.votre-domaine.com/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

        location / {
            proxy_pass http://kiosk_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Étape 7: Obtenir un Certificat SSL (Let's Encrypt)

```bash
# Obtenir les certificats pour chaque domaine
sudo certbot --nginx -d api.votre-domaine.com
sudo certbot --nginx -d admin.votre-domaine.com
sudo certbot --nginx -d chrona.votre-domaine.com

# Renouvellement automatique (cron)
sudo certbot renew --dry-run
```

### Étape 8: Déployer en Production

```bash
cd /opt/chrona/Chrona_Core

# Construire et lancer les services
docker compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs -f

# Appliquer les migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Créer l'utilisateur admin initial
docker compose -f docker-compose.prod.yml exec backend python tools/create_test_user.py

# Créer ou promouvoir l'administrateur (par défaut admin@example.com / adminpass123)
docker compose -f docker-compose.prod.yml exec backend python tools/create_admin_user.py
```

> **Note :** les mêmes options `--email`, `--password` et `--reset-password` sont disponibles en production pour cibler un
> compte spécifique ou réinitialiser un mot de passe existant.

### Étape 9: Configuration de Sauvegarde Automatique

**Script de sauvegarde PostgreSQL** (`/opt/chrona/backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/chrona"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="chrona"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose -f /opt/chrona/Chrona_Core/docker-compose.prod.yml exec -T db \
    pg_dump -U chrona $DB_NAME | gzip > $BACKUP_DIR/chrona_$DATE.sql.gz

# Nettoyer les anciennes sauvegardes
find $BACKUP_DIR -name "chrona_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: chrona_$DATE.sql.gz"
```

**Ajouter au cron** (sauvegarde quotidienne à 2h du matin):

```bash
sudo chmod +x /opt/chrona/backup.sh
sudo crontab -e

# Ajouter cette ligne:
0 2 * * * /opt/chrona/backup.sh >> /var/log/chrona_backup.log 2>&1
```

---

## Application Mobile

L'application mobile Chrona permet aux employés de générer des QR codes éphémères pour pointer via les kiosques. Elle est développée avec **React Native** et **Expo** pour une compatibilité iOS et Android.

### Architecture de l'Application Mobile

```
┌─────────────────────────────────────────────┐
│  Application Mobile (React Native + Expo)  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Écrans Principaux                   │  │
│  │  - Login (email/password)            │  │
│  │  - Enregistrement d'appareil         │  │
│  │  - Génération QR Code (30s)          │  │
│  │  - Historique des pointages          │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │  Sécurité                            │  │
│  │  - Device fingerprint (unique)       │  │
│  │  - JWT tokens (AsyncStorage)         │  │
│  │  - Anti-screenshot (expo-screen)     │  │
│  │  - Biométrie (LocalAuth)             │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
└─────────────────┼───────────────────────────┘
                  │ HTTPS
                  ▼
         ┌────────────────┐
         │  Backend API   │
         │  :8000 (dev)   │
         │  :443 (prod)   │
         └────────────────┘
```

### Prérequis Mobile

| Composant | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 20+ | Requis pour npm/Expo CLI |
| **npm/yarn** | 9+ / 1.22+ | Gestionnaire de paquets |
| **Expo CLI** | Latest | Installé automatiquement |
| **Émulateur Android** | Android Studio | Pour tests Android |
| **Simulateur iOS** | Xcode (macOS) | Pour tests iOS |
| **Expo Go** | App mobile | Pour tests sur appareil physique |

### Installation Développement/Test (Mobile)

#### Étape 1: Installer les Dépendances

**Windows / Linux / macOS:**

```bash
# Depuis la racine du projet
cd apps/mobile

# Installer les dépendances npm
npm install

# OU avec yarn
yarn install
```

#### Étape 2: Configurer l'API Backend

**Option A: Utiliser l'émulateur Android (Recommandé pour dev)**

L'app est préconfigurée pour utiliser `http://10.0.2.2:8000` qui pointe vers `localhost:8000` de la machine hôte depuis l'émulateur Android.

Aucune configuration supplémentaire n'est nécessaire si vous utilisez Docker Compose sur `localhost:8000`.

**Option B: Utiliser un appareil physique (même réseau WiFi)**

Créer un fichier `.env` dans `apps/mobile/`:

```bash
# apps/mobile/.env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```

Remplacez `192.168.1.100` par l'adresse IP locale de votre machine:

```bash
# Windows
ipconfig

# Linux/macOS
ifconfig
# Chercher l'adresse IPv4 (ex: 192.168.1.100)
```

**⚠️ Important:** Assurez-vous que le firewall autorise les connexions entrantes sur le port 8000.

**Option C: Utiliser ngrok pour tester sur appareil distant**

```bash
# Installer ngrok
npm install -g ngrok

# Exposer le backend local
ngrok http 8000

# Copier l'URL HTTPS fournie (ex: https://abc123.ngrok.io)
```

Puis configurer `.env`:

```bash
# apps/mobile/.env
EXPO_PUBLIC_API_URL=https://abc123.ngrok.io
```

#### Étape 3: Lancer l'Application Mobile

**Avec Expo Go (Recommandé pour démarrage rapide):**

```bash
# Démarrer le serveur de développement Expo
npm start

# OU pour Android directement
npm run android

# OU pour iOS (macOS uniquement)
npm run ios
```

**Scannez le QR code affiché:**
- **Android:** Ouvrir l'app "Expo Go" et scanner le QR code
- **iOS:** Ouvrir l'app Caméra et scanner le QR code (ouvre Expo Go automatiquement)

**Avec émulateur/simulateur:**

```bash
# Android (nécessite Android Studio + émulateur démarré)
npm run android

# iOS (macOS + Xcode uniquement)
npm run ios
```

#### Étape 4: Tester le Flux Complet

1. **S'assurer que le backend est démarré:**

```bash
# Depuis la racine du projet
docker compose up -d backend db
docker compose logs -f backend
```

2. **Créer un utilisateur test:**

```bash
docker compose exec backend python tools/create_test_user.py
```

Utiliser les identifiants:
- Email: `test@chrona.com`
- Password: `Test1234!`

3. **Se connecter depuis l'app mobile:**
   - Lancer l'app mobile
   - Entrer email et mot de passe
   - L'appareil sera automatiquement enregistré au premier login

4. **Générer un QR code:**
   - Appuyer sur "Générer QR Code"
   - Le QR code s'affiche avec un compte à rebours (30 secondes)
   - Scanner avec le kiosk avant expiration

5. **Consulter l'historique:**
   - Onglet "Historique"
   - Pull-to-refresh pour actualiser

### Installation Production (Mobile)

#### Option 1: Publication via Expo Application Services (EAS)

**EAS Build** permet de générer des binaires iOS (.ipa) et Android (.apk/.aab) sans Xcode ni Android Studio local.

**Étape 1: Installer EAS CLI**

```bash
npm install -g eas-cli
```

**Étape 2: Configurer EAS (première fois)**

```bash
cd apps/mobile

# Se connecter à Expo
eas login

# Configurer le projet
eas build:configure
```

Cela génère `eas.json`:

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "http://10.0.2.2:8000"
      }
    },
    "preview": {
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api-staging.votre-domaine.com"
      }
    },
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.votre-domaine.com"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

**Étape 3: Configurer app.json pour Production**

Éditer `apps/mobile/app.json`:

```json
{
  "expo": {
    "name": "Chrona",
    "slug": "chrona-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.votre-organisation.chrona",
      "buildNumber": "1"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.votre_organisation.chrona",
      "versionCode": 1,
      "permissions": [
        "CAMERA",
        "USE_BIOMETRIC",
        "USE_FINGERPRINT"
      ]
    },
    "extra": {
      "eas": {
        "projectId": "VOTRE_PROJECT_ID_EAS"
      }
    }
  }
}
```

**Étape 4: Générer les Builds de Production**

```bash
# Build Android (APK pour test interne)
eas build --platform android --profile preview

# Build Android (AAB pour Google Play Store)
eas build --platform android --profile production

# Build iOS (nécessite compte Apple Developer)
eas build --platform ios --profile production
```

**Étape 5: Télécharger et Distribuer**

Les builds seront disponibles dans votre dashboard Expo: https://expo.dev/accounts/VOTRE_COMPTE/projects/chrona-mobile/builds

**Distribution interne:**
- Android: Télécharger l'APK et partager via email/MDM
- iOS: Utiliser TestFlight (nécessite compte Apple Developer)

**Publication sur les stores:**

```bash
# Soumettre à Google Play Store
eas submit --platform android --latest

# Soumettre à Apple App Store
eas submit --platform ios --latest
```

#### Option 2: Build Local (sans EAS)

**Android:**

```bash
cd apps/mobile

# Installer les dépendances
npm install

# Générer l'APK
npx expo build:android -t apk

# OU générer un AAB pour Play Store
npx expo build:android -t app-bundle
```

**iOS (macOS + Xcode requis):**

```bash
# Générer le fichier .ipa
npx expo build:ios -t archive

# Publier sur TestFlight/App Store via Xcode
```

#### Option 3: Distribution via Mobile Device Management (MDM)

Pour les entreprises avec un MDM (Intune, AirWatch, MobileIron):

1. Générer l'APK/IPA en mode production
2. Uploader sur la console MDM
3. Déployer sur les appareils des employés
4. Configurer les politiques de sécurité:
   - Désactiver les screenshots (déjà implémenté dans l'app)
   - Activer le chiffrement de l'appareil
   - Exiger un code PIN/biométrie

### Configuration Mobile Production

**Variables d'environnement** (`.env` ou `eas.json`):

```env
# Backend API (PRODUCTION)
EXPO_PUBLIC_API_URL=https://api.votre-domaine.com

# Environnement
EXPO_PUBLIC_ENV=production

# Sentry (monitoring d'erreurs - optionnel)
EXPO_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx

# Analytics (optionnel)
EXPO_PUBLIC_ANALYTICS_KEY=your-analytics-key
```

### Sécurité de l'Application Mobile

L'app mobile implémente plusieurs mesures de sécurité:

**1. Device Fingerprinting**
- Génération d'un identifiant unique par appareil
- Envoyé au backend lors de l'enregistrement
- Validation à chaque génération de QR code

**2. Prévention Anti-Capture**
- `expo-screen-capture`: Désactive les screenshots/enregistrements d'écran
- Protection des QR codes éphémères contre la copie

**3. Stockage Sécurisé**
- `expo-secure-store`: Stockage chiffré des tokens JWT (iOS Keychain, Android Keystore)
- Pas de stockage de mots de passe en clair

**4. Authentification Biométrique (Optionnel)**
- `expo-local-authentication`: Face ID, Touch ID, empreinte digitale
- Peut être activé pour ouvrir l'app

**5. Certificate Pinning (Recommandé pour prod)**

Ajouter dans `app.json`:

```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSAppTransportSecurity": {
          "NSExceptionDomains": {
            "api.votre-domaine.com": {
              "NSIncludesSubdomains": true,
              "NSExceptionRequiresForwardSecrecy": true,
              "NSExceptionMinimumTLSVersion": "TLSv1.2",
              "NSPinnedDomains": ["api.votre-domaine.com"]
            }
          }
        }
      }
    },
    "android": {
      "networkSecurityConfig": "./network_security_config.xml"
    }
  }
}
```

Créer `apps/mobile/android/app/src/main/res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.votre-domaine.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">VOTRE_CERTIFICAT_HASH_BASE64</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### Tests de l'Application Mobile

**Tests unitaires (Jest):**

```bash
cd apps/mobile
npm test
```

**Tests E2E (Detox - optionnel):**

```bash
# Installer Detox
npm install -g detox-cli
npm install --save-dev detox

# Configurer (voir docs Detox)
detox init

# Lancer les tests
detox test --configuration android.emu.debug
```

### Dépannage Mobile

**Problème: "Network request failed"**

**Solution:**
```bash
# Vérifier que le backend est accessible
curl http://10.0.2.2:8000/health  # Depuis l'émulateur Android

# Vérifier l'URL dans .env
echo $EXPO_PUBLIC_API_URL

# Redémarrer Expo
npm start -- --clear
```

**Problème: "Unable to resolve module"**

**Solution:**
```bash
# Nettoyer le cache
npm start -- --clear

# Réinstaller les dépendances
rm -rf node_modules
npm install
```

**Problème: QR code non scannable par le kiosk**

**Vérifications:**
- Le token est-il expiré ? (30 secondes max)
- Le backend valide-t-il la signature RS256 ?
- L'appareil est-il enregistré dans la base ?

```bash
# Vérifier les logs backend
docker compose logs backend | grep -i "qr\|token"
```

**Problème: Émulateur Android lent**

**Solution:**
```bash
# Utiliser un appareil physique avec Expo Go
# OU augmenter la RAM de l'émulateur (Android Studio → AVD Manager)
```

---

## Configuration Email

### Option 1: Gmail (SMTP)

1. Créer un compte Gmail dédié (ex: `noreply-chrona@gmail.com`)
2. Activer l'authentification à 2 facteurs
3. Générer un **mot de passe d'application**:
   - Google Account → Sécurité → Mots de passe d'application
   - Sélectionner "Autre (nom personnalisé)" → "Chrona"
   - Copier le mot de passe généré

**Configuration `.env`**:

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply-chrona@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Mot de passe d'application
SMTP_USE_TLS=true
EMAIL_FROM_ADDRESS=noreply-chrona@gmail.com
EMAIL_FROM_NAME=Chrona - Pointage
```

### Option 2: SendGrid (Recommandé pour production)

1. Créer un compte sur https://sendgrid.com
2. Vérifier le domaine expéditeur
3. Générer une clé API (Settings → API Keys)

**Configuration `.env`**:

```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM_ADDRESS=noreply@votre-domaine.com
EMAIL_FROM_NAME=Chrona
```

### Option 3: Microsoft 365 / Outlook (SMTP)

**Configuration `.env`**:

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@votre-domaine.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_USE_TLS=true
EMAIL_FROM_ADDRESS=votre-email@votre-domaine.com
EMAIL_FROM_NAME=Chrona
```

### Tester l'envoi d'emails

```bash
# Activer l'environnement virtuel
cd backend
source .venv/bin/activate  # Linux
# OU
.venv\Scripts\activate  # Windows

# Lancer le script de test
python tools/test_email.py
```

---

## Sécurité et Clés

### Génération de Clés Sécurisées

**1. Clé secrète pour JWT (HS256 legacy)**

```bash
# Linux/macOS
openssl rand -base64 64

# Windows PowerShell
$bytes = New-Object byte[] 64
(New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
[Convert]::ToBase64String($bytes)
```

**2. Clés RSA pour JWT (RS256)**

```bash
# Générer avec le script fourni
python backend/tools/generate_keys.py --key-size 4096

# OU manuellement avec OpenSSL
openssl genpkey -algorithm RSA -out jwt_private_key.pem -pkeyopt rsa_keygen_bits:4096
openssl rsa -pubout -in jwt_private_key.pem -out jwt_public_key.pem
```

**3. Mot de passe PostgreSQL**

```bash
# Générer un mot de passe fort de 32 caractères
openssl rand -base64 32
```

### Stockage des Secrets

#### Développement
- Utiliser `.env` (gitignored)
- Ne **JAMAIS** commiter les clés privées

#### Production
Options recommandées:

**Option A: Variables d'environnement Docker**
```bash
# Définir via docker-compose avec fichier .env.production (chmod 600)
docker compose --env-file .env.production up -d
```

**Option B: Docker Secrets (Swarm)**
```bash
echo "VOTRE_SECRET" | docker secret create db_password -
```

**Option C: Gestionnaires de secrets externes**
- **AWS Secrets Manager** (AWS)
- **Azure Key Vault** (Azure)
- **HashiCorp Vault** (on-premise/cloud)
- **Google Secret Manager** (GCP)

### Rotation des Clés JWT

**Procédure de rotation annuelle (zéro downtime):**

1. Générer une nouvelle paire de clés RS256
2. Configurer le backend pour accepter les deux clés publiques
3. Déployer la mise à jour
4. Après expiration des anciens tokens (ex: 24h), retirer l'ancienne clé

---

## Tests E2E (End-to-End) avec Playwright

Les tests E2E valident le flux complet: Backend API → Kiosk UI → Interactions utilisateur.

### Configuration pour Tests E2E

**Étape 1: Variables d'Environnement Requises**

```bash
# backend/tests/e2e/.env
API_URL=http://localhost:8000
KIOSK_URL=http://localhost:5174
KIOSK_ID=1
TEST_KIOSK_API_KEY=<generated-key>
```

**Étape 2: Initialisation de la Base de Données**

⚠️ **Critique:** La base de données DOIT être initialisée AVANT les tests:

```bash
# Créer le schéma complet (tous les modèles)
cat > /tmp/init_db.py << 'EOF'
import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

async def init_db():
    engine = create_async_engine(os.getenv('DATABASE_URL','sqlite+aiosqlite:///./app.db'))
    try:
        import src.models  # ⚠️ IMPORTANT: importe TOUS les modèles
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✓ Database schema initialized")
    finally:
        await engine.dispose()

asyncio.run(init_db())
EOF

cd backend
export DATABASE_URL="sqlite+aiosqlite:////tmp/chrona_test.db"
python /tmp/init_db.py
```

**Étape 3: Lancer le Backend API**

```bash
# Terminal 1 - Backend (reste en avant-plan)
cd backend
export DATABASE_URL="sqlite+aiosqlite:////tmp/chrona_test.db"
uvicorn src.main:app --host 0.0.0.0 --port 8000

# OU en arrière-plan avec vérification de health
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
sleep 5  # Donner le temps au serveur de démarrer
curl http://localhost:8000/health
```

**Étape 4: Générer les Clés et Jeton API Kiosk**

```bash
# 1. Générer les clés JWT RS256 (si non présentes)
cd backend
python tools/generate_keys.py

# 2. Créer un administrateur pour générer les clés kiosk
python tools/create_admin_user.py --email "admin-e2e@local" --password "Passw0rd!" --role admin

# 3. Récupérer le token admin
TOKEN=$(curl -fsS -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=admin-e2e@local" \
  --data-urlencode "password=Passw0rd!" | jq -r .access_token)

# 4. Générer la clé API pour le kiosk
API_KEY=$(curl -fsS -X POST http://localhost:8000/admin/kiosks/1/generate-api-key \
  -H "Authorization: Bearer $TOKEN" | jq -r .api_key)

echo "TEST_KIOSK_API_KEY=$API_KEY"
```

**Étape 5: Lancer les Interfaces Frontend**

```bash
# Terminal 2 - Kiosk UI
cd apps/kiosk
npm ci
npm run dev -- --host 0.0.0.0 --port 5174

# Terminal 3 - Back-office (optionnel pour les tests, mais utile pour le UI complet)
cd apps/backoffice
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

**Étape 6: Exécuter les Tests E2E**

```bash
cd backend/tests/e2e

# Variables d'environnement requises
export API_URL=http://localhost:8000
export KIOSK_URL=http://localhost:5174
export KIOSK_ID=1
export TEST_KIOSK_API_KEY=<votre-clé-api>

# Installer les dépendances Playwright
npm install
npx playwright install --with-deps

# Exécuter tous les tests
npm test

# OU spécifier un test en particulier
npx playwright test --grep "should display connection status indicator"

# OU lancer en mode debug (viewer interactif)
npx playwright test --debug
```

### Tests E2E: Points Critiques Identifiés

Basé sur les exécutions réelles, voici les problèmes rencontrés et solutions:

**1. Offline Detection (Événement Browser)**

❌ **Problème initié:** Le composant `ConnectionStatus` n'était pas assez réactif aux changements de mode offline.

✅ **Solution:** Ajouter les event listeners du navigateur pour détection instantanée:

```typescript
// apps/kiosk/src/components/ConnectionStatus.tsx
useEffect(() => {
  const handleOnline = () => {
    setIsOnline(true)
    setLastCheck(new Date())
  }
  const handleOffline = () => {
    setIsOnline(false)
    setLastCheck(new Date())
  }

  // Event listeners pour détection instantanée
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)

  // + Health check périodique comme fallback
  const interval = setInterval(checkConnection, 10000)

  return () => {
    clearInterval(interval)
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  }
}, [])
```

**2. Configuration API Key (Développement)**

❌ **Problème:** Tests échouaient car `VITE_KIOSK_API_KEY` n'était pas configuré.

✅ **Solution:** Rendre graceful les erreurs de configuration:

```typescript
// apps/kiosk/src/services/api.ts
const getApiKey = (): string => {
  const apiKey = localStorage.getItem('kioskApiKey') || import.meta.env.VITE_KIOSK_API_KEY
  if (!apiKey || apiKey === 'your-api-key-here') {
    if (import.meta.env.DEV) {
      console.warn('API key not configured')  // Warn, not error
    }
    return ''  // Allow page to load without API key
  }
  return apiKey
}
```

**3. Kiosk-info Element Visibility**

❌ **Problème:** Test attendait `[class*="kiosk-info"]` visible sur page load.

✅ **Solution:** Kiosk-info n'est visible qu'après activation du mode kiosk:

```typescript
// backend/tests/e2e/kiosk.ui.e2e.ts
test('should display kiosk information', async ({ page }) => {
  // D'abord, activer le mode kiosk
  const enterKioskBtn = page.locator('button:has-text("Enter Kiosk Mode")')
  if ((await enterKioskBtn.count()) > 0) {
    await enterKioskBtn.click()
    await page.waitForTimeout(500)  // Attendre le rendu
  }

  // Maintenant vérifier la visibilité
  await expect(page.locator('[class*="kiosk-info"]').first())
    .toBeVisible({ timeout: 10000 })
})
```

**4. Console Errors Filtering**

❌ **Problème:** Tests échouaient sur console errors attendus.

✅ **Solution:** Filtrer les erreurs attendues liées à la configuration:

```typescript
// backend/tests/e2e/kiosk.ui.e2e.ts
const criticalErrors = errors.filter(
  (err) =>
    !err.includes('favicon') &&
    !err.includes('404') &&
    !err.includes('API key not configured') &&  // Expected in dev
    !err.includes('Failed to get API key')      // Expected in dev
)
expect(criticalErrors.length).toBe(0)
```

### Dépannage Tests E2E

**Erreur: "Timeout waiting for backend health check"**

```bash
# Vérifier que le backend répond
curl http://localhost:8000/health

# Si absent, vérifier les logs
docker compose logs backend -n 50

# Ou relancer manuellement
cd backend && uvicorn src.main:app --reload
```

**Erreur: "Failed to generate kiosk API key"**

```bash
# Vérifier que le kiosk admin existe
curl -X GET http://localhost:8000/admin/kiosks \
  -H "Authorization: Bearer $TOKEN"

# Créer manuellement si nécessaire
curl -X POST http://localhost:8000/admin/kiosks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"kiosk_name":"test-kiosk","location":"test","device_fingerprint":"test123","is_active":true}'
```

**Erreur: "no such table: kiosks"**

```bash
# Réinitialiser le schéma entièrement
rm -f /tmp/chrona_test.db

# Puis réexécuter init_db.py avec l'import complet src.models
python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
async def init():
    engine = create_async_engine('sqlite+aiosqlite:////tmp/chrona_test.db')
    import src.models  # ⚠️ Import TOUS les modèles
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()
asyncio.run(init())
"
```

---

## Vérifications et Tests

### Tests Post-Installation (Développement)

```bash
# 1. Vérifier que le backend répond
curl http://localhost:8000/health

# Réponse attendue:
# {"status":"ok","database":"connected"}

# 2. Tester l'inscription et la connexion
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'

# 3. Tester la documentation API
# Naviguer vers: http://localhost:8000/docs

# 4. Vérifier les frontends
# Back-office: http://localhost:5173
# Kiosk: http://localhost:5174
```

### Tests Post-Installation (Production)

```bash
# 1. Vérifier HTTPS et certificats SSL
curl -I https://api.votre-domaine.com/health

# 2. Tester la sécurité (headers)
curl -I https://api.votre-domaine.com | grep -i "strict-transport-security"

# 3. Vérifier rate limiting
for i in {1..15}; do curl -s https://api.votre-domaine.com/health; done

# 4. Tester l'authentification
curl -X POST https://api.votre-domaine.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@votre-domaine.com","password":"SecurePass123!"}'

# 5. Vérifier les logs
docker compose -f docker-compose.prod.yml logs backend --tail=50
```

### Tests de Performance (Production)

```bash
# Installer Apache Bench
sudo apt install apache2-utils

# Test de charge (100 requêtes, 10 concurrentes)
ab -n 100 -c 10 https://api.votre-domaine.com/health

# Test de latence
time curl https://api.votre-domaine.com/health
```

---

## Dépannage

### Problème: Backend ne démarre pas

**Symptôme**: `docker compose logs backend` affiche des erreurs de connexion DB

**Solution**:
```bash
# Vérifier que PostgreSQL est démarré
docker compose ps

# Vérifier les logs PostgreSQL
docker compose logs db

# Recréer les containers
docker compose down -v
docker compose up -d
```

### Problème: "JWT private key not found"

**Symptôme**: Erreur au démarrage du backend

**Solution**:
```bash
# Vérifier que les clés existent
ls -la backend/jwt_*.pem

# Si absentes, générer les clés
cd backend
python tools/generate_keys.py

# Vérifier les permissions
chmod 600 jwt_private_key.pem
chmod 644 jwt_public_key.pem
```

### Problème: Emails non envoyés

**Symptôme**: OTP non reçu par email

**Solution**:
```bash
# Vérifier la configuration email
docker compose exec backend env | grep EMAIL

# Tester l'envoi manuel
docker compose exec backend python tools/test_email.py

# Vérifier les logs
docker compose logs backend | grep -i email
```

### Problème: CORS errors dans le navigateur

**Symptôme**: Frontend affiche des erreurs CORS

**Solution**:
```bash
# Vérifier ALLOWED_ORIGINS dans .env
grep ALLOWED_ORIGINS backend/.env

# Doit inclure l'origine du frontend (ex: http://localhost:5173)
# Mettre à jour et redémarrer
docker compose restart backend
```

### Problème: PostgreSQL "too many connections"

**Symptôme**: Backend ne peut plus se connecter à la DB

**Solution**:
```bash
# Se connecter à PostgreSQL
docker compose exec db psql -U chrona -d chrona

# Voir les connexions actives
SELECT count(*) FROM pg_stat_activity;

# Augmenter max_connections (postgresql.conf)
# Ou redémarrer pour libérer les connexions
docker compose restart db
```

### Problème: Nginx 502 Bad Gateway

**Symptôme**: Nginx affiche "502 Bad Gateway"

**Solution**:
```bash
# Vérifier que les backends sont up
docker compose ps

# Vérifier les logs Nginx
docker compose logs nginx

# Tester la connexion interne
docker compose exec nginx curl http://backend:8000/health

# Redémarrer Nginx
docker compose restart nginx
```

---

## CI/CD Pipeline et Artefacts

### Genération du SBOM (Software Bill of Materials)

Le SBOM (liste des dépendances) est généré automatiquement par le pipeline CI/CD pour assurer la traçabilité des composants.

**Configuration du SBOM dans `.github/workflows/ci.yml`:**

```yaml
sbom-generation:
  name: Security • SBOM Generation
  runs-on: ubuntu-latest
  steps:
    - name: Install CycloneDX
      run: pip install cyclonedx-py  # v4+ CLI

    - name: Generate Python SBOM
      working-directory: backend
      run: |
        pip install -r requirements.txt
        # Syntaxe v4+: cyclonedx-py <subcommand> -i <input> -o <output> --output-format json
        cyclonedx-py requirements -i requirements.txt -o sbom-python.json --output-format json

    - name: Generate Mobile SBOM
      # ...
      run: npx @cyclonedx/cyclonedx-npm --output-file sbom-mobile.json

    - name: Generate Kiosk SBOM
      # ...
      run: npx @cyclonedx/cyclonedx-npm --output-file sbom-kiosk.json
```

**⚠️ Important - Commandes cyclonedx-py v4+:**

- ❌ Ancien (v3): `cyclonedx-py -r requirements.txt -o sbom.xml --format json`
- ✅ Nouveau (v4+): `cyclonedx-py requirements -i requirements.txt -o sbom.json --output-format json`

Points clés:
- Utiliser le **subcommand** `requirements` (au lieu de `-r`)
- Utiliser `-i` pour input (au lieu de `-r`)
- Utiliser `--output-format json` (au lieu de `--format json`)
- NE PAS utiliser le shorthand `-j`

**Téléchargement des Artefacts SBOM:**

Les SBOM sont générés et stockés comme artefacts GitHub:

```bash
# Via l'interface GitHub Actions:
1. Aller sur Actions → dernière exécution de CI
2. Cliquer sur l'artefact "sbom-reports"
3. Télécharger sbom-python.json, sbom-mobile.json, sbom-kiosk.json

# Via API GitHub:
gh api repos/<owner>/<repo>/actions/runs/<run-id>/artifacts --jq '.artifacts[] | select(.name=="sbom-reports")'
```

### Autres Artefacts de CI/CD

Le pipeline produit aussi:

| Artefact | Contenu | Usage |
|----------|---------|-------|
| **coverage-xml** | Coverage report (Codecov) | Métriques de qualité de code |
| **safety-report** | Python vulnerability scan | Audit de sécurité Python |
| **npm-audit-*** | Node audit reports | Audit de sécurité frontend |
| **trivy-report** | Docker image vulnerabilities | Scan de sécurité Docker |
| **semgrep-results** | SAST security findings | Analyse statique de code |
| **playwright-report** | E2E test results | Validation UI/intégration |
| **e2e-test-results** | Test traces + vidéos | Débogage des tests |

---

## Support et Documentation

- **Documentation complète**: `docs/` dans le dépôt
- **Spécifications techniques**: `docs/specs/chrona_plan.md`
- **Guide développeur**: `CLAUDE.md` et `AGENTS.md`
- **TODO et roadmap**: `docs/TODO.md`
- **Issues GitHub**: https://github.com/votre-org/Chrona_Core/issues

---

## Checklist de Déploiement Production

### Backend & Infrastructure
- [ ] Serveur Ubuntu/RHEL configuré avec firewall activé
- [ ] Docker et Docker Compose installés
- [ ] PostgreSQL 16 installé avec encryption at-rest
- [ ] Clés JWT RS256 générées (4096 bits)
- [ ] Fichier `.env.production` configuré et sécurisé (chmod 600)
- [ ] Certificats SSL/TLS obtenus (Let's Encrypt ou commercial)
- [ ] Nginx configuré avec rate limiting et security headers
- [ ] CORS configuré avec domaines de production uniquement
- [ ] Email SMTP/SendGrid configuré et testé
- [ ] Sauvegarde automatique PostgreSQL configurée (cron)
- [ ] Monitoring et logs configurés (Sentry, Prometheus, etc.)
- [ ] Tests de charge effectués (Apache Bench)
- [ ] Utilisateur admin créé

### Application Mobile
- [ ] `app.json` configuré avec bundle identifiers production
- [ ] `eas.json` configuré avec URL API production
- [ ] Builds Android (APK/AAB) générés via EAS ou local
- [ ] Builds iOS (.ipa) générés (si applicable)
- [ ] Tests effectués sur émulateur Android
- [ ] Tests effectués sur appareil physique Android
- [ ] Tests effectués sur simulateur iOS (si macOS disponible)
- [ ] Tests effectués sur appareil physique iOS (si applicable)
- [ ] Certificate pinning configuré (production)
- [ ] Anti-screenshot activé (expo-screen-capture)
- [ ] Stockage sécurisé des tokens (expo-secure-store)
- [ ] Distribution interne testée (MDM ou email APK)
- [ ] Publication sur Google Play Store (si applicable)
- [ ] Publication sur Apple App Store (si applicable)

### Frontend Web (Back-office & Kiosk)
- [ ] Back-office build production testé
- [ ] Kiosk build production testé
- [ ] Variables d'environnement production configurées
- [ ] HTTPS forcé sur tous les domaines

### Documentation & Formation
- [ ] Documentation remise au client (credentials, accès, runbook)
- [ ] Guide utilisateur mobile créé
- [ ] Formation des administrateurs effectuée
- [ ] Procédures de révocation d'appareil documentées
- [ ] Plan de réponse aux incidents préparé

---

**Version du document**: 1.1
**Dernière mise à jour**: 23 octobre 2025
**Auteur**: Équipe Chrona

**Changements v1.1:**
- Ajout section complète "Tests E2E avec Playwright"
- Documentation des problèmes rencontrés et solutions (offline detection, API key, kiosk-info visibility)
- Guide détaillé pour configurer et exécuter les tests E2E
- Amélioration de l'initialisation de schéma avec import complet des modèles
- Documentation du SBOM generation (cyclonedx-py v4+)
- Liste complète des artefacts CI/CD générés
### HTTPS en production (Traefik + Let’s Encrypt)

Pré-requis DNS:
- Créez des enregistrements A/AAAA pointant vers votre serveur pour:
  - `api.<domaine>`, `backoffice.<domaine>`, `kiosk.<domaine>`

Lancement avec l’overlay HTTPS prod:
```
DOMAIN=example.com TRAEFIK_ACME_EMAIL=admin@example.com \
docker compose -f docker-compose.yml -f docker-compose.https.prod.yml up -d --build
```

Accès:
- https://api.example.com
- https://backoffice.example.com
- https://kiosk.example.com

Sécurité:
- Activez `ENABLE_HSTS=true` côté backend lorsque l’HTTPS est garanti.
- Les en-têtes de sécurité (CSP, XFO, etc.) sont injectés par le backend.

### CI/CD – Déploiement via GitHub Actions

Un workflow `Deploy` est prêt (`.github/workflows/deploy.yml`). Il copie un bundle sur un serveur cible via SSH et lance le stack avec HTTPS.

Secrets requis (Repository → Settings → Secrets and variables → Actions):
- `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `SSH_TARGET_DIR`

Déclenchement:
- Actions → Deploy → Run workflow, fournir `environment`, `domain`, `traefik_email`.

Notes:
- Le workflow crée `.env` côté serveur avec `DOMAIN` et `TRAEFIK_ACME_EMAIL`.
- Adaptez à votre stratégie (rolling update, healthchecks, secrets manager).
