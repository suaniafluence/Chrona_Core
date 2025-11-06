# Déploiement sur AWS EC2

Ce guide explique comment déployer l'application Chrona (Backend + Backoffice) sur une instance Ubuntu EC2 AWS.

## Prérequis

1. **Instance EC2 Amazon Linux 2 ou Ubuntu 22.04 LTS** avec :
   - Au moins 2GB de RAM
   - 20GB d'espace disque
   - Ports 8000 (backend) et 5173 (backoffice) ouverts dans le Security Group
   - SSH accessible via port 22

2. **Fichier de clé SSH** (.pem) pour se connecter à l'instance

3. **GitHub Secrets** configurés dans votre repository

## Configuration des GitHub Secrets

Allez dans **Settings → Secrets and variables → Actions** et ajoutez :

### Secrets requis

| Secret | Description | Exemple |
|--------|-------------|---------|
| `EC2_HOST` | Adresse IP publique de l'instance EC2 | `13.37.245.222` |
| `EC2_USER` | Utilisateur SSH (ubuntu pour Ubuntu, ec2-user pour Amazon Linux) | `ubuntu` |
| `EC2_SSH_KEY` | Contenu du fichier `.pem` (voir section ci-dessous) | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DATABASE_URL` | URL de connexion PostgreSQL (optionnel, voir ci-dessous) | `postgresql+asyncpg://chrona:chrona@db:5432/chrona` |
| `SECRET_KEY` | Clé secrète pour JWT (doit être aléatoire et sécurisé) | `openssl rand -hex 32` |
| `ADMIN_EMAIL` | 🔐 Email du compte admin (optionnel, défaut: admin@chrona.local) | `admin@yourcompany.com` |
| `ADMIN_PASSWORD` | 🔐 Mot de passe du compte admin (optionnel, défaut: ChangeMe123!) | Un mot de passe fort |

### 🗄️ Configuration de la base de données (DATABASE_URL)

**Par défaut :** Si vous ne configurez PAS ce secret, le système utilise automatiquement la base PostgreSQL locale définie dans `docker-compose.yml` :

```
postgresql+asyncpg://chrona:chrona@db:5432/chrona
```

**⚠️ Vous devez SEULEMENT configurer ce secret si :**
- Vous utilisez AWS RDS
- Vous utilisez une base de données PostgreSQL externe
- Vous voulez modifier les credentials par défaut

**Format requis :**
```
postgresql+asyncpg://username:password@hostname:port/database_name
```

**Exemples selon votre configuration :**

1. **Base de données locale sur EC2** (par défaut, RIEN À FAIRE) :
   ```bash
   # Ne configurez PAS ce secret, la valeur par défaut fonctionne
   # Valeur automatique : postgresql+asyncpg://chrona:chrona@db:5432/chrona
   ```
   Note : `db` est le nom du service dans docker-compose.yml

2. **Base de données AWS RDS** (production) :
   ```bash
   echo "postgresql+asyncpg://admin:MySecurePass123@chrona-db.c9akrzq9zqxb.eu-west-1.rds.amazonaws.com:5432/chrona" | \
     gh secret set DATABASE_URL --repo your-org/Chrona_Core
   ```

3. **Base de données externe** (autre serveur PostgreSQL) :
   ```bash
   echo "postgresql+asyncpg://chrona_user:password@192.168.1.50:5432/chrona" | \
     gh secret set DATABASE_URL --repo your-org/Chrona_Core
   ```

**✅ Points importants :**
- **Utilisez toujours le driver `asyncpg`** : `postgresql+asyncpg://...`
- **Pour la base locale** : utilisez le nom du service `db` comme hostname
- **Pour AWS RDS/externe** : utilisez le hostname complet (endpoint AWS ou IP)
- Vérifiez que l'utilisateur PostgreSQL a les droits pour créer/modifier des tables
- Pour AWS RDS : assurez-vous que le Security Group autorise les connexions depuis votre EC2

### 🔐 Configuration des credentials admin (Optionnel mais RECOMMANDÉ)

Le workflow crée automatiquement un utilisateur admin lors du déploiement. Vous pouvez personnaliser les credentials :

**Secrets optionnels pour l'admin :**
- `ADMIN_EMAIL` : Email du compte administrateur (défaut: `admin@chrona.local`)
- `ADMIN_PASSWORD` : Mot de passe du compte admin (défaut: `ChangeMe123!`)

**⚠️ Si vous ne configurez pas ces secrets :**
Le système utilisera les credentials par défaut :
- Email: `admin@chrona.local`
- Password: `ChangeMe123!`

**🔒 IMPORTANT pour la sécurité :**
1. **Configurez toujours** `ADMIN_EMAIL` et `ADMIN_PASSWORD` dans les secrets GitHub pour la production
2. Si vous utilisez les credentials par défaut, **changez-les immédiatement** après le premier déploiement
3. Utilisez un mot de passe fort (12+ caractères, majuscules, minuscules, chiffres, symboles)

**Configuration via GitHub CLI :**
```bash
# Configurer les credentials admin personnalisés
echo "admin@yourcompany.com" | gh secret set ADMIN_EMAIL --repo your-org/Chrona_Core
echo "YourSecureP@ssw0rd!" | gh secret set ADMIN_PASSWORD --repo your-org/Chrona_Core
```

### Ajouter la clé SSH en secret

1. Lisez le contenu de votre fichier `.pem` :
   ```bash
   cat /path/to/your-key.pem
   ```

2. Copiez tout le contenu (y compris `-----BEGIN RSA PRIVATE KEY-----` et `-----END RSA PRIVATE KEY-----`)

3. Dans GitHub, allez à **Settings → Secrets → New repository secret**

4. Créez un secret nommé `EC2_SSH_KEY` et collez le contenu complet du fichier `.pem`

## Générer des clés secrètes sécurisées

Pour générer une clé `SECRET_KEY` sécurisée, exécutez :

```bash
# Sur Windows (PowerShell)
-join ((1..32) | ForEach-Object { [char](Get-Random -InputObject (48..122)) }) | Set-Clipboard

# Sur macOS/Linux
openssl rand -hex 32
```

## Déployer l'application

### Via l'interface GitHub

1. Allez à **Actions → Deploy** (workflow)
2. Cliquez sur **Run workflow**
3. Choisissez :
   - **Environment** : `prod` (ou `staging`)
   - **EC2 Host** : `13.37.245.222` (votre adresse IP ou domaine EC2)
   - **Backend API port** : `8000` (optionnel, défaut: 8000)
   - **Backoffice port** : `5173` (optionnel, défaut: 5173)
4. Cliquez sur **Run workflow**

La configuration est appliquée automatiquement à partir des variables d'environnement.

### Manuellement via SSH

Si vous préférez déployer manuellement :

```bash
# Connexion à l'instance
ssh -i /path/to/your-key.pem ubuntu@13.37.245.222

# Sur l'instance EC2
cd /opt/chrona

# Créer le fichier .env avec votre configuration
cat > .env <<EOF
EC2_HOST=13.37.245.222
EC2_PORT=8000
BACKOFFICE_PORT=5173
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/chrona
SECRET_KEY=your-secure-random-key
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

# Démarrer les services avec docker-compose.yml standard
docker compose up -d --build
```

## Vérifier le déploiement

Une fois le workflow terminé, vérifiez que tout fonctionne :

```bash
# SSH dans l'instance
ssh -i /path/to/your-key.pem ubuntu@13.37.245.222

# Aller dans le répertoire de déploiement
cd /opt/chrona

# Vérifier l'état des services
docker compose ps

# Vérifier les migrations Alembic (IMPORTANT!)
docker compose exec backend alembic current

# Voir les logs
docker compose logs -f backend
docker compose logs -f backoffice

# Tester le backend
curl http://localhost:8000/docs

# Tester le backoffice
curl http://localhost:5173
```

### Vérifier la création de l'utilisateur admin

Le workflow crée automatiquement un utilisateur admin après les migrations. Pour vérifier :

```bash
cd /opt/chrona

# Se connecter à la base de données et vérifier les utilisateurs
docker compose exec db psql -U chrona -d chrona -c "SELECT id, email, role FROM users;"

# Ou via le backend
docker compose exec backend python -c "
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import os

async def check_admin():
    from src.models.user import User
    db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./app.db')
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.role == 'admin'))
        admins = result.scalars().all()
        for admin in admins:
            print(f'Admin: {admin.email} (ID: {admin.id})')

asyncio.run(check_admin())
"
```

**Se connecter au backoffice avec l'admin :**
1. Allez sur : http://13.37.245.222:5173
2. Connectez-vous avec les credentials :
   - Email: `admin@chrona.local` (ou votre email personnalisé)
   - Password: `ChangeMe123!` (ou votre mot de passe personnalisé)

**Créer manuellement un admin si nécessaire :**
```bash
cd /opt/chrona

docker compose exec backend python tools/create_admin_user.py \
  --email "admin@example.com" \
  --password "Passw0rd!" \
  --role admin
```

### Vérifier les migrations de base de données

Le workflow exécute automatiquement `alembic upgrade head` après le démarrage des services. Pour vérifier manuellement :

```bash
cd /opt/chrona

# Vérifier la version actuelle de la migration
docker compose exec backend alembic current

# Voir l'historique des migrations
docker compose exec backend alembic history

# Lancer les migrations manuellement si nécessaire
docker compose exec backend alembic upgrade head
```

### Script de déploiement automatique

Un script helper est disponible dans `scripts/deploy-ec2.sh` :

```bash
cd /opt/chrona

# Vérifier l'environnement et la connexion DB
./scripts/deploy-ec2.sh check

# Vérifier le statut des migrations
./scripts/deploy-ec2.sh status

# Lancer uniquement les migrations
./scripts/deploy-ec2.sh migrate

# Déploiement complet (restart + migrations)
./scripts/deploy-ec2.sh deploy
```

## Accéder à l'application

- **Backend (API)** : `http://13.37.245.222:8000`
  - Swagger UI : `http://13.37.245.222:8000/docs`
  - API JSON Schema : `http://13.37.245.222:8000/openapi.json`
- **Backoffice** : `http://13.37.245.222:5173`

## Dépannage

### Docker non installé

Le workflow installe automatiquement Docker si absent. Pour installer manuellement :

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### Permission refusée lors du déploiement

Assurez-vous que :
1. Le répertoire `/opt/chrona` a les bonnes permissions
2. L'utilisateur SSH est dans le groupe `docker` : `docker ps` doit fonctionner

### Services ne démarrent pas

Consultez les logs :
```bash
docker compose -f /opt/chrona/docker-compose.prod.yml logs
```

Assurez-vous que les ports 8000 et 5173 ne sont pas utilisés :
```bash
sudo lsof -i :8000
sudo lsof -i :5173
```

### Erreur de connexion à la base de données

Vérifiez que `DATABASE_URL` est correct et accessible :

```bash
# 1. Vérifier que DATABASE_URL est bien configuré dans le backend
docker compose exec backend env | grep DATABASE_URL

# 2. Tester la connexion depuis le backend container
docker compose exec backend python3 -c "
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
import os

async def test_db():
    url = os.getenv('DATABASE_URL')
    print(f'Testing connection to: {url}')
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        print('✓ Connection successful!')
    await engine.dispose()

asyncio.run(test_db())
"

# 3. Si PostgreSQL tourne dans docker-compose, vérifier son statut
docker compose exec db pg_isready -U chrona

# 4. Test de connexion avec psql (si installé)
# Pour base locale :
docker compose exec db psql -U chrona -d chrona -c "SELECT version();"

# Pour base externe :
psql "postgresql://user:pass@db-host:5432/chrona" -c "SELECT version();"
```

**Erreurs courantes :**

- **"could not translate host name"** → Hostname incorrect dans DATABASE_URL
- **"password authentication failed"** → Mauvais username/password
- **"database does not exist"** → La base de données n'a pas été créée
- **"connection refused"** → PostgreSQL n'est pas démarré ou port incorrect
- **"no route to host"** → Problème réseau/firewall

**Solutions :**
```bash
# Si vous utilisez la base locale (docker-compose) :
DATABASE_URL=postgresql+asyncpg://chrona:chrona@db:5432/chrona

# Vérifier que le service db est démarré
docker compose ps db

# Redémarrer PostgreSQL si nécessaire
docker compose restart db
```

### Erreur lors des migrations Alembic

Si `alembic upgrade head` échoue :

```bash
cd /opt/chrona

# 1. Vérifier la version actuelle
docker compose exec backend alembic current

# 2. Vérifier l'historique des migrations
docker compose exec backend alembic history --verbose

# 3. Vérifier les logs du backend
docker compose logs backend | grep -i alembic

# 4. Tester la connexion DB depuis Alembic
docker compose exec backend alembic upgrade head --sql > migration.sql
cat migration.sql  # Voir le SQL qui serait exécuté

# 5. Si les migrations sont corrompues, réinitialiser (ATTENTION: perte de données!)
# Option 1 : Stamp to head (marquer comme à jour sans exécuter)
docker compose exec backend alembic stamp head

# Option 2 : Réinitialisation complète (DESTRUCTIF!)
docker compose exec db psql -U chrona -d chrona -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec backend alembic upgrade head
```

**Migrations partielles :**
```bash
# Voir quelle migration a échoué
docker compose logs backend | tail -50

# Revenir à une migration spécifique
docker compose exec backend alembic downgrade <revision_id>

# Puis réessayer
docker compose exec backend alembic upgrade head
```

## Mise à jour de l'application

Pour redéployer après des changements :

1. Poussez vos modifications sur `main` (ou votre branche)
2. Allez à **Actions → Deploy** et lancez le workflow
3. Spécifiez à nouveau votre **EC2 Host** (13.37.245.222) et ports
4. Les services vont redémarrer automatiquement avec les nouveaux code/configuration

## Production Checklist

Avant de déployer en production :

- [ ] Database est configurée sur un serveur RDS ou externe (pas en local)
- [ ] `SECRET_KEY` est une clé aléatoire de 32 caractères minimum
- [ ] `ALLOWED_ORIGINS` inclut tous vos domaines
- [ ] Les ports 8000 et 5173 sont ouverts dans le Security Group
- [ ] SSH est limité à des adresses IP connues (si possible)
- [ ] Les sauvegardes de base de données sont configurées
- [ ] Un nom de domaine est associé et un certificat SSL est prévu

## Arrêter les services

```bash
ssh -i /path/to/your-key.pem ubuntu@54.123.456.789
docker compose -f /opt/chrona/docker-compose.prod.yml down
```

## Support

Consultez les logs GitHub Actions pour plus de détails sur les erreurs :
- Allez à **Actions → Deploy** → Cliquez sur la dernière exécution
- Consultez l'onglet **Deploy to EC2** pour voir les détails

