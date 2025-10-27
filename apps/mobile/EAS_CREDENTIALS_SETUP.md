# ⚙️ Configuration des Credentials EAS pour Android

Ce guide explique comment configurer les credentials EAS (Android Keystore) nécessaires pour générer des APK signés via GitHub Actions.

## 🎯 Objectif

Configurer un **keystore Android** qui sera utilisé pour signer toutes les APKs. Ce keystore est stocké sur les serveurs Expo et accessible via un `EXPO_TOKEN`.

## 🔄 Flux Actuel

```
Local Machine (Une fois)
    ↓
[1] eas login → Authentification
[2] eas credentials configure → Génération du keystore
[3] Keystore stocké sur Expo servers
    ↓
GitHub Actions (À chaque push de tag)
    ↓
[1] Utilise EXPO_TOKEN du secret GitHub
[2] Récupère le keystore depuis Expo
[3] Signe et génère l'APK
[4] Crée une Release GitHub
```

## 📋 Prérequis

- ✅ Compte Expo (gratuit) - https://expo.dev/signup
- ✅ EAS CLI installé globally (`npm install -g eas-cli`)
- ✅ Node.js 14+ installé
- ✅ EXPO_TOKEN créé (voir section "Obtenir EXPO_TOKEN")

## 🚀 Étapes de Configuration

### Étape 1 : Vérifier EXPO_TOKEN dans GitHub

1. Allez sur https://github.com/suaniafluence/Chrona_Core/settings/secrets/actions
2. Vérifiez que `EXPO_TOKEN` existe ✅

Si absent, vous devez le créer :
1. Allez sur https://expo.dev/settings/tokens
2. Cliquez "Create Token"
3. Copiez le token
4. Ajoutez-le aux GitHub Secrets sous le nom `EXPO_TOKEN`

### Étape 2 : Configurer les Credentials Localement

**Ouvrez PowerShell** dans `apps/mobile/` et exécutez :

```powershell
.\setup-eas-credentials.ps1
```

Le script va :

1. ✅ Vérifier que EAS CLI est installé
2. ✅ Vérifier que vous êtes connecté à Expo
3. ✅ Lancer la configuration interactive des credentials
4. ✅ Générer un nouveau keystore Android
5. ✅ Sauvegarder le keystore sur Expo servers

### Étape 3 : Suivre les Instructions Interactives

Quand le script demande :

```
? What do you want to do?
❯ Generate new keystore
  Reuse existing keystore
```

**Sélectionnez "Generate new keystore"** avec la touche ↓ puis Enter.

Le script va générer un keystore unique pour votre application.

### Étape 4 : Vérifier la Configuration

Après que le script finisse, vérifiez :

```powershell
eas credentials show --platform android
```

Vous devriez voir :

```
Keystore
  Path: .../(keystore.jks)
  Alias: ...
  Key Password: ••••
  Store Password: ••••
```

## ✅ Validation

Une fois configuré, testez avec un build local :

```powershell
cd apps/mobile
eas build --platform android --profile preview
```

Le build devrait :
1. Démarrer sur les serveurs Expo (~15-20 min)
2. Récupérer le keystore
3. Signer l'APK
4. Fournir un lien de téléchargement

## 🔐 Sécurité

### Où est stocké le Keystore ?

- **Local** : Pas stocké sur votre machine (sauf cache EAS)
- **Expo Servers** : Chiffré et sécurisé
- **GitHub** : Utilise EXPO_TOKEN pour l'accès

### Que contient EXPO_TOKEN ?

Le token :
- ✅ Authentifie votre compte Expo
- ✅ Permet l'accès aux credentials
- ❌ Ne contient PAS le keystore lui-même

### Jamais de Secrets dans Git

N'ajoutez **JAMAIS** à git :
- Le keystore
- Les passwords
- Les private keys
- Le EXPO_TOKEN

## 🐛 Dépannage

### Erreur: "Not logged in"

```powershell
eas login
# Ou si vous avez EXPO_TOKEN :
$env:EXPO_TOKEN = 'votre-token'
eas credentials configure --platform android
```

### Erreur: "Keystore already exists"

Si vous voulez reconfigurer :

```powershell
.\setup-eas-credentials.ps1 -Force
```

### Erreur: "Build failed - Invalid credentials"

Les credentials peuvent être périmés. Recréez-les :

```powershell
# Dans apps/mobile
eas credentials configure --platform android --force
```

### Erreur sur GitHub Actions: "Generating keystore not supported"

**C'est normal !** GitHub Actions ne peut pas générer interactif. C'est pour ça que vous configurez localement d'abord.

Une fois configuré localement, GitHub Actions récupère simplement le keystore existant.

## 📚 Ressources

- [EAS Build Documentation](https://docs.expo.dev/build/introduction/)
- [Managing Credentials](https://docs.expo.dev/build/how-eas-build-works/#signing-credentials)
- [EXPO_TOKEN Guide](https://docs.expo.dev/eas-cli/commands/)

## 🔄 Workflow Complet

### 1️⃣ Configuration (Une fois)

```powershell
# 1. Créer un compte Expo
# 2. Créer un EXPO_TOKEN sur https://expo.dev/settings/tokens
# 3. Ajouter EXPO_TOKEN aux GitHub Secrets
# 4. Lancer setup-eas-credentials.ps1
```

### 2️⃣ Build Local (Test)

```powershell
cd apps/mobile
.\build-apk.ps1 -AutoDetectIP
```

### 3️⃣ Build Automatique (CI/CD)

```bash
# Git push avec tag mobile-v*.*.*
git tag -a mobile-v1.0.2 -m "Description"
git push origin mobile-v1.0.2
# GitHub Actions se déclenche et génère l'APK
```

### 4️⃣ Release GitHub

L'APK est automatiquement créée en tant que Release GitHub avec :
- 📥 Lien de téléchargement direct
- 📊 SHA256 checksum
- 📝 Description
- 📲 QR Code pour installation mobile

## ✨ Résumé

| Étape | Quoi | Où | Fréquence |
|-------|------|-----|-----------|
| 1 | Créer compte Expo | https://expo.dev/signup | Une fois |
| 2 | Créer EXPO_TOKEN | https://expo.dev/settings/tokens | Une fois |
| 3 | Ajouter à GitHub | Settings → Secrets → Actions | Une fois |
| 4 | Configurer credentials | `./setup-eas-credentials.ps1` | Une fois |
| 5 | Pousser tag Git | `git push origin mobile-vX.X.X` | À chaque version |

Après l'étape 4, tout est automatique ! 🚀

## 🆘 Support

Si vous avez des problèmes :

1. Vérifiez que vous êtes connecté à Expo : `eas whoami`
2. Vérifiez les credentials : `eas credentials show --platform android`
3. Vérifiez EXPO_TOKEN dans GitHub Secrets
4. Consultez les logs du GitHub Action : Actions tab sur GitHub

---

**Last Updated**: 2025-10-27
**EAS CLI Version**: Latest
**Node Version**: 14+
