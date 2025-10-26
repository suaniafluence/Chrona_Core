# 📦 Guide de déploiement - Chrona Kiosk Mobile

Guide complet pour déployer l'application kiosk sur des tablettes Android en production.

## 📋 Table des matières

1. [Préparation](#préparation)
2. [Build de l'APK](#build-de-lapk)
3. [Installation sur tablettes](#installation-sur-tablettes)
4. [Configuration du réseau](#configuration-du-réseau)
5. [Mode Kiosk](#mode-kiosk)
6. [Gestion des mises à jour](#gestion-des-mises-à-jour)
7. [Monitoring et maintenance](#monitoring-et-maintenance)

---

## 🔧 Préparation

### Prérequis serveur

- ✅ Backend Chrona déployé et accessible
- ✅ IP fixe ou nom de domaine configuré
- ✅ Port 8000 ouvert sur le pare-feu
- ✅ Kiosks enregistrés dans le backend (via back-office)
- ✅ Clés API générées pour chaque kiosk

### Prérequis tablettes

- **Android 8.0+** (API 26+)
- **Caméra arrière** fonctionnelle
- **WiFi** configuré sur le réseau local
- **4 GB RAM** minimum recommandé
- **Stockage** : 500 MB d'espace libre

### Matériel recommandé

- **Tablettes** : Samsung Galaxy Tab A8, Lenovo Tab M10
- **Support mural** : Pour montage fixe
- **Protection écran** : Pour usage intensif
- **Alimentation** : Câble USB-C long si montage mural

---

## 📦 Build de l'APK

### Méthode 1 : EAS Build (Cloud - Recommandé)

#### Avantages
- ✅ Pas besoin d'Android Studio
- ✅ Build dans le cloud
- ✅ Rapide et fiable
- ✅ Gratuit (compte Expo free tier)

#### Étapes

```bash
# 1. Installer EAS CLI globalement
npm install -g eas-cli

# 2. Se connecter à Expo
eas login

# 3. Générer l'APK de production
cd apps/kiosk-mobile
eas build --platform android --profile production
```

Le build prend environ **5-10 minutes**.

Une fois terminé, vous recevrez :
- Un lien de téléchargement de l'APK
- Un QR code pour installation directe

**Télécharger l'APK** :
```
https://expo.dev/artifacts/eas/[BUILD_ID].apk
```

### Méthode 2 : Build local (Avancé)

Si vous ne pouvez pas utiliser EAS (restrictions réseau, confidentialité...) :

#### Prérequis
- Android Studio
- JDK 11+
- Variables d'environnement configurées

```bash
# 1. Générer le projet Android natif
npx expo prebuild --platform android

# 2. Build avec Gradle
cd android
./gradlew assembleRelease

# 3. APK généré dans :
# android/app/build/outputs/apk/release/app-release.apk
```

---

## 📲 Installation sur tablettes

### Option 1 : Installation USB (Recommandé pour masse)

```bash
# 1. Activer le mode développeur sur la tablette
# Paramètres → À propos → Appuyer 7 fois sur "Numéro de build"

# 2. Activer le débogage USB
# Paramètres → Options développeur → Débogage USB

# 3. Connecter la tablette en USB

# 4. Installer l'APK via ADB
adb install chrona-kiosk.apk

# Pour plusieurs tablettes en parallèle :
adb devices  # Lister les appareils
adb -s [DEVICE_ID] install chrona-kiosk.apk
```

### Option 2 : Installation manuelle (Simple, pour 1-2 tablettes)

1. **Transférer l'APK** sur la tablette
   - USB (copier dans Downloads/)
   - Email (s'envoyer l'APK)
   - Google Drive / Dropbox
   - Serveur web local

2. **Autoriser les sources inconnues**
   - Paramètres → Sécurité
   - Activer "Sources inconnues" ou "Installer des applis inconnues"

3. **Installer l'APK**
   - Ouvrir le fichier APK
   - Accepter les permissions
   - Attendre l'installation

### Option 3 : Installation par QR Code (Expo)

Si vous utilisez EAS Build :

1. Scanner le QR code fourni après le build
2. Télécharger et installer l'APK directement

---

## 🌐 Configuration du réseau

### Étape 1 : Déterminer l'IP du serveur backend

```bash
# Windows
ipconfig

# Linux/macOS
ifconfig

# Chercher l'adresse IPv4 du réseau local (ex: 192.168.1.50)
```

### Étape 2 : Tester la connectivité

Depuis la tablette, ouvrir le navigateur :
```
http://[IP_SERVEUR]:8000/health
```

Réponse attendue :
```json
{"status":"ok","db":"connected"}
```

### Étape 3 : Configurer l'app kiosk

Au premier lancement de l'app :

1. Appuyer sur **⚙️** (icône paramètres)
2. Remplir le formulaire :

   | Champ | Exemple | Description |
   |-------|---------|-------------|
   | **URL de l'API** | `http://192.168.1.50:8000` | IP du serveur backend |
   | **ID du Kiosk** | `1` | Numéro unique (1, 2, 3...) |
   | **Clé API** | `kiosk-abc123...` | Clé fournie par l'admin |
   | **Type** | Entrée ou Sortie | Mode de pointage |

3. Appuyer sur **Enregistrer**

### Vérification

- 🟢 **Connecté** : Configuration OK
- 🔴 **Déconnecté** : Vérifier IP, pare-feu, backend

---

## 🔒 Mode Kiosk

Pour empêcher les utilisateurs de sortir de l'application.

### Option 1 : Screen Pinning (Android natif - Basique)

**Avantages** : Gratuit, natif Android
**Inconvénients** : Facile à contourner (bouton Retour long)

#### Configuration

1. **Paramètres** → **Sécurité** → **Épinglage d'écran**
2. Activer l'épinglage
3. Ouvrir Chrona Kiosk
4. Menu multitâche (bouton carré)
5. Icône d'épinglage sur la carte Chrona

#### Désépingler
Maintenir **Retour** + **Vue d'ensemble** pendant 3s

### Option 2 : Application Kiosk Mode (Gratuit)

Installer une app de kiosk mode depuis le Play Store :
- **Kiosk Browser Lockdown** (gratuit)
- **SureLock** (essai gratuit)
- **Fully Kiosk Browser** (payant, ~8€)

### Option 3 : MDM Enterprise (Production)

Pour une gestion professionnelle de flottes :

#### Solutions recommandées

| Solution | Prix | Avantages |
|----------|------|-----------|
| **Hexnode** | 1€/mois/device | Interface simple, kiosk robuste |
| **Microsoft Intune** | Inclus M365 | Intégration AD, très sécurisé |
| **ManageEngine** | 395€/an | On-premise, pas de cloud |
| **Google Workspace** | 6€/mois/user | Android Enterprise natif |

#### Fonctionnalités MDM

- ✅ **Kiosk mode** : Verrouillage sur une seule app
- ✅ **Déploiement** : Installation à distance
- ✅ **Configuration** : Push de configs (IP, clés API...)
- ✅ **Monitoring** : État de santé des tablettes
- ✅ **Sécurité** : Verrouillage root, désactivation USB
- ✅ **Mises à jour** : Déploiement automatique

---

## 🔄 Gestion des mises à jour

### Build d'une nouvelle version

```bash
cd apps/kiosk-mobile

# 1. Incrémenter la version dans app.json
# "version": "1.0.0" → "1.1.0"

# 2. Build nouvelle APK
eas build --platform android --profile production

# 3. Télécharger l'APK
```

### Déploiement

#### Avec MDM (recommandé)
- Upload de l'APK dans le MDM
- Push automatique vers toutes les tablettes
- Installation silencieuse

#### Sans MDM
- Installer manuellement via USB/ADB
- Ou télécharger depuis serveur web local

### Version OTA (Over-The-Air)

Expo supporte les mises à jour OTA pour JavaScript uniquement :

```bash
# Publier une mise à jour OTA
eas update --branch production

# Les changements JS/UI sont poussés instantanément
# (sans rebuild APK)
```

⚠️ **Limitations** : Modifications natives (permissions, dépendances) nécessitent un rebuild APK.

---

## 📊 Monitoring et maintenance

### Logs de l'application

#### Via USB/ADB

```bash
# Voir les logs en temps réel
adb logcat | grep Chrona

# Sauvegarder les logs
adb logcat > kiosk-logs.txt
```

#### Via MDM

La plupart des MDM offrent :
- Dashboard de santé des devices
- Logs d'erreurs
- Utilisation réseau
- État de la batterie

### Indicateurs à surveiller

| Indicateur | Normal | Action si anormal |
|------------|--------|-------------------|
| 🟢 Connexion | Vert | Vérifier réseau/backend |
| 📶 WiFi | Connecté | Réinitialiser WiFi |
| 🔋 Batterie | >20% | Vérifier alimentation |
| 📷 Caméra | Fonctionne | Nettoyer/Tester |

### Tests réguliers

**Hebdomadaire** :
- Tester un scan QR sur chaque kiosk
- Vérifier l'indicateur de connexion
- Nettoyer les caméras

**Mensuel** :
- Vérifier les logs d'erreurs
- Mettre à jour l'APK si nécessaire
- Vérifier l'espace de stockage

### Dépannage à distance

Si MDM configuré :
- Redémarrer la tablette à distance
- Réinstaller l'app
- Consulter les logs
- Prendre une capture d'écran

---

## 🛡️ Sécurité

### Checklist de sécurité

- [ ] Désactiver le débogage USB après installation
- [ ] Configurer un code PIN sur l'écran de paramètres
- [ ] Utiliser HTTPS en production (voir backend)
- [ ] Stocker les clés API de manière sécurisée
- [ ] Limiter l'accès physique aux tablettes
- [ ] Rotation régulière des clés API kiosk

### Mots de passe des tablettes

Pour éviter les manipulations :
- Code PIN simple mais non-public (ex: 1973)
- Ne pas l'afficher près de la tablette
- Changer périodiquement

---

## 📞 Support

En cas de problème :

1. Consulter [README.md](./README.md) pour dépannage
2. Vérifier les logs avec `adb logcat`
3. Tester la connexion backend : `http://[IP]:8000/health`
4. Vérifier le back-office : le kiosk est-il enregistré ?
5. Contacter l'administrateur système

---

## 📝 Checklist de déploiement

### Avant installation

- [ ] Backend déployé et accessible
- [ ] Kiosks enregistrés dans le back-office
- [ ] Clés API générées
- [ ] APK buildée et téléchargée
- [ ] Tablettes chargées et configurées WiFi

### Installation

- [ ] APK installée sur toutes les tablettes
- [ ] Permissions caméra accordées
- [ ] Configuration IP/ID/Clé API saisie
- [ ] Connexion vérifiée (🟢 vert)
- [ ] Test de scan QR réussi

### Sécurisation

- [ ] Mode kiosk activé
- [ ] Débogage USB désactivé
- [ ] Tablettes montées/sécurisées
- [ ] Code PIN configuré (si applicable)

### Documentation

- [ ] IPs et IDs documentés
- [ ] Clés API sauvegardées (gestionnaire de mots de passe)
- [ ] Procédure de maintenance rédigée
- [ ] Contact support défini

---

## ✅ Résumé

| Étape | Temps | Difficulté |
|-------|-------|------------|
| Build APK (EAS) | 10 min | ⭐ Facile |
| Installation (manuelle) | 5 min/tablette | ⭐ Facile |
| Configuration réseau | 10 min | ⭐⭐ Moyen |
| Mode kiosk (Screen Pinning) | 5 min | ⭐ Facile |
| MDM (optionnel) | 1-2h setup | ⭐⭐⭐ Avancé |

**Temps total estimé** : 30-45 minutes pour 1 tablette (sans MDM)

Bonne mise en production ! 🚀
