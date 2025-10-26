# 📷 Guide - Configuration par QR Code

Configuration ultra-rapide des tablettes kiosk en 2 secondes avec un QR code.

## 🎯 Pourquoi utiliser le QR code ?

| Configuration | Temps | Erreurs | Déploiement masse |
|--------------|-------|---------|-------------------|
| **QR Code** ⭐ | 2 sec | 0% | ✅ Excellent |
| Manuel | 2-3 min | Possible | ❌ Fastidieux |

## 📋 Prérequis

- Backend Chrona déployé et accessible
- Kiosks enregistrés dans le back-office (avec clés API)
- Navigateur web (Chrome, Firefox, Edge...)
- Tablettes avec l'app Chrona Kiosk installée

## 🚀 Étapes

### 1. Générer le QR code (PC)

1. **Ouvrir le générateur** :
   - Double-cliquer sur `apps/kiosk-mobile/tools/generate-config-qr.html`
   - Ou ouvrir dans un navigateur web

2. **Remplir le formulaire** :

   | Champ | Exemple | Requis |
   |-------|---------|--------|
   | URL de l'API | `http://192.168.1.50:8000` | ✅ Oui |
   | ID du Kiosk | `1` | ✅ Oui |
   | Nom du Kiosk | `Kiosk Entrée` | ❌ Non |
   | Clé API | `kiosk-abc123...` | ✅ Oui |
   | Localisation | `Bâtiment A` | ❌ Non |
   | Type de pointage | Entrée ou Sortie | ✅ Oui |

3. **Cliquer sur "Générer le QR Code"**

4. **Résultat** :
   - QR code affiché à l'écran
   - JSON de configuration visible
   - Option de téléchargement PNG

### 2. Scanner sur la tablette

1. **Ouvrir l'app Chrona Kiosk**

2. **Appuyer sur ⚙️** (icône paramètres en haut à droite)

3. **Cliquer sur le bouton bleu** : 📷 **"Scanner un QR de configuration"**

4. **Scanner le QR code** affiché sur votre PC

5. **Vérifier les informations** dans la popup de confirmation

6. **Appuyer sur "Appliquer"**

✅ **Configuration terminée !** L'indicateur de connexion doit passer au vert 🟢

## 📱 Format du QR Code

Le QR code contient un JSON avec cette structure :

```json
{
  "apiBaseUrl": "http://192.168.1.50:8000",
  "kioskId": 1,
  "kioskApiKey": "kiosk-abc123...",
  "kioskName": "Kiosk Entrée",
  "location": "Bâtiment A",
  "punchType": "clock_in"
}
```

**Champs obligatoires** :
- `apiBaseUrl` : URL complète du backend (avec http:// et port)
- `kioskId` : Numéro unique du kiosk
- `kioskApiKey` : Clé d'authentification
- `punchType` : `clock_in` ou `clock_out`

**Champs optionnels** :
- `kioskName` : Nom lisible
- `location` : Emplacement physique

## 💡 Astuces

### Déploiement de plusieurs tablettes

1. **Générer plusieurs QR codes** (un par kiosk)
2. **Télécharger les images PNG** (bouton "Télécharger le QR Code")
3. **Imprimer les QR codes** ou afficher sur plusieurs écrans
4. **Scanner chaque tablette** avec son QR correspondant

### Sauvegarder les configurations

- Les QR codes PNG peuvent être archivés
- Utile pour ré-installer rapidement une tablette
- Stockage sécurisé recommandé (contient la clé API)

### Configuration centralisée

Pour gérer plusieurs kiosks :

```bash
Kiosk 1 → QR Code 1 → chrona-kiosk-config-Entree.png
Kiosk 2 → QR Code 2 → chrona-kiosk-config-Sortie.png
Kiosk 3 → QR Code 3 → chrona-kiosk-config-Cantine.png
```

## 🔒 Sécurité

⚠️ **Le QR code contient la clé API !**

- Ne pas afficher publiquement
- Ne pas partager par email non sécurisé
- Supprimer après installation
- Stockage sécurisé si sauvegarde

## 🐛 Dépannage

### "QR code invalide"

- Vérifier que c'est bien un QR généré par l'outil
- Re-générer le QR code
- Vérifier la luminosité de l'écran

### "Configuration invalide"

- Vérifier que tous les champs requis sont remplis
- Vérifier le format de l'URL (http://...)
- Vérifier que kioskId est un nombre

### La tablette reste déconnectée après scan

- Vérifier que le backend est accessible
- Tester l'URL dans un navigateur : `http://[IP]:8000/health`
- Vérifier le réseau WiFi de la tablette
- Vérifier la clé API dans le back-office

## 🎬 Démo rapide

**Scénario** : Configurer 5 tablettes

```
Temps total : ~10 minutes

1. Générer 5 QR codes (1 min)
2. Télécharger les PNGs (30 sec)
3. Scanner chaque tablette (2 sec × 5 = 10 sec)
4. Vérifier les connexions (1 min)
```

**vs Configuration manuelle** : ~15-20 minutes (3 min × 5)

## 📚 Ressources

- [README.md](./README.md) - Documentation complète
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Guide de déploiement
- [QUICK_START.md](./QUICK_START.md) - Démarrage rapide

---

✨ **Astuce** : Affichez le QR code sur un écran externe ou imprimez-le pour scanner plusieurs tablettes rapidement !
