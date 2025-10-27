# 🚀 Configuration EAS - Démarrage Rapide

## ⏱️ Temps Total : ~5 minutes (+ temps d'attente du build)

### 🎯 Objectif
Configurer un keystore Android pour que GitHub Actions puisse générer des APK signées.

---

## 📋 Checklist Prérequis

- [ ] Vous avez un compte Expo (https://expo.dev) - **GRATUIT**
- [ ] Vous avez un EXPO_TOKEN dans les GitHub Secrets (https://github.com/suaniafluence/Chrona_Core/settings/secrets/actions)
- [ ] PowerShell est ouvert dans `apps/mobile/`

---

## 🔧 Configuration en 3 Étapes

### Étape 1 : Ouvrir PowerShell dans `apps/mobile/`

```powershell
# Dans VS Code ou Terminal:
cd apps/mobile
```

### Étape 2 : Lancer le script de configuration

```powershell
.\setup-eas-credentials.ps1
```

**Ce script va:**
1. ✅ Vérifier que EAS CLI est installé
2. ✅ Vérifier votre authentification Expo
3. ✅ Lancer la configuration interactive
4. ✅ Générer un keystore sécurisé

### Étape 3 : Suivre l'Assistant Interactif

Quand on vous demande :

```
? What do you want to do?
❯ Generate new keystore
  Reuse existing keystore
```

**Appuyez sur Enter** pour sélectionner "Generate new keystore" (première option)

---

## ✅ Vérification

Après que le script finisse, vous devriez voir :

```
✅ Credentials Configurés avec Succès !

Keystore
  Path: .../(keystore.jks)
  Alias: ...
  Key Password: ••••
  Store Password: ••••
```

---

## 🚀 Test du Build (Optionnel)

Si vous voulez tester un build local avant de relancer GitHub Actions :

```powershell
.\build-apk.ps1 -AutoDetectIP
```

Cela va :
1. Détecter automatiquement votre IP locale
2. Lancer un build sur les serveurs Expo (~15-20 min)
3. Générer une APK signée

---

## 🔄 Relancer le Build APK sur GitHub

Une fois les credentials configurés :

```bash
git tag -a mobile-v1.0.3 -m "Build with configured keystore"
git push origin mobile-v1.0.3
```

GitHub Actions va automatiquement :
1. Récupérer les credentials depuis Expo (via EXPO_TOKEN)
2. Générer l'APK
3. Créer une Release GitHub avec l'APK

**Suivez la progression :** https://github.com/suaniafluence/Chrona_Core/actions

---

## ❓ Questions Courantes

### Q: Où sont stockés les credentials ?
**R:** Sur les serveurs Expo, chiffrés et sécurisés. Pas sur votre machine.

### Q: Le script demande une connexion interactive ?
**R:** Oui, c'est normal. Suivez juste les instructions à l'écran.

### Q: Peut-on réutiliser le keystore ?
**R:** Oui ! Une fois configuré, tous les futurs builds l'utiliseront automatiquement.

### Q: Que faire si le script échoue ?
**R:** Consultez `apps/mobile/EAS_CREDENTIALS_SETUP.md` section "🐛 Dépannage"

---

## 📚 Ressources

- 📖 [Guide Complet](apps/mobile/EAS_CREDENTIALS_SETUP.md)
- 📖 [Guide Build APK](apps/mobile/APK_BUILD.md)
- 🔗 [Documentation EAS](https://docs.expo.dev/build/introduction/)

---

## 🎬 Prochaines Étapes

Une fois configuré :

1. ✅ Les builds GitHub Actions vont fonctionner
2. ✅ Vous pourrez pousser des tags pour déclencher des builds
3. ✅ Les APK seront créées automatiquement en tant que Release GitHub

**C'est tout ! 🎉**

---

**Besoin d'aide ?** Consultez le fichier `apps/mobile/EAS_CREDENTIALS_SETUP.md`
