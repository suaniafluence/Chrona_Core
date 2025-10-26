# ✅ Application Mobile Employé - Build APK Complet

## 🎯 Objectif

Permettre aux employés d'installer l'application mobile Chrona sur leurs téléphones Android pour générer des QR codes de pointage.

---

## 📱 Fonctionnalités de l'Application Employé

### Authentification et Sécurité
- ✅ **Login sécurisé** avec email/password
- ✅ **JWT tokens** stockés dans SecureStore
- ✅ **Enregistrement d'appareil** avec device fingerprint
- ✅ **Authentification biométrique** (optionnel)

### Onboarding (Niveau B)
- ✅ **Code HR** fourni par l'administrateur
- ✅ **Vérification OTP** par email/SMS
- ✅ **Device attestation** pour lier l'appareil au compte

### Génération de QR Code
- ✅ **QR codes éphémères** (durée de vie: 30 secondes)
- ✅ **Tokens JWT signés RS256** avec nonce et jti
- ✅ **Countdown visuel** pour expiration
- ✅ **Protection anti-capture** (screenshot/screen recording)

### Historique
- ✅ **Liste des pointages** (entrée/sortie)
- ✅ **Pull-to-refresh** pour actualiser
- ✅ **Timestamps** et détails des kiosks

---

## 🏗️ Architecture de l'Application

### Structure des Écrans

```
apps/mobile/
├── App.tsx                          # Navigation principale
├── src/
│   ├── screens/
│   │   ├── LoginScreen.tsx         # Écran de connexion
│   │   ├── HomeScreen.tsx          # Menu principal
│   │   ├── QRCodeScreen.tsx        # Génération QR code
│   │   ├── HistoryScreen.tsx       # Historique pointages
│   │   └── onboarding/
│   │       ├── HRCodeScreen.tsx              # Étape 1: Code HR
│   │       ├── OTPVerificationScreen.tsx     # Étape 2: OTP
│   │       └── CompleteOnboardingScreen.tsx  # Étape 3: Finalisation
│   ├── services/
│   │   ├── api.ts                  # Client API Axios
│   │   ├── secureStorage.ts        # Stockage JWT
│   │   ├── deviceSecurity.ts       # Device fingerprint
│   │   └── biometricAuth.ts        # Authentification biométrique
│   └── components/
│       └── SecurityCheck.tsx       # Vérifications de sécurité
```

### Technologies Utilisées

- **Framework**: React Native + Expo
- **Navigation**: React Navigation
- **HTTP Client**: Axios
- **Stockage sécurisé**: expo-secure-store
- **QR Code**: react-native-qrcode-svg
- **Biométrie**: expo-local-authentication
- **Device info**: react-native-device-info

---

## 🚀 Build APK - Guide Complet

### 🎯 Deux Méthodes de Build

| Méthode | Builds/mois | Hébergement | Automatisation | Recommandé |
|---------|-------------|-------------|----------------|------------|
| **GitHub Releases** | ♾️ Illimité | Permanent | GitHub Actions | ✅ OUI |
| **EAS Direct** | 30 | 30 jours | Manuel | Pour tests |

### Prérequis

1. **Compte Expo** (gratuit): https://expo.dev/signup
2. **Token Expo** pour GitHub Actions:
   - Générer: https://expo.dev/accounts/[username]/settings/access-tokens
   - Ajouter comme secret GitHub: `EXPO_TOKEN`
3. **EAS CLI** (optionnel pour build manuel):
   ```bash
   npm install -g eas-cli
   ```

### Méthode 1: GitHub Releases (Recommandé - Automatique)

**Build automatique avec GitHub Actions - Une seule commande !**

```powershell
cd apps/mobile

# Créer une release version 1.0.0
.\create-release.ps1 -Version 1.0.0 -Push
```

**Le script fait automatiquement:**
- ✅ Met à jour `app.json` (version + versionCode)
- ✅ Crée un commit de version
- ✅ Crée un tag Git `mobile-v1.0.0`
- ✅ Push vers GitHub
- ✅ **Déclenche GitHub Actions** qui:
  - Build l'APK avec EAS (~20 min)
  - Crée une GitHub Release
  - Upload l'APK comme asset
  - Génère le SHA256 checksum

**Résultat:**
- **URL stable**: `https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk`
- **Hébergement permanent** sur GitHub
- **Builds illimités** (gratuit)

**Durée totale**: ~25 minutes (automatique)

**📚 Guide complet**: [GITHUB_RELEASES.md](apps/mobile/GITHUB_RELEASES.md)

### Méthode 2: Build Manuel avec EAS (Pour Tests)

**Pour tests rapides uniquement**

```powershell
cd apps/mobile

# Auto-détection de l'IP WiFi
.\build-apk.ps1 -AutoDetectIP

# Ou spécifier l'URL manuellement
.\build-apk.ps1 -ApiUrl http://192.168.1.100:8000
```

**Le script fait automatiquement:**
- ✅ Détecte votre IP WiFi (si -AutoDetectIP)
- ✅ Installe EAS CLI si absent
- ✅ Vérifie l'authentification Expo
- ✅ Met à jour eas.json avec l'URL de l'API
- ✅ Lance le build cloud

**Limitations:**
- ❌ URL temporaire (expire après 30 jours)
- ❌ Limité à 30 builds/mois
- ❌ Nécessite compte Expo pour télécharger

**Durée**: ~20 minutes

### Méthode 3: Build Complètement Manuel (Déconseillé)

**Étape 1: Se connecter à Expo**

```bash
eas login
```

**Étape 2: Configurer l'URL de l'API**

Éditer `apps/mobile/eas.json`:

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

**Étape 3: Lancer le build**

```bash
cd apps/mobile
eas build --platform android --profile preview
```

**Étape 4: Récupérer l'APK**

Après le build, Expo fournit une URL de téléchargement:

```
https://expo.dev/artifacts/eas/abc123.apk
```

---

## 📤 Distribution de l'APK

### 🎯 URL de Téléchargement

**Méthode GitHub Releases (Recommandée):**
```
https://github.com/USER/REPO/releases/download/mobile-vX.Y.Z/chrona-mobile-vX.Y.Z.apk
```

**Exemple:**
```
https://github.com/mycompany/chrona/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

✅ **Avantages:**
- URL permanente (ne expire jamais)
- Hébergement gratuit illimité
- Checksum SHA256 fourni
- Historique de toutes les versions

### Option 1: QR Code de Distribution

**1. Générer le QR code**

Ouvrir dans un navigateur:
```
apps/mobile/tools/generate-apk-qr.html
```

**2. Entrer l'URL de l'APK**

**GitHub Release (recommandé):**
```
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

**Ou EAS Build (temporaire):**
```
https://expo.dev/artifacts/eas/abc123.apk
```

**3. Générer et télécharger**

- Cliquer sur "Générer le QR Code"
- Cliquer sur "Télécharger PNG"
- Distribuer le QR code aux employés

**4. Les employés scannent le QR code**

- Scanner avec l'appareil photo du téléphone
- Télécharger l'APK
- Installer l'application

### Option 2: Envoi par Email

**1. Récupérer l'URL de l'APK**

**GitHub Release:**
```
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

**2. Envoyer par email**

```
Objet: Installation Chrona Mobile - Application de Pointage

Bonjour,

Veuillez installer l'application mobile Chrona pour effectuer vos pointages.

🔗 Lien de téléchargement:
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk

📋 Installation:
1. Cliquer sur le lien ci-dessus
2. Télécharger le fichier APK
3. Ouvrir le fichier téléchargé
4. Autoriser l'installation depuis sources inconnues si demandé
5. Installer l'application

Identifiants:
- Email: votre.email@entreprise.com
- Code HR: [fourni par RH]

Support: support@chrona.com
```

### Option 3: Hébergement Interne

**1. Héberger l'APK sur votre serveur**

```bash
# Télécharger l'APK depuis GitHub Release
wget https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk

# Servir avec Python
python -m http.server 8080

# L'APK sera accessible sur:
# http://VOTRE_IP:8080/chrona-mobile-v1.0.0.apk
```

**2. Créer une page de téléchargement**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Télécharger Chrona Mobile</title>
</head>
<body>
    <h1>📲 Application Chrona Mobile</h1>
    <p>Version: 1.0.0</p>
    <a href="/chrona-mobile.apk" download>
        <button>📥 Télécharger APK</button>
    </a>
</body>
</html>
```

---

## 📲 Installation sur Android

### Étape 1: Autoriser les Sources Inconnues

**Android 8.0+:**
1. Paramètres → Sécurité
2. Activer "Installer des apps inconnues"
3. Autoriser le navigateur ou gestionnaire de fichiers

### Étape 2: Installer l'APK

**Via téléchargement:**
1. Télécharger l'APK depuis le lien/QR code
2. Ouvrir le fichier téléchargé
3. Appuyer sur "Installer"
4. Attendre la fin de l'installation

**Via transfert de fichier:**
1. Copier l'APK sur le téléphone (USB/Bluetooth)
2. Ouvrir le gestionnaire de fichiers
3. Naviguer vers l'APK
4. Appuyer sur le fichier
5. Appuyer sur "Installer"

### Étape 3: Première Connexion

**Nouvel employé (Onboarding):**
1. Ouvrir l'application
2. Appuyer sur "S'inscrire"
3. Entrer le **code HR** fourni par l'administrateur
4. Vérifier le **code OTP** reçu par email
5. L'appareil est enregistré

**Employé existant:**
1. Ouvrir l'application
2. Se connecter avec email/password
3. Enregistrer l'appareil si premier appareil

---

## 🔄 Mises à Jour de l'Application

### Incrémenter la Version

**1. Modifier `app.json`:**

```json
{
  "expo": {
    "version": "1.0.1",      // Version lisible
    "android": {
      "versionCode": 2       // Numéro de version (incrémenter)
    }
  }
}
```

**2. Rebuild:**

```bash
.\build-apk.ps1 -AutoDetectIP
```

**3. Distribuer la nouvelle version**

Les employés devront:
- Désinstaller l'ancienne version
- Installer la nouvelle version
- Se reconnecter

---

## 🔐 Sécurité de l'Application

### Protections Implémentées

**Authentification:**
- JWT tokens avec RS256
- Tokens stockés dans SecureStore (chiffrement hardware)
- Expiration automatique après 60 minutes

**Device Binding:**
- Device fingerprint unique
- Attestation lors de l'enregistrement
- Révocation possible par admin

**QR Code:**
- Tokens éphémères (30 secondes)
- Nonce unique (single-use)
- JTI pour prévention de replay attacks

**Anti-Capture:**
- Protection screenshot (expo-screen-capture)
- Détection de screen recording
- Blur automatique en background

### Permissions Android

**Requises:**
- `INTERNET` - Connexion au backend
- `ACCESS_NETWORK_STATE` - Vérifier connectivité
- `USE_BIOMETRIC` - Authentification biométrique (optionnel)

**Bloquées:**
- `RECORD_AUDIO` - Pas d'enregistrement audio
- `ACCESS_FINE_LOCATION` - Pas de géolocalisation
- `ACCESS_COARSE_LOCATION` - Pas de localisation

---

## 🧪 Tests de l'Application

### Test de Connexion Backend

**1. Vérifier l'accès réseau**

Ouvrir le navigateur du téléphone:
```
http://VOTRE_IP:8000/health
```

Résultat attendu:
```json
{"status":"ok","db":"ok"}
```

**2. Tester la génération de QR code**

1. Se connecter à l'application
2. Appuyer sur "Générer QR Code"
3. Vérifier que le QR code s'affiche
4. Vérifier le countdown (30s)

**3. Tester le pointage**

1. Générer un QR code sur mobile
2. Scanner avec une tablette kiosk
3. Vérifier la confirmation
4. Vérifier dans l'historique

---

## 🛠️ Dépannage

### Problème: "Network request failed"

**Causes possibles:**
1. Backend non accessible
2. URL de l'API incorrecte dans eas.json
3. Pare-feu bloquant le port 8000

**Solutions:**
```bash
# 1. Vérifier que le backend est démarré
podman ps

# 2. Tester l'accès depuis le navigateur du téléphone
http://VOTRE_IP:8000/health

# 3. Configurer le pare-feu Windows
netsh advfirewall firewall add rule name="Chrona Backend" dir=in action=allow protocol=TCP localport=8000

# 4. Rebuild avec la bonne URL
.\build-apk.ps1 -ApiUrl http://CORRECT_IP:8000
```

### Problème: "APK not installing"

**Causes possibles:**
1. Sources inconnues pas autorisées
2. Ancienne version installée
3. APK corrompu

**Solutions:**
```bash
# 1. Activer sources inconnues dans Paramètres

# 2. Désinstaller l'ancienne version
# Via adb:
adb uninstall com.chrona.mobile

# 3. Réinstaller
adb install chrona-mobile.apk
```

### Problème: "Login failed"

**Causes possibles:**
1. Identifiants incorrects
2. Compte non créé

**Solutions:**
1. Vérifier email/password
2. Créer un compte via onboarding (code HR)
3. Contacter l'administrateur

### Problème: "Device registration failed"

**Causes possibles:**
1. Code HR invalide
2. Code OTP expiré
3. Appareil déjà enregistré

**Solutions:**
1. Demander un nouveau code HR
2. Redemander un code OTP
3. Révoquer l'appareil existant via back-office

---

## 📊 Statistiques de Build

### Temps de Build

| Méthode | Durée | Plateforme |
|---------|-------|------------|
| EAS Cloud | 15-20 min | Serveurs Expo |
| EAS Local | 10-15 min | PC local (Android SDK requis) |

### Taille de l'APK

| Profil | Taille APK | Format |
|--------|-----------|--------|
| Preview | ~30-50 MB | APK |
| Production | ~25-40 MB | AAB (optimisé) |

### Coûts

| Service | Coût | Limite Gratuite |
|---------|------|----------------|
| Expo Account | Gratuit | Illimité |
| EAS Build | Gratuit | 30 builds/mois |
| Google Play Developer | 25 USD | Unique (optionnel) |

---

## 📚 Fichiers Créés/Modifiés

### Configuration de Build

- `apps/mobile/eas.json` - Configuration EAS Build
- `apps/mobile/app.json` - Métadonnées Expo (versionCode ajouté)
- `apps/mobile/build-apk.ps1` - Script PowerShell automatisé

### Documentation

- `apps/mobile/APK_BUILD.md` - Guide complet de build APK
- `apps/mobile/INSTALLATION.md` - Guide d'installation employé
- `apps/mobile/README.md` - Documentation générale

### Outils

- `apps/mobile/tools/generate-apk-qr.html` - Générateur QR code pour distribution

### Application Mobile

- `apps/mobile/App.tsx` - Navigation principale
- `apps/mobile/src/screens/` - Tous les écrans
- `apps/mobile/src/services/` - Services API et sécurité
- `apps/mobile/src/components/` - Composants réutilisables

---

## ✨ Résumé

### Avant

❌ Application mobile existante mais pas de processus de build
❌ Pas de documentation pour générer l'APK
❌ Pas d'automatisation du build
❌ Pas d'outils de distribution

### Après

✅ **Configuration EAS Build** complète
✅ **Script PowerShell automatisé** pour build en 1 commande
✅ **Documentation complète** (APK_BUILD.md)
✅ **Outil de distribution** (QR code generator)
✅ **Processus de mise à jour** documenté
✅ **Guide de dépannage** complet

### Workflow Final

**Build APK en 3 commandes:**

```powershell
cd apps/mobile
npm install -g eas-cli
.\build-apk.ps1 -AutoDetectIP
```

**Distribution en 3 étapes:**

1. Récupérer l'URL de l'APK depuis EAS Build
2. Générer un QR code avec `generate-apk-qr.html`
3. Distribuer le QR code aux employés

**Installation employé:**

1. Scanner le QR code
2. Télécharger l'APK
3. Installer et se connecter

---

## 🎯 Cas d'Usage Types

### Scénario 1: Nouvel Employé

1. **RH** crée le compte et génère un code HR
2. **RH** distribue le QR code APK + code HR
3. **Employé** scanne QR, installe l'app
4. **Employé** entre le code HR → OTP → onboarding complet
5. **Employé** peut pointer via QR code

### Scénario 2: Mise à Jour de l'Application

1. **Admin** modifie `app.json` (version 1.0.1, versionCode 2)
2. **Admin** exécute `.\build-apk.ps1 -AutoDetectIP`
3. **Admin** distribue la nouvelle version
4. **Employés** désinstallent l'ancienne, installent la nouvelle

### Scénario 3: Déploiement Multi-Sites

1. **Admin** build une fois avec URL de production
2. **Admin** génère un QR code unique
3. **RH de chaque site** distribue le même QR code
4. **Tous les employés** installent la même version

---

## 🔗 Ressources

- **Documentation Expo**: https://docs.expo.dev/
- **EAS Build Guide**: https://docs.expo.dev/build/introduction/
- **React Native Docs**: https://reactnative.dev/
- **Guide Chrona complet**: `docs/GUIDE_DEPLOIEMENT.md`

---

🚀 **L'application mobile employé est prête pour la production !**
