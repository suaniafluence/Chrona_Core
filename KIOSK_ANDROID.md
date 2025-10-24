# 📱 Chrona - Guide du Kiosk sur Tablette Android

Vous avez une tablette Android et vous voulez l'utiliser comme kiosk Chrona pour scanner les QR codes de punch ? Ce guide vous explique comment configurer et utiliser le kiosk.

---

## 🎯 Vue d'ensemble

Le **Kiosk Chrona** est une application web qui fonctionne sur n'importe quel navigateur, y compris sur les tablettes Android. Elle permet:

- 📱 Scanner les QR codes générés par l'appli mobile
- ⏱️ Enregistrer les punch-in/punch-out
- 📊 Afficher l'historique des pointages
- 🔒 Accès sécurisé avec clé API

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir:

✅ **Sur votre PC Windows:**
- Docker Desktop ou Podman Desktop installé
- Chrona Core en cours d'exécution (`docker compose up -d`)
- Les scripts PowerShell (`setup-kiosk-android.ps1`, `start-kiosk-android.ps1`)

✅ **Sur votre tablette Android:**
- Un navigateur web (Chrome, Firefox, Opera, etc.)
- Connexion WiFi disponible
- **Même réseau WiFi que le PC** (très important!)

---

## ⚡ Configuration Rapide (1 commande)

### Sur le PC Windows

Ouvrez PowerShell dans le dossier `Chrona_Core` et exécutez:

```powershell
.\setup-kiosk-android.ps1
```

Ce script va:
1. ✅ Vérifier que les services Chrona tournent
2. ✅ Récupérer votre adresse IP locale
3. ✅ Générer la clé API du kiosk
4. ✅ Configurer les fichiers `.env`
5. ✅ Afficher les instructions d'accès

**Durée:** ~30 secondes

---

## 🚀 Démarrer le Kiosk

### Chaque fois que vous voulez utiliser le kiosk:

```powershell
.\start-kiosk-android.ps1
```

Cela va:
- Démarrer/redémarrer le conteneur kiosk
- Vérifier la configuration réseau
- Afficher l'URL d'accès

---

## 📱 Utilisation sur Tablette Android

### 1️⃣ Se connecter au même WiFi

Sur votre tablette Android:
- Allez dans **Paramètres → WiFi**
- Connectez-vous au même WiFi que votre PC
- Notez bien l'adresse IP affichée par le script PowerShell

### 2️⃣ Ouvrir le navigateur

- Ouvrez **Chrome**, **Firefox** ou tout autre navigateur
- Dans la barre d'adresse, tapez:

```
http://ADRESSE_IP:5174
```

**Exemple:** `http://192.168.1.100:5174`

### 3️⃣ Utiliser le kiosk

Une fois connecté, vous verrez:

- **Vue principale**: Zone de scan de code QR
- **Indicateur de connexion**: Vert = connecté, Rouge = déconnecté
- **Historique**: Liste des punches récents
- **Statut**: Information sur la dernière action

---

## 🔍 Comment trouver l'adresse IP

Après avoir exécuté `setup-kiosk-android.ps1`, le script affiche:

```
📱 ACCÈS DEPUIS VOTRE TABLETTE ANDROID:

   URL du Kiosk:
   ► http://192.168.1.100:5174
```

**Utilisez cette adresse!**

---

## ⚙️ Configuration du Pare-feu Windows

Si votre tablette ne peut pas se connecter, le pare-feu Windows bloque peut-être les connexions.

Pour autoriser l'accès, exécutez cette commande en **tant qu'administrateur** dans PowerShell:

```powershell
netsh advfirewall firewall add rule name="Chrona Kiosk" dir=in action=allow protocol=TCP localport=5174
netsh advfirewall firewall add rule name="Chrona Backend" dir=in action=allow protocol=TCP localport=8000
```

---

## 🧪 Tester la Connexion

Avant d'utiliser le kiosk, vérifiez que votre tablette peut atteindre le serveur.

### Sur votre tablette Android:

1. Ouvrez le navigateur
2. Accédez à: `http://ADRESSE_IP:8000/health`
3. Vous devriez voir:

```json
{"status":"ok","db":"ok"}
```

**Si vous voyez une erreur de connexion:**
- ❌ Vérifiez le WiFi
- ❌ Vérifiez l'adresse IP
- ❌ Vérifiez le pare-feu Windows
- ❌ Vérifiez que `docker compose up -d` est actif

---

## 📸 Workflow du Kiosk

### Scénario: Un employé fait un punch-in

1. **Sur l'appli mobile** (téléphone):
   - L'employé se connecte avec ses identifiants
   - Appui sur "Demander QR pour punch-in"
   - Un QR code s'affiche à l'écran du téléphone (valide 30 secondes)

2. **Sur le kiosk** (tablette Android):
   - Positionnez la caméra face au QR code du téléphone
   - Le kiosk scanne automatiquement
   - ✅ Succès! Le punch est enregistré
   - Affichage du nom de l'employé et de l'heure

3. **Confirmation**:
   - Le punch apparaît dans l'historique du kiosk
   - L'employé recevra une notification sur son téléphone
   - Le punch est enregistré en base de données

---

## 🎥 Caméra et Scan QR

Le kiosk Android fonctionne comme sur desktop:

- **Autorisations**: La tablette vous demandera accès à la caméra au premier lancement
  - ✅ Acceptez pour permettre le scan de QR codes

- **Positionnement**: Maintenez la caméra face au QR code du téléphone
  - Distance idéale: 15-30 cm
  - Bonne luminosité requis

- **Détection**: Automatique - le QR code se scanne dès qu'il est détecté

---

## 📊 Interface du Kiosk

### Parties principales:

```
┌─────────────────────────────────────┐
│  Chrona - Kiosk                  🟢 │  ← Statut connexion
├─────────────────────────────────────┤
│                                     │
│   [Zone de scan QR avec caméra]     │
│                                     │
├─────────────────────────────────────┤
│ Historique:                         │
│ • 14:32 - Dupont Martin - Clock In │
│ • 12:15 - Leblanc Sophie - Clock O │
│ • 09:45 - Martin Jean - Clock In   │
└─────────────────────────────────────┘
```

---

## 🔐 Sécurité

### Informations importantes:

- **Clé API**: Générée automatiquement et stockée en local
- **QR codes**: Valides 30 secondes seulement (anti-replay)
- **Signature JWT**: Chaque QR code est signé avec RS256
- **Réseau local**: Communication en HTTP sur réseau privé (WiFi)

### Bonnes pratiques:

- ✅ Gardez la tablette dans un endroit sécurisé
- ✅ Gardez-la sur le même réseau WiFi que le serveur
- ✅ Ne partez pas la tablette en mode kiosk sans surveillance
- ✅ Vérifiez que seuls les employés autorisés ont accès

---

## 🐛 Dépannage

### La tablette ne peut pas atteindre le serveur

**Symptôme:** "Impossible de se connecter" ou timeout

**Solutions:**
1. Vérifiez le WiFi - même réseau que le PC
2. Vérifiez l'adresse IP - essayez l'IP du PC au lieu de "localhost"
3. Vérifiez le pare-feu Windows
4. Redémarrez le conteneur: `docker compose restart kiosk`
5. Vérifiez les logs: `docker compose logs kiosk`

---

### Le QR code ne se scanne pas

**Symptôme:** La caméra voit le QR mais rien ne se passe

**Solutions:**
1. Vérifiez les permissions - acceptez l'accès caméra si demandé
2. Bonne luminosité - QR codes ont besoin de lumière
3. Distance correcte - 15-30 cm du QR code
4. Nettoyez l'objectif de la caméra

---

### Connexion est intermittente

**Symptôme:** "Connexion perdue" par moments

**Solutions:**
1. Vérifiez la force du signal WiFi
2. Éloignez-vous des obstacles (murs, métaux)
3. Redémarrez le WiFi de la tablette
4. Redémarrez le conteneur: `docker compose restart kiosk`

---

## 💡 Astuces et Bonnes Pratiques

### Pour une utilisation au quotidien:

- 📍 Positionnez la tablette à hauteur de poitrine de l'employé
- 💾 Gardez-la chargée ou branchez-la en permanence
- 🔒 Utilisez un support sécurisé/encastré pour la tablette
- 📱 Affichez l'historique pour feedback immédiat
- 🌐 Testez la connexion WiFi à la première utilisation

### Pour la maintenance:

- 🔄 Redémarrage quotidien: `docker compose restart kiosk`
- 📋 Vérifiez les logs régulièrement: `docker compose logs kiosk`
- 🔧 Gardez Docker/Podman à jour
- 💾 Sauvegardez les configurations

---

## 📞 Support et Questions

### Fichiers de configuration:

- **Kiosk .env**: `apps/kiosk/.env`
- **Backend config**: `backend/.env`
- **Docker compose**: `docker-compose.yml`

### Logs et diagnostic:

```powershell
# Voir les logs du kiosk
docker compose logs -f kiosk

# Voir les logs du backend
docker compose logs -f backend

# Vérifier le statut des services
docker compose ps

# Redémarrer tout
docker compose restart
```

---

## 🎓 Ressources Supplémentaires

- **Guide principal**: `QUICK_START.md`
- **Documentation API**: `http://localhost:8000/docs`
- **Dépôt GitHub**: https://github.com/suaniafluence/Chrona_Core

---

## ✅ Résumé

Pour utiliser le kiosk sur tablette Android:

1. Exécutez: `.\setup-kiosk-android.ps1` (une seule fois)
2. Exécutez: `.\start-kiosk-android.ps1` (chaque utilisation)
3. Accédez à `http://ADRESSE_IP:5174` depuis votre tablette
4. Scannez les QR codes des employés!

**C'est tout! Vous êtes prêt.** 🚀
