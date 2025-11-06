# Guide de Déploiement - AWS EC2

Ce guide explique comment déployer Chrona sur votre instance EC2.

## 📋 Prérequis

- Instance EC2 Ubuntu 22.04 LTS avec au moins 2GB RAM
- Fichier `.pem` pour la connexion SSH
- Secrets GitHub configurés
- Accès à GitHub (pour les Actions)

## 🔐 Configuration des Secrets GitHub

Les secrets suivants doivent être configurés dans **Settings → Secrets and variables → Actions** :

| Secret | Valeur | Exemple |
|--------|--------|---------|
| `EC2_HOST` | Adresse IP publique de l'instance | `13.37.245.222` |
| `EC2_USER` | Utilisateur SSH | `ubuntu` |
| `EC2_SSH_KEY` | Contenu du fichier `.pem` | `-----BEGIN RSA...` |
| `DATABASE_URL` | URL PostgreSQL | `postgresql+asyncpg://user:pass@db:5432/chrona` |
| `SECRET_KEY` | Clé secrète JWT (32 caractères min) | Généré via `openssl rand -hex 32` |
| `ADMIN_EMAIL` | Email admin (optionnel) | `admin@yourcompany.com` |
| `ADMIN_PASSWORD` | Password admin (optionnel) | Un mot de passe fort |

### Comment configurer les secrets rapidement :

**Windows (PowerShell):**
```powershell
# Assurez-vous que vous avez gh CLI installé
$PemContent = Get-Content "C:\path\to\key.pem" -Raw

# Définir les secrets
"13.37.245.222" | gh secret set EC2_HOST --repo your-org/Chrona_Core
"ubuntu" | gh secret set EC2_USER --repo your-org/Chrona_Core
$PemContent | gh secret set EC2_SSH_KEY --repo your-org/Chrona_Core
"postgresql+asyncpg://user:pass@db:5432/chrona" | gh secret set DATABASE_URL --repo your-org/Chrona_Core
"<random-secret-key>" | gh secret set SECRET_KEY --repo your-org/Chrona_Core
```

**Linux/macOS:**
```bash
cat ~/.ssh/key.pem | gh secret set EC2_SSH_KEY --repo your-org/Chrona_Core
echo "13.37.245.222" | gh secret set EC2_HOST --repo your-org/Chrona_Core
echo "ubuntu" | gh secret set EC2_USER --repo your-org/Chrona_Core
echo "postgresql+asyncpg://user:pass@db:5432/chrona" | gh secret set DATABASE_URL --repo your-org/Chrona_Core
echo "$(openssl rand -hex 32)" | gh secret set SECRET_KEY --repo your-org/Chrona_Core
```

## 🚀 Déployer l'application

### Via GitHub Actions (Recommandé)

1. Allez sur : https://github.com/your-org/Chrona_Core/actions
2. Cliquez sur **Deploy** workflow
3. Cliquez sur **Run workflow**
4. Remplissez les paramètres :
   - **Environment**: `prod` ou `staging`
   - **EC2 Host**: `13.37.245.222` (votre IP)
   - **Backend API port**: `8000` (par défaut)
   - **Backoffice port**: `5173` (par défaut)
5. Cliquez sur **Run workflow**

Le déploiement prendra environ 3-5 minutes et effectuera automatiquement :
- ✅ Construction et démarrage des services Docker
- ✅ Vérification de la connexion à la base de données
- ✅ **Exécution des migrations Alembic vers la dernière version (head)**
- ✅ **Création de l'utilisateur admin** (email: `admin@chrona.local` / password: `ChangeMe123!` par défaut)
- ✅ Vérification de l'état des services

**🔒 Sécurité : Credentials admin**

Par défaut, l'admin créé a :
- Email: `admin@chrona.local`
- Password: `ChangeMe123!`

**IMPORTANT:** Pour la production, configurez `ADMIN_EMAIL` et `ADMIN_PASSWORD` dans les GitHub Secrets :
```bash
echo "admin@yourcompany.com" | gh secret set ADMIN_EMAIL --repo your-org/Chrona_Core
echo "YourSecureP@ssw0rd!" | gh secret set ADMIN_PASSWORD --repo your-org/Chrona_Core
```

### Vérifier le déploiement

Après le workflow:

```bash
# SSH dans l'instance
ssh -i ~/key.pem ubuntu@13.37.245.222

# Aller dans le répertoire de déploiement
cd /opt/chrona

# Vérifier les services
docker-compose ps

# Vérifier que l'admin a été créé
docker-compose exec db psql -U chrona -d chrona -c "SELECT email, role FROM users WHERE role='admin';"

# Voir les logs du backend
docker-compose logs -f backend

# Tester le backend
curl http://localhost:8000/docs
```

**Se connecter au backoffice:**
1. Allez sur : http://13.37.245.222:5173
2. Utilisez les credentials admin (voir les logs du déploiement ou les valeurs par défaut)

## 📍 Accéder à l'application

Une fois déployée:

- **Backend (API)**: http://13.37.245.222:8000
  - Swagger UI: http://13.37.245.222:8000/docs
  - OpenAPI JSON: http://13.37.245.222:8000/openapi.json

- **Backoffice**: http://13.37.245.222:5173

## 🔧 Déploiement Manuel (sans GitHub Actions)

Si vous préférez déployer manuellement :

```bash
# 1. Connexion SSH
ssh -i ~/key.pem ubuntu@13.37.245.222

# 2. Créer répertoire de déploiement
mkdir -p /opt/chrona
cd /opt/chrona

# 3. Cloner ou télécharger les sources
git clone https://github.com/your-org/Chrona_Core.git .

# 4. Créer le fichier .env
cat > .env <<'EOF'
EC2_HOST=13.37.245.222
EC2_PORT=8000
BACKOFFICE_PORT=5173
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/chrona
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=http://13.37.245.222:5173,http://13.37.245.222:8000
VITE_API_URL=http://13.37.245.222:8000
ALLOW_CREDENTIALS=false
ALLOWED_METHODS=*
ALLOWED_HEADERS=*
ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_PRIVATE_KEY_PATH=/app/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/app/jwt_public_key.pem
POSTGRES_DB=chrona
POSTGRES_USER=chrona
POSTGRES_PASSWORD=chrona
EOF

# 5. Installer Docker si absent
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# 6. Démarrer les services
docker-compose up -d --build

# 7. Vérifier le statut
docker-compose ps
```

## 📊 Monitorer le déploiement

**Voir les logs en temps réel:**
```bash
docker-compose logs -f backend    # Backend
docker-compose logs -f backoffice # Backoffice
docker-compose logs -f db         # Base de données
```

**Redémarrer un service:**
```bash
docker-compose restart backend
docker-compose restart backoffice
```

**Arrêter tous les services:**
```bash
docker-compose down
```

## 🐛 Dépannage

### Erreur: "docker-compose not found"
```bash
sudo apt-get update
sudo apt-get install -y docker-compose
```

### Erreur: "Permission denied while trying to connect to Docker daemon"
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Backend ne démarre pas
```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier le fichier .env
cat .env

# Vérifier le port 8000 est libre
sudo lsof -i :8000
```

### Backoffice ne peut pas se connecter au backend
- Vérifier que `VITE_API_URL` dans `.env` pointe vers la bonne adresse
- Vérifier que le backend est bien démarré: `docker-compose ps`
- Vérifier les CORS: `ALLOWED_ORIGINS` doit inclure l'URL du backoffice

## 🔄 Mise à jour de l'application

Pour mettre à jour après un changement de code:

```bash
cd /opt/chrona

# Tirer les dernières modifications
git pull origin main

# Relancer les services
docker-compose up -d --build
```

Ou simplement relancer le workflow GitHub Actions.

## 📝 Variables d'environnement

Voir `.env.example` pour la documentation complète de chaque variable.

Les variables principales:
- **EC2_HOST**: Adresse IP ou domaine (ne change pas le comportement, juste documentaire)
- **DATABASE_URL**: Connection string PostgreSQL
- **SECRET_KEY**: Clé secrète pour les tokens JWT
- **ALLOWED_ORIGINS**: CORS - URLs qui peuvent appeler l'API

## 🆘 Support

Pour les erreurs ou questions:
1. Consultez les logs: `docker-compose logs`
2. Vérifiez le fichier `.env`
3. Vérifiez que tous les secrets GitHub sont configurés
4. Consultez `docs/DEPLOYMENT_EC2.md` pour plus de détails

