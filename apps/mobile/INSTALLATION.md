# 📱 Installation de l'Application Mobile Chrona

Guide d'installation pour Android et iOS

---

## 🎯 Prérequis

- **Téléphone Android** (version 8.0+) ou **iPhone** (iOS 13+)
- **Application Expo Go** installée sur votre téléphone
  - [Expo Go sur Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)
  - [Expo Go sur App Store](https://apps.apple.com/app/expo-go/id982107779)
- **Ordinateur et téléphone sur le même réseau WiFi**

---

## 🚀 Installation Rapide

### Étape 1: Installer Expo Go sur votre téléphone

**Android:**
1. Ouvrir Google Play Store
2. Chercher "Expo Go"
3. Installer l'application

**iOS:**
1. Ouvrir App Store
2. Chercher "Expo Go"
3. Installer l'application

### Étape 2: Configurer le backend sur votre PC

Sur votre **ordinateur Windows**, exécutez:

```powershell
# Installer le projet Chrona (si pas déjà fait)
.\setup-dev.ps1

# Configurer l'app mobile
.\setup-mobile.ps1
```

Le script `setup-mobile.ps1`:
- ✅ Détecte automatiquement votre IP WiFi
- ✅ Configure le fichier `.env` avec l'URL du backend
- ✅ Affiche les instructions pour configurer le pare-feu

### Étape 3: Configurer le pare-feu Windows

**IMPORTANT**: Ouvrez PowerShell **en tant qu'Administrateur** et exécutez:

```powershell
netsh advfirewall firewall add rule name="Chrona Backend API" dir=in action=allow protocol=TCP localport=8000
```

### Étape 4: Démarrer l'application mobile

Sur votre **ordinateur**, dans le dossier `apps/mobile`:

```bash
cd apps/mobile
npm install    # Première fois seulement
npm start
```

Un **QR code** s'affichera dans le terminal.

### Étape 5: Scanner le QR code

**Android:**
1. Ouvrir **Expo Go**
2. Appuyer sur **"Scan QR Code"**
3. Scanner le QR code affiché dans le terminal

**iOS:**
1. Ouvrir l'app **Caméra**
2. Scanner le QR code
3. Appuyer sur la notification pour ouvrir dans Expo Go

---

## 🧪 Tester la Connexion au Backend

Avant de scanner le QR code, testez que votre téléphone peut accéder au backend:

1. **Trouvez votre IP WiFi** (affichée par `setup-mobile.ps1`)
   - Exemple: `192.168.1.168`

2. **Ouvrez le navigateur de votre téléphone**

3. **Allez sur**: `http://[VOTRE-IP]:8000/health`
   - Exemple: `http://192.168.1.168:8000/health`

4. **Résultat attendu**:
   ```json
   {"status":"ok","db":"ok"}
   ```

**Si ça ne fonctionne pas:**
- ✅ Vérifiez que le pare-feu Windows est configuré (étape 3)
- ✅ Vérifiez que votre PC et téléphone sont sur le même WiFi
- ✅ Redémarrez le backend: `podman compose restart backend`

---

## 📝 Configuration Manuelle (Alternative)

Si le script automatique ne fonctionne pas, créez manuellement `apps/mobile/.env`:

```env
# Remplacez par l'IP de votre ordinateur
EXPO_PUBLIC_API_URL=http://192.168.1.168:8000
EXPO_PUBLIC_ENV=development
```

**Pour trouver votre IP manuellement:**

**Windows:**
```powershell
ipconfig
```
Cherchez "Carte réseau sans fil Wi-Fi" → "Adresse IPv4"

**macOS/Linux:**
```bash
ifconfig | grep "inet "
```

---

## 🔧 Dépannage

### Problème: "Network request failed"

**Solutions:**
1. Vérifiez que le backend est démarré:
   ```bash
   podman ps    # Doit afficher chrona_core-backend-1
   ```

2. Testez depuis le navigateur du téléphone (voir section "Tester la Connexion")

3. Vérifiez le fichier `.env`:
   ```bash
   cat apps/mobile/.env
   ```

4. Redémarrez Expo:
   ```bash
   npm start -- --clear
   ```

### Problème: QR code ne s'affiche pas

**Solution:**
```bash
# Installer les dépendances à nouveau
rm -rf node_modules
npm install
npm start
```

### Problème: "Unable to resolve module"

**Solution:**
```bash
# Nettoyer le cache
npm start -- --clear
```

### Problème: Expo Go ne se connecte pas

**Vérifications:**
1. Téléphone et PC sur le **même WiFi** (pas WiFi invité)
2. Pare-feu Windows **désactivé** OU règle ajoutée (étape 3)
3. Backend **accessible** depuis le téléphone (test navigateur)

---

## 📱 Utilisation de l'Application

Une fois l'app démarrée sur votre téléphone:

### Première Utilisation

1. **Créer un compte** ou **Se connecter**
   - Email: votre adresse email
   - Mot de passe: au moins 8 caractères

2. **Enregistrer votre appareil** (onboarding):
   - Entrer le **code HR** fourni par votre administrateur
   - Valider le **code OTP** reçu par email
   - L'appareil sera lié à votre compte

### Générer un QR Code de Pointage

1. Appuyer sur **"Générer QR Code"**
2. Le QR code s'affiche pendant **30 secondes**
3. Scanner le QR code sur une **tablette kiosk**
4. Confirmation de pointage

### Consulter l'Historique

1. Aller dans **"Historique"**
2. Voir tous vos pointages (entrée/sortie)
3. Pull-to-refresh pour actualiser

---

## 🏗️ Build Production (Optionnel)

Pour créer une version APK/IPA à distribuer:

### Android APK

```bash
npm install -g eas-cli
eas login
eas build --platform android --profile preview
```

### iOS IPA (nécessite compte Apple Developer)

```bash
eas build --platform ios --profile production
```

Les builds seront disponibles sur: https://expo.dev

---

## 📚 Ressources

- [Documentation Expo](https://docs.expo.dev/)
- [Expo Go App](https://expo.dev/client)
- [React Native Documentation](https://reactnative.dev/)
- [Guide complet Chrona](../../docs/GUIDE_DEPLOIEMENT.md)

---

## ✨ Résumé

**Installation en 5 étapes:**
1. ✅ Installer Expo Go sur votre téléphone
2. ✅ Exécuter `.\setup-mobile.ps1` sur PC
3. ✅ Configurer le pare-feu Windows
4. ✅ Démarrer l'app avec `npm start`
5. ✅ Scanner le QR code avec Expo Go

**Durée totale:** ~5 minutes
