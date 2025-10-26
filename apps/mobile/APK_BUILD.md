# 🚀 Guide de Build APK - Chrona Mobile

Guide complet pour générer l'APK de l'application mobile Chrona pour les employés.

---

## 📋 Table des Matières

1. [Prérequis](#-prérequis)
2. [Configuration Initiale](#-configuration-initiale)
3. [Build APK Local (sans EAS)](#-build-apk-local-sans-eas)
4. [Build APK avec EAS (Recommandé)](#-build-apk-avec-eas-recommandé)
5. [Distribution de l'APK](#-distribution-de-lapk)
6. [Dépannage](#-dépannage)

---

## ✅ Prérequis

### Compte Expo (Gratuit)

1. Créer un compte sur [https://expo.dev/signup](https://expo.dev/signup)
2. Installer EAS CLI globalement:
   ```bash
   npm install -g eas-cli
   ```
3. Se connecter:
   ```bash
   eas login
   ```

### Configuration du Projet

```bash
cd apps/mobile
npm install
```

---

## 🔧 Configuration Initiale

### 1. Initialiser EAS Build

```bash
eas build:configure
```

Cela créera le fichier `eas.json` (déjà créé dans ce projet).

### 2. Configurer l'URL de l'API Backend

Éditez `eas.json` et remplacez `YOUR_SERVER_IP` par l'IP de votre serveur:

```json
{
  "build": {
    "preview": {
      "env": {
        "EXPO_PUBLIC_API_URL": "http://192.168.1.100:8000"
      }
    }
  }
}
```

**Options de configuration:**

- **Développement local**: `http://192.168.1.XXX:8000` (IP de votre PC)
- **Serveur de production**: `https://api.chrona.com`
- **Serveur de staging**: `https://staging.chrona.com`

### 3. Vérifier app.json

Le fichier `app.json` doit contenir:

```json
{
  "expo": {
    "name": "Chrona",
    "slug": "chrona-mobile",
    "version": "1.0.0",
    "android": {
      "package": "com.chrona.mobile",
      "versionCode": 1,
      "permissions": [
        "USE_BIOMETRIC",
        "USE_FINGERPRINT"
      ]
    }
  }
}
```

**Important**: Le `versionCode` doit être incrémenté à chaque nouvelle version.

---

## 📦 Build APK Local (sans EAS)

**Note**: Cette méthode nécessite Android Studio et Java JDK installés.

### 1. Installer Expo CLI

```bash
npm install -g expo-cli
```

### 2. Générer le Bundle

```bash
npx expo export --platform android
```

### 3. Build avec EAS localement

```bash
eas build --platform android --local --profile preview
```

**Limitations**:
- Nécessite Android SDK installé
- Nécessite un ordinateur puissant (8+ GB RAM)
- Durée: 10-20 minutes

---

## 🌐 Build APK avec EAS (Recommandé)

### Méthode 1: Build APK de Preview (Rapide)

**Utilisation**: Tests internes, distribution hors Google Play

```bash
eas build --platform android --profile preview
```

**Avantages**:
- ✅ Génère un fichier `.apk` directement installable
- ✅ Pas besoin de Google Play
- ✅ Distribution par email/link
- ✅ Build cloud (pas besoin de SDK local)

**Processus**:
1. Le build démarre sur les serveurs Expo
2. Durée: ~15-20 minutes
3. Un lien de téléchargement s'affiche
4. Télécharger l'APK et distribuer

**Exemple de commande avec sortie:**

```bash
$ eas build --platform android --profile preview

✔ Select a build profile: preview
✔ Using remote Android credentials (Expo server)

Build started, it may take a few minutes to complete.

Build details: https://expo.dev/accounts/yourname/projects/chrona-mobile/builds/abc123

⚙️  Building...
✅ Build finished!

Download URL: https://expo.dev/artifacts/eas/abc123.apk
```

### Méthode 2: Build Production (Google Play)

**Utilisation**: Publication sur Google Play Store

```bash
eas build --platform android --profile production
```

**Différences avec Preview:**
- Génère un fichier `.aab` (Android App Bundle) au lieu de `.apk`
- Optimisé pour le Play Store
- Signature automatique avec clés de production
- Nécessite un compte Google Play Developer (25 USD unique)

---

## 📤 Distribution de l'APK

### Option 1: Téléchargement Direct

Après le build, Expo fournit une URL de téléchargement:

```
https://expo.dev/artifacts/eas/abc123.apk
```

**Partager l'APK:**
1. Envoyer le lien par email aux employés
2. Ou générer un QR code avec l'URL
3. Scanner le QR code sur le téléphone
4. Télécharger et installer l'APK

### Option 2: QR Code de Distribution

Créer un QR code avec le lien de téléchargement:

```html
<!-- Utiliser tools/generate-apk-qr.html -->
<!DOCTYPE html>
<html>
<head>
  <title>QR Code APK Chrona</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
</head>
<body>
  <h1>QR Code APK Chrona Mobile</h1>
  <div id="qrcode"></div>
  <script>
    new QRCode(document.getElementById("qrcode"), {
      text: "https://expo.dev/artifacts/eas/abc123.apk",
      width: 256,
      height: 256
    });
  </script>
</body>
</html>
```

### Option 3: Hébergement Local

Héberger l'APK sur votre serveur interne:

```bash
# Télécharger l'APK depuis Expo
wget https://expo.dev/artifacts/eas/abc123.apk -O chrona-mobile-v1.0.0.apk

# Servir avec un serveur web simple
python -m http.server 8080

# L'APK sera accessible sur:
# http://VOTRE_IP:8080/chrona-mobile-v1.0.0.apk
```

### Option 4: Distribution par USB/Transfert de Fichier

1. Télécharger l'APK sur votre PC
2. Transférer sur le téléphone via USB ou AirDrop/Bluetooth
3. Installer manuellement

---

## 📲 Installation de l'APK sur Android

### 1. Activer les Sources Inconnues

**Android 8.0+:**
1. Ouvrir **Paramètres** > **Sécurité**
2. Activer **"Sources inconnues"** ou **"Installer des apps inconnues"**
3. Autoriser le navigateur/gestionnaire de fichiers à installer des apps

### 2. Installer l'APK

**Méthode 1: Téléchargement depuis le navigateur**
1. Ouvrir le lien de téléchargement sur le téléphone
2. Télécharger l'APK
3. Ouvrir le fichier téléchargé
4. Appuyer sur **"Installer"**

**Méthode 2: Transfert de fichier**
1. Copier l'APK sur le téléphone
2. Ouvrir le gestionnaire de fichiers
3. Naviguer vers l'APK
4. Appuyer sur le fichier
5. Appuyer sur **"Installer"**

**Méthode 3: ADB (pour développeurs)**
```bash
adb install chrona-mobile-v1.0.0.apk
```

---

## 🔄 Mises à Jour de l'Application

### Incrémenter la Version

**1. Modifier `app.json`:**

```json
{
  "expo": {
    "version": "1.0.1",  // Incrémenter
    "android": {
      "versionCode": 2   // Incrémenter (obligatoire)
    }
  }
}
```

**2. Rebuild:**

```bash
eas build --platform android --profile preview
```

**3. Distribuer la nouvelle version:**

Les employés devront désinstaller l'ancienne version et installer la nouvelle.

**Note**: Pour des mises à jour automatiques, utilisez Expo Updates (OTA).

---

## 🛠️ Dépannage

### Erreur: "Build Failed"

**Cause commune**: Dépendances manquantes ou incompatibles

**Solution:**
```bash
# Nettoyer les dépendances
rm -rf node_modules package-lock.json
npm install

# Relancer le build
eas build --platform android --profile preview
```

### Erreur: "Invalid credentials"

**Solution:**
```bash
eas login
eas build --platform android --profile preview
```

### Erreur: "APK not installing on device"

**Causes possibles:**
1. Sources inconnues pas activées → Activer dans Paramètres
2. Ancienne version installée → Désinstaller l'ancienne version
3. APK corrompu → Télécharger à nouveau

**Solution:**
```bash
# Désinstaller l'ancienne version
adb uninstall com.chrona.mobile

# Réinstaller
adb install chrona-mobile.apk
```

### Erreur: "Network request failed" après installation

**Cause**: URL de l'API incorrecte dans `eas.json`

**Solution:**
1. Vérifier l'IP du serveur backend
2. Modifier `eas.json`:
   ```json
   {
     "build": {
       "preview": {
         "env": {
           "EXPO_PUBLIC_API_URL": "http://CORRECT_IP:8000"
         }
       }
     }
   }
   ```
3. Rebuild l'APK

### Tester la connexion backend:

Ouvrir le navigateur du téléphone et aller sur:
```
http://VOTRE_IP:8000/health
```

Résultat attendu:
```json
{"status":"ok","db":"ok"}
```

---

## 🎯 Workflow Recommandé

### Pour Tests Internes (Preview)

```bash
# 1. Configurer l'URL de l'API
# Éditer eas.json → EXPO_PUBLIC_API_URL

# 2. Builder
eas build --platform android --profile preview

# 3. Télécharger l'APK
# Récupérer le lien depuis la console

# 4. Distribuer
# Envoyer le lien aux testeurs
```

### Pour Production (Google Play)

```bash
# 1. Configurer l'URL de production
# Éditer eas.json → production → EXPO_PUBLIC_API_URL

# 2. Incrémenter la version
# Éditer app.json → version + versionCode

# 3. Builder
eas build --platform android --profile production

# 4. Soumettre au Play Store
eas submit --platform android
```

---

## 📊 Comparaison des Méthodes

| Méthode | Format | Durée | Utilisation | Coût |
|---------|--------|-------|-------------|------|
| **Local Build** | APK | 10-20 min | Tests locaux | Gratuit |
| **EAS Preview** | APK | 15-20 min | Distribution interne | Gratuit (build limités) |
| **EAS Production** | AAB | 15-20 min | Google Play Store | 25 USD/an (Play Store) |

---

## 🔐 Sécurité

### Signature de l'APK

EAS Build gère automatiquement la signature:
- **Preview**: Signature de développement
- **Production**: Signature de production avec clés sécurisées

### Vérifier la Signature

```bash
# Extraire les infos de signature
jarsigner -verify -verbose -certs chrona-mobile.apk

# Vérifier le certificat
keytool -printcert -jarfile chrona-mobile.apk
```

---

## 📚 Ressources

- [Documentation EAS Build](https://docs.expo.dev/build/introduction/)
- [Configuration eas.json](https://docs.expo.dev/build/eas-json/)
- [Publication Google Play](https://docs.expo.dev/submit/android/)
- [Expo Updates (OTA)](https://docs.expo.dev/eas-update/introduction/)

---

## ✨ Résumé

**Build APK en 3 commandes:**

```bash
# 1. Installer EAS CLI
npm install -g eas-cli

# 2. Se connecter
eas login

# 3. Builder
eas build --platform android --profile preview
```

**Durée totale:** ~20 minutes (build cloud)

**Résultat:** APK prêt à distribuer aux employés
