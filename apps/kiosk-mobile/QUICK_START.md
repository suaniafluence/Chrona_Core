# 🚀 Démarrage Rapide - Chrona Kiosk Mobile

Guide ultra-rapide pour tester et déployer l'application kiosk Android.

## ⚡ Test rapide (2 minutes)

### Sur votre téléphone

```bash
# 1. Installer les dépendances
cd apps/kiosk-mobile
npm install

# 2. Démarrer le serveur de développement
npm start
```

1. Scanner le QR code avec **Expo Go** (Android/iOS)
2. Aller dans ⚙️ → Configurer l'IP du backend
3. Tester le scan de QR code

## 📦 Générer l'APK (10 minutes)

### Méthode EAS (recommandée, sans Android Studio)

```bash
# 1. Installer EAS CLI (une seule fois)
npm install -g eas-cli

# 2. Se connecter à Expo
eas login

# 3. Générer l'APK
eas build --platform android --profile preview
```

✅ **Résultat** : Lien de téléchargement de l'APK

## 📲 Installer sur la tablette

1. **Télécharger l'APK** depuis le lien EAS
2. **Transférer sur la tablette** (USB, email, Drive...)
3. **Autoriser les sources inconnues** :
   - Paramètres → Sécurité → Sources inconnues
4. **Installer l'APK**

## ⚙️ Configuration initiale

Au premier lancement :

1. Appuyer sur **⚙️**
2. Configurer :
   - **URL API** : `http://[IP_SERVEUR]:8000`
   - **Kiosk ID** : `1` (ou autre numéro unique)
   - **Clé API** : Fournie par l'admin
   - **Type** : Entrée ou Sortie
3. **Enregistrer**

## ✅ Vérifier

- 🟢 Indicateur de connexion : **Connecté**
- Scanner un QR code de test
- Vérifier le message de validation

## 🆘 Problèmes courants

| Problème | Solution |
|----------|----------|
| ❌ Déconnecté | Vérifier l'IP et que le backend tourne |
| ❌ Caméra bloquée | Autoriser les permissions caméra |
| ❌ QR non reconnu | Vérifier la luminosité, nettoyer caméra |

## 📚 Documentation complète

Voir [README.md](./README.md) pour :
- Build local avec Android Studio
- Configuration avancée
- Mode kiosk Android
- Dépannage détaillé
