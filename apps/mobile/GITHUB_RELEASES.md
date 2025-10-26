# 🚀 GitHub Releases - Distribution APK Chrona Mobile

Guide complet pour créer et distribuer des APK via GitHub Releases avec build automatique.

---

## 🎯 Avantages de GitHub Releases

### Pourquoi GitHub Releases ?

✅ **Gratuit et Illimité**
- Pas de limite de builds (contrairement à EAS gratuit: 30/mois)
- Hébergement permanent sur GitHub
- Pas de compte Expo requis pour télécharger

✅ **Automatisé avec GitHub Actions**
- Push un tag → APK buildé automatiquement
- Pas besoin de build manuel
- Workflow reproductible

✅ **Traçabilité et Versionning**
- Historique complet des versions
- SHA256 pour vérification d'intégrité
- Notes de release automatiques

✅ **Distribution Facile**
- URL stable et permanente
- Compatible avec QR codes
- Téléchargement direct sans authentification

---

## 🏗️ Configuration Initiale

### Prérequis

1. **Compte Expo** (pour EAS Build)
   - Créer un compte: https://expo.dev/signup

2. **Token Expo**
   - Générer un token: https://expo.dev/accounts/[username]/settings/access-tokens
   - Copier le token pour l'étape suivante

3. **Secret GitHub**
   - Aller dans Settings → Secrets and variables → Actions
   - Créer un secret nommé `EXPO_TOKEN`
   - Coller le token Expo

### Vérifier la Configuration

**1. Workflow GitHub Actions**

Le fichier `.github/workflows/build-mobile-apk.yml` doit exister.

**2. Script de Release**

Le fichier `apps/mobile/create-release.ps1` doit exister.

**3. Configuration EAS**

Le fichier `apps/mobile/eas.json` doit contenir le profil `preview`.

---

## 📦 Créer une Release

### Méthode 1: Script Automatique (Recommandé)

**Une seule commande pour tout faire:**

```powershell
cd apps/mobile

# Créer release version 1.0.0
.\create-release.ps1 -Version 1.0.0 -Push
```

**Le script fait automatiquement:**
1. ✅ Valide le format de version (semver)
2. ✅ Met à jour `app.json` (version + versionCode)
3. ✅ Crée un commit de version
4. ✅ Crée un tag Git `mobile-v1.0.0`
5. ✅ Push vers GitHub (si `-Push`)
6. ✅ Déclenche le workflow GitHub Actions

**Options du script:**

```powershell
# Version obligatoire
.\create-release.ps1 -Version 1.2.3

# Avec message de commit personnalisé
.\create-release.ps1 -Version 1.2.3 -Message "feat: add biometric login"

# Avec push automatique
.\create-release.ps1 -Version 1.2.3 -Push

# Tout combiné
.\create-release.ps1 -Version 1.2.3 -Message "feat: new feature" -Push
```

### Méthode 2: Manuelle (Git)

**Étape 1: Mettre à jour la version**

Éditer `apps/mobile/app.json`:

```json
{
  "expo": {
    "version": "1.0.0",
    "android": {
      "versionCode": 10000
    }
  }
}
```

**Calcul du versionCode:**
```
versionCode = Major * 10000 + Minor * 100 + Patch

Exemples:
1.0.0 → 10000
1.2.3 → 10203
2.5.1 → 20501
```

**Étape 2: Commit et Tag**

```bash
# Commit
git add apps/mobile/app.json
git commit -m "chore(mobile): bump version to 1.0.0"

# Tag
git tag -a mobile-v1.0.0 -m "Release Chrona Mobile v1.0.0"

# Push
git push origin main
git push origin mobile-v1.0.0
```

**Étape 3: GitHub Actions Build**

Le workflow se déclenche automatiquement et:
1. Récupère le code
2. Build l'APK avec EAS (15-20 min)
3. Crée une GitHub Release
4. Upload l'APK comme asset

---

## 🔄 Workflow GitHub Actions

### Déclencheurs

Le workflow se déclenche sur:

**1. Push de Tag**
```bash
git tag mobile-v1.0.0
git push origin mobile-v1.0.0
```

**2. Déclenchement Manuel**

Via l'interface GitHub:
1. Aller sur **Actions**
2. Sélectionner **"Build Mobile APK"**
3. Cliquer **"Run workflow"**
4. Entrer la version et l'URL de l'API
5. Cliquer **"Run workflow"**

### Étapes du Workflow

```
┌─────────────────────────────────────────┐
│ 1. Checkout du code                    │
├─────────────────────────────────────────┤
│ 2. Setup Node.js 18.x                  │
├─────────────────────────────────────────┤
│ 3. Setup EAS CLI avec token            │
├─────────────────────────────────────────┤
│ 4. Installation des dépendances        │
├─────────────────────────────────────────┤
│ 5. Configuration de la version         │
│    - Extrait version du tag            │
│    - Met à jour app.json               │
│    - Calcule versionCode               │
├─────────────────────────────────────────┤
│ 6. Configuration de l'URL API          │
│    - Met à jour eas.json               │
├─────────────────────────────────────────┤
│ 7. Build APK avec EAS (15-20 min)      │
│    - Lance le build cloud              │
│    - Attend la fin du build            │
│    - Récupère l'URL de téléchargement  │
├─────────────────────────────────────────┤
│ 8. Téléchargement de l'APK             │
│    - Download depuis Expo              │
│    - Renommage avec version            │
├─────────────────────────────────────────┤
│ 9. Génération d'infos                  │
│    - Taille du fichier                 │
│    - Checksum SHA256                   │
├─────────────────────────────────────────┤
│ 10. Création de la GitHub Release      │
│     - Titre et description             │
│     - Upload de l'APK                  │
│     - Génération des notes             │
└─────────────────────────────────────────┘
```

### Temps de Build

| Étape | Durée |
|-------|-------|
| Setup (1-4) | ~2 min |
| Configuration (5-6) | ~30 sec |
| **Build EAS (7)** | **15-20 min** |
| Download (8-9) | ~1 min |
| Release (10) | ~30 sec |
| **TOTAL** | **~20-25 min** |

---

## 📥 Télécharger et Distribuer

### URL de Téléchargement

Après le build, l'APK est disponible sur:

```
https://github.com/USER/REPO/releases/download/mobile-vX.Y.Z/chrona-mobile-vX.Y.Z.apk
```

**Exemple concret:**
```
https://github.com/mycompany/chrona/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

### Option 1: QR Code de Distribution

**1. Générer le QR Code**

Ouvrir `apps/mobile/tools/generate-apk-qr.html` dans un navigateur.

**2. Entrer l'URL**

Coller l'URL de la release GitHub:
```
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

**3. Télécharger le QR**

Cliquer sur "Télécharger PNG" et distribuer aux employés.

**4. Les employés scannent**

Scanner avec l'appareil photo → Télécharger → Installer

### Option 2: Email

**Template d'email:**

```
Objet: 📱 Chrona Mobile v1.0.0 - Nouvelle Version

Bonjour,

Une nouvelle version de l'application Chrona Mobile est disponible.

🔗 Téléchargement:
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk

📋 Installation:
1. Cliquer sur le lien ci-dessus
2. Télécharger le fichier APK
3. Ouvrir le fichier sur votre téléphone
4. Autoriser l'installation si demandé
5. Installer l'application

📊 Informations:
- Version: 1.0.0
- Taille: 35 MB
- Compatible: Android 8.0+

🆕 Nouveautés:
- [Liste des fonctionnalités]

❓ Support:
support@chrona.com

---
🤖 Email automatique généré par GitHub Actions
```

### Option 3: Page Web

Créer une page HTML simple:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Télécharger Chrona Mobile</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>📱 Chrona Mobile</h1>

    <h2>Version 1.0.0</h2>

    <a href="https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk"
       download>
        <button style="font-size: 20px; padding: 20px;">
            📥 Télécharger APK (35 MB)
        </button>
    </a>

    <h3>Installation</h3>
    <ol>
        <li>Cliquer sur le bouton ci-dessus</li>
        <li>Ouvrir le fichier téléchargé</li>
        <li>Autoriser l'installation</li>
        <li>Installer</li>
    </ol>

    <h3>Sécurité</h3>
    <p>SHA256: <code>abc123...</code></p>

    <h3>Historique des Versions</h3>
    <ul>
        <li><a href="https://github.com/USER/REPO/releases">Toutes les versions</a></li>
    </ul>
</body>
</html>
```

---

## 🔐 Vérification de Sécurité

### Vérifier le Checksum SHA256

**Sur Windows (PowerShell):**
```powershell
Get-FileHash chrona-mobile-v1.0.0.apk -Algorithm SHA256
```

**Sur Linux/Mac:**
```bash
sha256sum chrona-mobile-v1.0.0.apk
```

**Comparer avec la release:**

Le SHA256 est affiché dans les notes de release sur GitHub.

### Vérifier la Signature APK

```bash
# Avec jarsigner
jarsigner -verify -verbose -certs chrona-mobile-v1.0.0.apk

# Avec apksigner (Android SDK)
apksigner verify --print-certs chrona-mobile-v1.0.0.apk
```

---

## 🔄 Gestion des Versions

### Convention de Versioning (Semver)

**Format:** `MAJOR.MINOR.PATCH`

| Type | Quand incrémenter | Exemple |
|------|------------------|---------|
| **MAJOR** | Changements incompatibles | 1.0.0 → 2.0.0 |
| **MINOR** | Nouvelles fonctionnalités | 1.0.0 → 1.1.0 |
| **PATCH** | Corrections de bugs | 1.0.0 → 1.0.1 |

### Exemples

**Bug fix:**
```powershell
.\create-release.ps1 -Version 1.0.1 -Message "fix: login issue" -Push
```

**Nouvelle fonctionnalité:**
```powershell
.\create-release.ps1 -Version 1.1.0 -Message "feat: biometric auth" -Push
```

**Breaking change:**
```powershell
.\create-release.ps1 -Version 2.0.0 -Message "feat!: new API" -Push
```

### Historique des Versions

Consulter toutes les releases:
```
https://github.com/USER/REPO/releases
```

Télécharger une version spécifique:
```
https://github.com/USER/REPO/releases/download/mobile-v1.0.0/chrona-mobile-v1.0.0.apk
```

---

## 🛠️ Dépannage

### Problème: Workflow ne se déclenche pas

**Causes possibles:**
1. Tag mal formaté (doit être `mobile-vX.Y.Z`)
2. Workflow désactivé
3. Secret `EXPO_TOKEN` manquant

**Solutions:**
```bash
# Vérifier les tags
git tag -l "mobile-v*"

# Vérifier le workflow
# Aller sur GitHub → Actions → Workflows

# Vérifier les secrets
# Settings → Secrets and variables → Actions
```

### Problème: Build EAS échoue

**Causes possibles:**
1. Token Expo invalide/expiré
2. Dépendances incompatibles
3. Erreur de configuration

**Solutions:**
```bash
# Vérifier les logs GitHub Actions
# Actions → Select workflow run → View logs

# Regénérer le token Expo
# https://expo.dev/accounts/[username]/settings/access-tokens

# Mettre à jour le secret GitHub
# Settings → Secrets → EXPO_TOKEN → Update
```

### Problème: APK ne s'installe pas

**Causes possibles:**
1. Sources inconnues pas autorisées
2. Ancienne version installée
3. APK corrompu

**Solutions:**
```bash
# 1. Vérifier le SHA256
Get-FileHash chrona-mobile.apk -Algorithm SHA256

# 2. Télécharger à nouveau
# Supprimer le fichier et re-télécharger

# 3. Désinstaller l'ancienne version
adb uninstall com.chrona.mobile

# 4. Réinstaller
adb install chrona-mobile.apk
```

### Problème: Release créée mais APK manquant

**Cause:**
Le build EAS a échoué après la création du tag.

**Solution:**
```bash
# 1. Supprimer la release incomplète
# GitHub → Releases → Delete release

# 2. Supprimer le tag
git tag -d mobile-v1.0.0
git push origin :refs/tags/mobile-v1.0.0

# 3. Recréer la release
.\create-release.ps1 -Version 1.0.0 -Push
```

---

## 📊 Monitoring

### Suivre les Builds

**1. GitHub Actions**

URL: `https://github.com/USER/REPO/actions`

**2. Notifications**

Configurer les notifications GitHub:
- Settings → Notifications
- Activer "Actions" notifications

**3. Status Badge**

Ajouter un badge dans le README:

```markdown
[![Build Mobile APK](https://github.com/USER/REPO/actions/workflows/build-mobile-apk.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/build-mobile-apk.yml)
```

### Statistiques

**Nombre de téléchargements:**

GitHub fournit des statistiques de téléchargement par release:
- Aller sur Releases
- Voir "Assets" pour chaque version
- Nombre de téléchargements affiché

---

## 🎯 Workflow Complet

### Scénario: Release 1.0.0 → 1.0.1 (Bug Fix)

**1. Développement**
```bash
# Créer une branche
git checkout -b fix/login-issue

# Développer le fix
# ...

# Commit
git commit -m "fix: resolve login timeout issue"

# Merge dans main
git checkout main
git merge fix/login-issue
git push origin main
```

**2. Release**
```powershell
# Créer la release
cd apps/mobile
.\create-release.ps1 -Version 1.0.1 -Message "fix: login timeout" -Push
```

**3. Attendre le Build**
```
⏳ 20-25 minutes
✅ GitHub Actions construit l'APK
✅ Release créée automatiquement
```

**4. Distribution**
```
1. Générer QR code avec nouvelle URL
2. Envoyer email aux utilisateurs
3. Publier sur intranet
```

**5. Installation Utilisateurs**
```
1. Scanner QR / Cliquer lien
2. Télécharger APK
3. Installer (écraser ancienne version)
```

---

## ✨ Résumé

### Avantages GitHub Releases

| Critère | EAS Free | GitHub Releases |
|---------|----------|----------------|
| **Builds/mois** | 30 | Illimité |
| **Hébergement** | 30 jours | Permanent |
| **Coût** | Gratuit | Gratuit |
| **Automatisation** | Manuel | GitHub Actions |
| **URL** | Temporaire | Permanente |
| **Versionning** | Non | Oui (releases) |
| **Téléchargement** | Compte Expo | Public |

### Workflow en 3 Commandes

```powershell
# 1. Développer et commit
git commit -am "feat: new feature"

# 2. Créer release
.\create-release.ps1 -Version 1.1.0 -Push

# 3. Distribuer
# → Générer QR code avec nouvelle URL
```

---

## 📚 Ressources

- **GitHub Actions Docs**: https://docs.github.com/actions
- **GitHub Releases**: https://docs.github.com/repositories/releasing-projects-on-github
- **EAS Build**: https://docs.expo.dev/build/introduction/
- **Semver**: https://semver.org/

---

🚀 **Système de distribution automatique prêt pour la production !**
