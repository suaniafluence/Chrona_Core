# Guide de Déploiement Chrona

Ce guide décrit les étapes complètes pour installer et configurer Chrona en environnement de **développement/test** et en **production**.

---

## Table des Matières

1. [Prérequis Système](#prérequis-système)
2. [Architecture Réseau](#architecture-réseau)
3. [Installation Développement/Test](#installation-développementtest)
4. [Installation Production](#installation-production)
5. [Configuration Email](#configuration-email)
6. [Sécurité et Clés](#sécurité-et-clés)
7. [Vérifications et Tests](#vérifications-et-tests)
8. [Dépannage](#dépannage)

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
│  ┌──────────────┐  ┌─────────────────────┐ │
│  │  Backend     │  │  PostgreSQL/SQLite  │ │
│  │  :8000       │──│  :5432              │ │
│  └──────────────┘  └─────────────────────┘ │
│         │                                   │
│  ┌──────┴─────────┬──────────────────────┐ │
│  │  Back-office   │  Kiosk               │ │
│  │  :5173         │  :5174               │ │
│  └────────────────┴──────────────────────┘ │
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

#### Étape 3: Configurer les variables d'environnement

**Backend** - Copier `backend/.env.example` → `backend/.env`:

```bash
# Windows
copy backend\.env.example backend\.env

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

# Sécurité (générer une clé aléatoire sécurisée)
SECRET_KEY=dev-secret-CHANGE-ME-IN-PRODUCTION

# JWT RS256
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
mkcert -cert-file infra/traefik/certs/dev-localhost.pem \
       -key-file infra/traefik/certs/dev-localhost-key.pem \
       localhost 127.0.0.1 ::1 api.localhost backoffice.localhost kiosk.localhost
```

3) Démarrer en HTTPS:
```
DOMAIN=localhost docker compose -f docker-compose.yml -f docker-compose.https.dev.yml up -d
```

4) Accéder en HTTPS:
- Backend: https://api.localhost
- Backoffice: https://backoffice.localhost
- Kiosk: https://kiosk.localhost

#### Étape 5: Initialiser la base de données

```bash
# Appliquer les migrations Alembic
docker compose exec backend alembic upgrade head

# Créer un utilisateur admin
docker compose exec backend python tools/create_test_user.py
```

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
│  ┌──────────────────────────────────────┐ │
│  │  Nginx Reverse Proxy                 │ │
│  │  - SSL/TLS (Let's Encrypt)           │ │
│  │  - Rate limiting                     │ │
│  │  - CORS headers                      │ │
│  └──────────────┬───────────────────────┘ │
│                 │                          │
│  ┌──────────────┴───────────────────────┐ │
│  │  Docker Containers                   │ │
│  │  ┌─────────┬──────────┬────────────┐ │ │
│  │  │ Backend │Backoffice│   Kiosk    │ │ │
│  │  └────┬────┴──────────┴────────────┘ │ │
│  │       │                               │ │
│  │  ┌────▼──────────────────────────┐   │ │
│  │  │  PostgreSQL 16                │   │ │
│  │  │  - Encryption at rest         │   │ │
│  │  │  - WAL archiving              │   │ │
│  │  └───────────────────────────────┘   │ │
│  └──────────────────────────────────────┘ │
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

# Sécurité - GÉNÉRER UNE CLÉ ALÉATOIRE FORTE
# Commande: openssl rand -base64 64
SECRET_KEY=VOTRE-CLE-SECRETE-ALEATOIRE-TRES-LONGUE-64-CARACTERES-MINIMUM

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

# Email - Configuration SMTP Production
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@votre-domaine.com
SMTP_PASSWORD=APP-SPECIFIC-PASSWORD
SMTP_USE_TLS=true
EMAIL_FROM_ADDRESS=noreply@votre-domaine.com
EMAIL_FROM_NAME=Chrona - Pointage

# Logs
LOG_LEVEL=warning

# Sentry (optionnel - monitoring d'erreurs)
# SENTRY_DSN=https://xxx@sentry.io/xxx
```

**⚠️ IMPORTANT:** Protéger ce fichier:
```bash
sudo chmod 600 /opt/chrona/.env.production
sudo chown root:root /opt/chrona/.env.production
```

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
```

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

## Support et Documentation

- **Documentation complète**: `docs/` dans le dépôt
- **Spécifications techniques**: `docs/specs/chrona_plan.md`
- **Guide développeur**: `CLAUDE.md` et `AGENTS.md`
- **TODO et roadmap**: `docs/TODO.md`
- **Issues GitHub**: https://github.com/votre-org/Chrona_Core/issues

---

## Checklist de Déploiement Production

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
- [ ] Documentation remise au client (credentials, accès, runbook)

---

**Version du document**: 1.0
**Dernière mise à jour**: 21 octobre 2025
**Auteur**: Équipe Chrona
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
