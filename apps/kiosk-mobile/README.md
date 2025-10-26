# Chrona Kiosk - Application Android

Application React Native pour les tablettes kiosk de pointage Chrona.

## 🎯 Fonctionnalités

- **Scanner QR Code** : Scan des codes QR signés JWT des employés
- **Validation en temps réel** : Communication directe avec l'API backend
- **Configuration dynamique** : Interface de configuration de l'IP du serveur
- **Indicateur de connexion** : Vérification automatique de la connectivité
- **Interface kiosk** : Design optimisé pour tablettes en mode kiosk

## 📋 Prérequis

### Pour le développement local

- **Node.js** >= 18
- **npm** ou **yarn**
- **Expo Go** (pour tester sur téléphone physique)
- **Android Studio** (optionnel, pour émulateur Android)

### Pour générer l'APK

- **Compte Expo** (gratuit) : https://expo.dev/signup
- **EAS CLI** : `npm install -g eas-cli`

## 🚀 Installation et développement

### 1. Installer les dépendances

```bash
cd apps/kiosk-mobile
npm install
```

### 2. Configuration initiale

L'application démarre avec une configuration par défaut :
- **API URL** : `http://192.168.1.100:8000`
- **Kiosk ID** : `1`
- **Type de pointage** : `clock_in`

Vous pouvez modifier ces paramètres via l'écran de configuration (icône ⚙️).

### 3. Lancer en mode développement

#### Sur téléphone physique (recommandé)

```bash
npm start
```

1. Scanner le QR code avec **Expo Go** (Android/iOS)
2. L'app se charge automatiquement
3. Utiliser le bouton ⚙️ pour configurer l'IP du backend

#### Sur émulateur Android

```bash
# Démarrer l'émulateur Android depuis Android Studio
npm run android
```

## 📱 Générer l'APK pour distribution

### Option 1 : Build avec EAS (Recommandé)

EAS Build permet de générer des APK sans avoir Android Studio installé.

#### 1. Installer EAS CLI

```bash
npm install -g eas-cli
```

#### 2. Se connecter à Expo

```bash
eas login
```

Créer un compte gratuit sur https://expo.dev/signup si nécessaire.

#### 3. Configurer le projet

```bash
eas build:configure
```

#### 4. Générer l'APK

```bash
# Build de preview (APK)
eas build --platform android --profile preview

# Build de production (APK)
eas build --platform android --profile production
```

Le build se fait dans le cloud Expo. Une fois terminé, vous recevrez un lien pour télécharger l'APK.

#### 5. Télécharger et installer l'APK

1. Télécharger l'APK depuis le lien fourni
2. Transférer sur la tablette Android
3. Activer "Sources inconnues" dans les paramètres Android
4. Installer l'APK

### Option 2 : Build local avec Android Studio

Si vous préférez un build 100% local (plus long et complexe) :

#### 1. Installer Android Studio

Télécharger depuis https://developer.android.com/studio

#### 2. Configurer les variables d'environnement

```bash
# Windows (PowerShell)
$env:ANDROID_HOME = "C:\Users\VotreNom\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\platform-tools"

# Linux/macOS
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### 3. Générer le projet Android

```bash
npx expo prebuild --platform android
```

#### 4. Build de l'APK

```bash
cd android
./gradlew assembleRelease
```

L'APK sera généré dans `android/app/build/outputs/apk/release/app-release.apk`

## ⚙️ Configuration de la tablette kiosk

### 1. Installation de l'APK

1. Transférer l'APK sur la tablette via USB ou téléchargement
2. Autoriser l'installation depuis des sources inconnues
3. Installer l'APK

### 2. Configuration du backend

#### Option A : Configuration automatique par QR Code ⭐ (Recommandé)

**Avantages** :
- ✅ Instantané (2 secondes)
- ✅ Zéro saisie manuelle
- ✅ Aucune erreur de frappe
- ✅ Idéal pour déploiement de plusieurs tablettes

**Étapes** :

1. **Sur votre PC** : Ouvrir `apps/kiosk-mobile/tools/generate-config-qr.html` dans un navigateur
2. Remplir le formulaire :
   - **URL de l'API** : `http://192.168.1.50:8000`
   - **ID du Kiosk** : `1` (ou autre numéro unique)
   - **Nom du Kiosk** : `Kiosk Entrée` (optionnel)
   - **Clé API** : `kiosk-abc123...` (fournie par l'admin)
   - **Type** : Entrée ou Sortie
3. Cliquer sur **"Générer le QR Code"**
4. **Sur la tablette** : Ouvrir l'app Chrona Kiosk
5. Appuyer sur **⚙️** → **"Scanner un QR de configuration"** 📷
6. Scanner le QR code affiché sur votre PC
7. Confirmer la configuration

✅ **C'est terminé !** La tablette est configurée et prête à l'emploi.

#### Option B : Configuration manuelle

Si vous préférez saisir manuellement :

1. Appuyer sur l'icône ⚙️ (en haut à droite)
2. Faire défiler vers le bas (après le bouton de scan QR)
3. Configurer les paramètres :
   - **URL de l'API** : `http://[IP_DU_SERVEUR]:8000`
     - Exemple : `http://192.168.1.50:8000`
     - Ne pas oublier le `http://` et le port `:8000`
   - **ID du Kiosk** : Numéro unique du kiosk (1, 2, 3...)
   - **Clé API** : Clé d'authentification fournie par l'admin
   - **Type de pointage** : `Entrée` ou `Sortie`
4. Appuyer sur **Enregistrer**

### 3. Vérifier la connexion

L'indicateur de connexion (en haut à droite) doit afficher :
- 🟢 **Connecté** : Backend accessible
- 🔴 **Déconnecté** : Problème de connexion

### 4. Tester le scan QR

1. Ouvrir l'app mobile employé sur un téléphone
2. Générer un QR code de pointage
3. Scanner avec la tablette kiosk
4. Vérifier le message de validation

## 🔧 Mode kiosk Android

Pour verrouiller la tablette en mode kiosk (empêcher la sortie de l'app) :

### Option 1 : Screen Pinning (Android natif)

1. Aller dans **Paramètres** → **Sécurité** → **Épinglage d'écran**
2. Activer l'épinglage d'écran
3. Ouvrir l'app Chrona Kiosk
4. Ouvrir le menu multitâche (bouton carré)
5. Appuyer sur l'icône d'épinglage

### Option 2 : Application MDM (Kiosk Mode professionnel)

Utiliser une solution MDM comme :
- **Hexnode**
- **ManageEngine**
- **Microsoft Intune**

Ces solutions permettent :
- Verrouillage en mode kiosk
- Gestion à distance
- Déploiement de configurations
- Restrictions d'accès

## 🐛 Dépannage

### L'app ne se connecte pas au backend

1. Vérifier que le backend est démarré : `http://[IP]:8000/health`
2. Vérifier l'IP dans les paramètres (⚙️)
3. Vérifier que la tablette et le serveur sont sur le même réseau WiFi
4. Désactiver temporairement le pare-feu Windows pour tester

### La caméra ne fonctionne pas

1. Vérifier les permissions caméra dans les paramètres Android
2. Redémarrer l'application
3. Redémarrer la tablette

### Le QR code n'est pas reconnu

1. Vérifier la luminosité de l'écran du téléphone
2. Rapprocher/éloigner le téléphone de la caméra
3. Nettoyer l'objectif de la caméra

### Erreur "Kiosk non autorisé"

1. Vérifier la clé API dans les paramètres
2. Contacter l'administrateur pour vérifier l'enregistrement du kiosk

## 📂 Structure du projet

```
apps/kiosk-mobile/
├── src/
│   ├── components/          # Composants React Native
│   │   ├── QRScanner.tsx   # Scanner de QR codes
│   │   ├── ValidationResult.tsx
│   │   └── ConnectionStatus.tsx
│   ├── screens/             # Écrans de l'app
│   │   ├── HomeScreen.tsx  # Écran principal
│   │   └── SettingsScreen.tsx # Configuration
│   └── services/            # Services API
│       └── api.ts          # Client API et configuration
├── App.tsx                  # Point d'entrée
├── app.json                 # Configuration Expo
├── eas.json                 # Configuration EAS Build
└── package.json
```

## 🔐 Sécurité

- Les clés API sont stockées dans AsyncStorage (chiffré sur Android)
- Communication en HTTP (utiliser HTTPS en production)
- Pas de stockage de données sensibles dans l'app
- Validation JWT côté backend

## 📝 TODO

- [ ] Support HTTPS avec certificats auto-signés
- [ ] Mode offline avec cache des validations
- [ ] Notifications push pour alertes système
- [ ] Interface d'administration intégrée
- [ ] Support multi-langues (FR/EN)

## 📄 Licence

Chrona Time Tracking System - Proprietary

## 🤝 Support

Pour toute question ou problème :
- Consulter `docs/GUIDE_DEPLOIEMENT.md`
- Ouvrir une issue sur le dépôt Git
