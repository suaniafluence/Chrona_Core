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
| `EC2_HOST` | Adresse IP publique de l'instance EC2 | `54.123.456.789` |
| `EC2_USER` | Utilisateur SSH (ubuntu pour Ubuntu, ec2-user pour Amazon Linux) | `ubuntu` |
| `EC2_SSH_KEY` | Contenu du fichier `.pem` (voir section ci-dessous) | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+asyncpg://user:pass@db-host:5432/chrona` |
| `SECRET_KEY` | Clé secrète pour JWT (doit être aléatoire et sécurisé) | `your-secure-random-key-here` |
| `ALLOWED_ORIGINS` | Origines CORS autorisées (séparées par virgules) | `http://54.123.456.789:5173,http://api.example.com` |

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
   - **Backend URL** : `http://54.123.456.789:8000` (remplacez par votre IP EC2)
4. Cliquez sur **Run workflow**

### Manuellement via SSH

Si vous préférez déployer manuellement :

```bash
# Connexion à l'instance
ssh -i /path/to/your-key.pem ubuntu@54.123.456.789

# Sur l'instance EC2
cd /opt/chrona

# Créer le fichier .env
cat > .env <<EOF
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/chrona
SECRET_KEY=your-secure-random-key
ALLOWED_ORIGINS=http://54.123.456.789:5173,http://54.123.456.789:8000
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_URL=http://54.123.456.789:8000
EOF

# Démarrer les services
docker compose -f docker-compose.prod.yml up -d --build
```

## Vérifier le déploiement

Une fois le workflow terminé, vérifiez que tout fonctionne :

```bash
# SSH dans l'instance
ssh -i /path/to/your-key.pem ubuntu@54.123.456.789

# Vérifier l'état des services
docker compose -f /opt/chrona/docker-compose.prod.yml ps

# Voir les logs
docker compose -f /opt/chrona/docker-compose.prod.yml logs -f backend
docker compose -f /opt/chrona/docker-compose.prod.yml logs -f backoffice

# Tester le backend
curl http://localhost:8000/docs

# Tester le backoffice
curl http://localhost:5173
```

## Accéder à l'application

- **Backend (API)** : `http://54.123.456.789:8000`
  - Swagger UI : `http://54.123.456.789:8000/docs`
- **Backoffice** : `http://54.123.456.789:5173`

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
# Test de connexion (si psql est installé)
psql "postgresql://user:pass@db-host:5432/chrona"
```

## Mise à jour de l'application

Pour redéployer après des changements :

1. Poussez vos modifications sur `main` (ou votre branche)
2. Allez à **Actions → Deploy** et lancez le workflow
3. Les services vont redémarrer automatiquement

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

