# Local Development Setup

Ce guide explique comment exécuter Chrona localement pour le développement.

## 🖥️ Option 1: Docker Compose (Recommandé)

### Prérequis

- Docker Desktop (Windows/macOS) ou Docker Engine (Linux)
- Docker Compose (inclus dans Docker Desktop)
- 4GB RAM minimum
- Ports 8000, 5173, 5432 disponibles

### Démarrage

```bash
# 1. Cloner le repository
git clone https://github.com/your-org/Chrona_Core.git
cd Chrona_Core

# 2. Créer le fichier .env local
cp .env.example .env

# 3. Générer les JWT keys (s'ils n'existent pas)
mkdir -p backend
openssl ecparam -name prime256v1 -genkey -noout -out backend/jwt_private_key.pem
openssl ec -in backend/jwt_private_key.pem -pubout -out backend/jwt_public_key.pem

# 4. Démarrer les services
docker-compose up -d --build

# 5. Attendre que tout démarre (~30 secondes)
sleep 30

# 6. Vérifier le statut
docker-compose ps

# 7. Voir les logs
docker-compose logs -f backend
```

### Accès local

- **Backend API**: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - OpenAPI JSON: http://localhost:8000/openapi.json

- **Backoffice**: http://localhost:5173

- **PostgreSQL**: localhost:5432 (user: chrona, password: chrona)
  - Accès via: `psql postgresql://chrona:chrona@localhost:5432/chrona`

### Arrêt

```bash
docker-compose down
# Ou pour réinitialiser la base de données:
docker-compose down -v
```

### Logs

```bash
# Tous les logs
docker-compose logs

# Backend uniquement
docker-compose logs -f backend

# Backoffice uniquement
docker-compose logs -f backoffice

# Base de données
docker-compose logs -f db

# Traefik
docker-compose logs -f traefik
```

---

## 🐍 Option 2: Backend Local (Python)

Pour développer le backend sans Docker.

### Prérequis

- Python 3.11+
- PostgreSQL local ou service externe
- Node.js 18+ (optionnel pour backoffice)

### Setup Backend

```bash
cd backend

# 1. Créer un environment virtuel
python -m venv .venv

# 2. Activer
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Générer les JWT keys
mkdir -p /app
openssl ecparam -name prime256v1 -genkey -noout -out jwt_private_key.pem
openssl ec -in jwt_private_key.pem -pubout -out jwt_public_key.pem

# 5. Configurer l'environment
cat > .env << 'EOF'
DATABASE_URL=postgresql://chrona:chrona@localhost:5432/chrona
SECRET_KEY=dev-secret-key-12345678901234567890
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000
JWT_PRIVATE_KEY_PATH=./jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=./jwt_public_key.pem
ALLOW_CREDENTIALS=false
ALLOWED_METHODS=*
ALLOWED_HEADERS=*
ACCESS_TOKEN_EXPIRE_MINUTES=60
EOF

# 6. Lancer les migrations (si première exécution)
alembic upgrade head

# 7. Démarrer le serveur
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Tests Backend

```bash
cd backend

# Tous les tests
pytest

# Test spécifique
pytest tests/test_auth.py

# Avec couverture
pytest --cov=src --cov-report=html

# Ouvrir le rapport HTML
# Windows: start htmlcov/index.html
# macOS: open htmlcov/index.html
```

### Linting & Formatage

```bash
cd backend

# Formater avec black
black src tests

# Vérifier
black --check src tests

# Trier les imports
isort .

# Linter
flake8 src tests
```

---

## ⚛️ Option 3: Backoffice Local (Node.js)

Pour développer le backoffice sans Docker.

### Prérequis

- Node.js 18+
- npm ou yarn
- Backend accessible (http://localhost:8000)

### Setup Backoffice

```bash
cd apps/backoffice

# 1. Installer les dépendances
npm ci

# 2. Créer .env local
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:8000
EOF

# 3. Démarrer le dev server
npm run dev
# Accessible à: http://localhost:5173

# 4. Build pour production
npm run build

# 5. Tests
npm test

# 6. Linting
npm run lint
```

---

## 🔄 Flux de Développement Recommandé

### Pour développer le backend

```bash
# Terminal 1: Backend local
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Database Docker uniquement
docker-compose up db

# Terminal 3: Backoffice (optionnel)
cd apps/backoffice
npm run dev
```

### Pour développer le backoffice

```bash
# Terminal 1: Backend local OU Docker
# Option 1: Avec Docker
docker-compose up backend db

# Option 2: Backend local
cd backend && uvicorn src.main:app --reload

# Terminal 2: Backoffice
cd apps/backoffice
npm run dev
```

### Pour développer le système complet

```bash
# Simplement:
docker-compose up
```

---

## 🛠️ Dépannage

### PostgreSQL déjà en utilisation

```bash
# Trouver quel processus utilise le port 5432
# Windows:
netstat -ano | findstr :5432

# macOS/Linux:
lsof -i :5432

# Tuer le processus
kill -9 <PID>
```

### Backend ne se connecte pas à la DB

```bash
# Vérifier la connexion
psql postgresql://chrona:chrona@localhost:5432/chrona

# Si PostgreSQL n'est pas installé localement, utiliser Docker:
docker-compose up db
# Cela démarre juste la base de données
```

### Frontend ne peut pas se connecter au backend

- Vérifier que `VITE_API_URL=http://localhost:8000` dans `.env.local`
- Vérifier que le backend est bien accessible: `curl http://localhost:8000/docs`
- Vérifier que `ALLOWED_ORIGINS` inclut `http://localhost:5173`

### Rebuild complet après changements

```bash
# Réinitialiser tout
docker-compose down -v

# Reconstruire
docker-compose up --build
```

---

## 📊 Voir les données

### Avec pgAdmin

```bash
# Ajouter pgAdmin au docker-compose.yml:
docker-compose up

# Accès à pgAdmin: http://localhost:5050
# Email: admin@localhost
# Mot de passe: admin
```

### Avec psql

```bash
psql postgresql://chrona:chrona@localhost:5432/chrona

# Commandes utiles:
\dt                    # Lister les tables
SELECT * FROM users;   # Voir les utilisateurs
\d users               # Structure de la table users
```

---

## ✨ Variables d'Environnement

Voir `.env.example` pour la documentation complète.

Pour le développement local, les valeurs par défaut fonctionnent:
- `DOMAIN=localhost`
- `EC2_HOST=localhost`
- `EC2_PORT=8000`
- `BACKOFFICE_PORT=5173`
- `DATABASE_URL=postgresql+asyncpg://chrona:chrona@db:5432/chrona`

---

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 🆘 Support

Pour les problèmes:
1. Vérifier les logs: `docker-compose logs`
2. Consulter ce guide
3. Vérifier `CLAUDE.md` pour l'architecture du projet
4. Consulter la documentation dans `docs/`

