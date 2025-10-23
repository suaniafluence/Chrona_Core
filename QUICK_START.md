# 🚀 Chrona - Guide de Démarrage Rapide

Installation et déploiement en **3 commandes** !

---

## 📋 Prérequis

- **Windows 10/11** avec PowerShell
- **Podman Desktop** ou **Docker Desktop** installé
- **Python 3.11+** et **Node.js 20+**

---

## ⚡ Installation Complète (1 commande)

Ouvrez PowerShell dans le dossier `Chrona_Core` et exécutez:

```powershell
.\setup-dev.ps1
```

**Ce script fait tout automatiquement:**
- ✅ Génère les clés JWT RS256
- ✅ Crée les fichiers `.env` avec SECRET_KEY
- ✅ Démarre PostgreSQL et le Backend API
- ✅ Applique les migrations de base de données
- ✅ Crée un utilisateur admin (`admin@example.com` / `Passw0rd!`)
- ✅ Configure le kiosk avec sa clé API

**Durée:** ~2-3 minutes

---

## 🖥️ Démarrage du Back-office (1 commande)

```powershell
.\start-backoffice.ps1
```

**Accès:** http://localhost:5173

**Login:**
- Email: `admin@example.com`
- Password: `Passw0rd!`

---

## 📱 Démarrage du Kiosk (1 commande)

```powershell
.\start-kiosk.ps1
```

**Accès:** http://localhost:5174

Le kiosk est déjà configuré avec sa clé API !

---

## 📱 Configuration de l'App Mobile (1 commande)

```powershell
.\setup-mobile.ps1
```

**Ce script:**
- ✅ Détecte automatiquement votre IP WiFi
- ✅ Crée le fichier `.env` pour React Native
- ✅ Installe les dépendances npm
- ✅ Affiche les instructions pour le pare-feu

**Puis démarrez l'app:**

```bash
cd apps/mobile
npm start
```

**Options:**
- **Émulateur Android:** `npm run android`
- **Appareil physique:** Scannez le QR code avec Expo Go

---

## 🎯 Résumé des URLs

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Back-office** | http://localhost:5173 | admin@example.com / Passw0rd! |
| **Kiosk** | http://localhost:5174 | (clé API auto-configurée) |
| **Mobile** | http://[VOTRE-IP]:8000 | Créer un compte via l'app |

---

## 🔧 Commandes Utiles

### Voir les logs en temps réel

```bash
# Backend
podman logs -f chrona_core-backend-1

# Kiosk
podman logs -f chrona_core-kiosk-1

# Back-office
podman logs -f chrona_core-backoffice-1
```

### Arrêter tous les services

```bash
podman compose down
```

### Redémarrer un service

```bash
podman compose restart backend
podman compose restart kiosk
podman compose restart backoffice
```

### Réinitialiser complètement

```bash
# Attention: supprime TOUTES les données !
podman compose down -v
.\setup-dev.ps1
```

---

## 🔥 Configuration du Pare-feu Windows

**Obligatoire pour l'app mobile sur appareil physique**

Ouvrez PowerShell **en tant qu'Administrateur** :

```powershell
netsh advfirewall firewall add rule name="Chrona Backend API" dir=in action=allow protocol=TCP localport=8000
```

---

## 🐛 Dépannage

### Podman ne démarre pas

```bash
podman machine start
```

### Le backend ne répond pas

```bash
podman compose restart backend
curl http://localhost:8000/health
```

### Le kiosk affiche "API key not configured"

```bash
# Regénérer la clé API
podman exec chrona_core-backend-1 python tools/generate_kiosk_api_key.py 1

# Puis redémarrer le kiosk
podman compose restart kiosk
```

### L'app mobile ne se connecte pas

1. Vérifiez que le pare-feu est configuré (commande ci-dessus)
2. Testez depuis votre téléphone: `http://[VOTRE-IP]:8000/health`
3. Vérifiez le fichier `apps/mobile/.env` contient la bonne IP

---

## 📚 Documentation Complète

Pour plus de détails, consultez:
- `docs/GUIDE_DEPLOIEMENT.md` - Guide complet
- `CLAUDE.md` - Configuration développeur
- `docs/TODO.md` - Roadmap et tâches
- `backend/README.md` - Documentation API

---

## ✨ C'est Tout !

Vous êtes prêt à développer avec Chrona 🎉

**Questions ?** Consultez `docs/GUIDE_DEPLOIEMENT.md` ou créez une issue GitHub.
