# Installation Manuelle de Docker Compose sur EC2

Si le déploiement automatique échoue avec `sudo: docker-compose: command not found`, tu dois installer `docker-compose` manuellement sur ton EC2.

## 📋 Prérequis

- SSH connecté à l'instance EC2
- Docker déjà installé (`docker --version` doit fonctionner)

## 🚀 Installation rapide (1 minute)

### Option 1: Script automatique (recommandé)

```bash
# Se connecter à l'EC2
ssh -i ~/key.pem ubuntu@13.37.245.222

# Télécharger et exécuter le script
curl -fsSL https://raw.githubusercontent.com/your-org/Chrona_Core/feat/ec2-deployment-workflow/MANUAL_EC2_SETUP.md | bash
```

### Option 2: Installation manuelle

```bash
# 1. Déterminer votre architecture
uname -s   # Affiche: Linux
uname -m   # Affiche: x86_64 (ou aarch64, etc.)

# 2. Télécharger docker-compose
# Pour Linux x86_64:
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-Linux-x86_64" \
  -o /usr/local/bin/docker-compose

# 3. Rendre exécutable
sudo chmod +x /usr/local/bin/docker-compose

# 4. Vérifier l'installation
docker-compose --version
# Output: Docker Compose version 2.x.x, build ...
```

## 🔧 Détection automatique d'architecture

Si tu veux une commande qui marche pour n'importe quelle architecture :

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

## ✅ Vérification

Après installation, vérifiez:

```bash
# Doit afficher la version (2.x.x ou supérieur)
docker-compose --version

# Doit être accessible sans sudo (optionnel mais recommandé)
sudo usermod -aG docker $USER
newgrp docker
docker-compose --version  # Sans sudo
```

## 🐛 Dépannage

### Si le téléchargement échoue

```bash
# Vérifier votre connexion réseau
curl -I https://github.com

# Si curl n'est pas installé
sudo apt-get update
sudo apt-get install -y curl

# Essayer avec wget
wget https://github.com/docker/compose/releases/latest/download/docker-compose-Linux-x86_64 \
  -O /tmp/docker-compose
sudo mv /tmp/docker-compose /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Si vous avez une permission denied

```bash
# Vérifier que sudo fonctionne
sudo echo "Sudo works"

# S'assurer que /usr/local/bin existe
sudo mkdir -p /usr/local/bin

# Essayer l'installation à nouveau
```

## 📍 Après installation

Une fois `docker-compose` installé, vous pouvez :

```bash
cd /opt/chrona

# Relancer les services
docker-compose up -d --build

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f backend
```

## 🔄 Alternative: Utiliser Docker Compose V2 (intégré à Docker)

Depuis Docker 20.10+, vous pouvez utiliser `docker compose` (sans tiret) à la place de `docker-compose`:

```bash
cd /opt/chrona

# Au lieu de:
docker-compose up -d --build

# Utiliser:
docker compose up -d --build
```

Mettez à jour le fichier `.env` ou les scripts pour utiliser `docker compose` au lieu de `docker-compose` si vous préférez.

---

Pour plus d'aide, consultez:
- [Docker Compose Documentation](https://docs.docker.com/compose/install/)
- [GitHub Releases](https://github.com/docker/compose/releases)

