# 🎨 Assets Chrona Mobile

Ce dossier contient les assets graphiques pour l'application mobile.

## 📋 Assets Requis

### Icon (icon.png)
- **Taille**: 1024×1024 pixels
- **Format**: PNG avec transparence
- **Usage**: Icône principale de l'application
- **Plateforme**: iOS et Android

### Adaptive Icon (adaptive-icon.png)
- **Taille**: 1024×1024 pixels
- **Format**: PNG avec transparence
- **Zone de sécurité**: Contenu important dans un cercle de 66% du carré
- **Usage**: Icône Android adaptative
- **Plateforme**: Android uniquement

### Splash Screen (splash.png)
- **Taille**: 1242×2436 pixels (ou proportionnelle)
- **Format**: PNG
- **Couleur de fond**: #667eea (définie dans app.json)
- **Usage**: Écran de démarrage
- **Plateforme**: iOS et Android

### Favicon (favicon.png)
- **Taille**: 48×48 pixels minimum
- **Format**: PNG
- **Usage**: Web uniquement
- **Plateforme**: Web

## 🛠️ Génération des Assets

### Méthode Automatique (Recommandé)

Utiliser l'outil Expo pour générer tous les assets depuis un seul fichier:

```bash
# Créer un fichier icon.png de 1024×1024
# Puis générer automatiquement tous les assets
npx expo-asset-generate
```

### Méthode Manuelle

Créer les fichiers avec les dimensions suivantes:

- `icon.png`: 1024×1024
- `adaptive-icon.png`: 1024×1024
- `splash.png`: 1242×2436
- `favicon.png`: 48×48

## 🎨 Design Guidelines

### Icône Principale

**Recommandations:**
- Logo simple et reconnaissable
- Éviter le texte (difficile à lire en petit)
- Utiliser les couleurs de la marque Chrona (#667eea, #764ba2)
- Fond transparent ou couleur unie
- Contraste élevé pour visibilité

**Exemple de concept:**
```
┌─────────────────┐
│                 │
│       ⏰        │  (Icône d'horloge stylisée)
│     CHRONA      │  (Texte optionnel en petit)
│                 │
└─────────────────┘
```

### Adaptive Icon Android

**Zone de sécurité:**
- Le système Android peut masquer jusqu'à 33% des bords
- Placer le contenu important dans un cercle de 66% du carré
- Éviter les détails fins sur les bords

**Masques Android:**
- Cercle
- Carré arrondi
- Squircle
- Autre (selon fabricant)

### Splash Screen

**Recommandations:**
- Logo centré
- Fond dégradé (#667eea → #764ba2)
- Animation légère (optionnel)
- Pas de texte superflu
- Temps d'affichage: < 2 secondes

## 🔧 Configuration dans app.json

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#667eea"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#667eea"
      }
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}
```

## 📐 Templates

### Créer les Assets avec Figma/Photoshop

**1. Icon (1024×1024):**
```
- Canvas: 1024×1024
- Background: Transparent ou #667eea
- Logo: Centré, 70% de la taille
- Export: PNG 24-bit avec transparence
```

**2. Adaptive Icon (1024×1024):**
```
- Canvas: 1024×1024
- Safe Zone: Cercle de 676 pixels (66%)
- Content: Dans le cercle uniquement
- Background: Transparent
- Export: PNG 24-bit avec transparence
```

**3. Splash (1242×2436):**
```
- Canvas: 1242×2436 (ratio iPhone X)
- Background: Gradient #667eea → #764ba2
- Logo: Centré, 30% de la hauteur
- Export: PNG 24-bit
```

## 🎯 Assets par Défaut

Si les fichiers n'existent pas, Expo utilisera des placeholders par défaut.

**Pour créer rapidement des assets temporaires:**

```bash
# Générer des placeholders
npx @expo/image-utils generate-icons --foregroundImage ./your-logo.png
```

## 📚 Ressources

- [Expo Asset Guide](https://docs.expo.dev/guides/app-icons/)
- [Android Adaptive Icons](https://developer.android.com/guide/practices/ui_guidelines/icon_design_adaptive)
- [iOS App Icon Guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Figma Templates](https://www.figma.com/community/file/1234567890/expo-app-assets)

## ✨ Checklist

Avant de builder l'APK, vérifier que tous les assets sont présents:

- [ ] `icon.png` (1024×1024)
- [ ] `adaptive-icon.png` (1024×1024)
- [ ] `splash.png` (1242×2436)
- [ ] `favicon.png` (48×48)
- [ ] Tous les assets sont en PNG
- [ ] Les icônes ont un fond transparent (ou couleur unie)
- [ ] Le logo est visible en petit (tester en 48×48)
- [ ] Les couleurs correspondent à la charte graphique

---

💡 **Astuce**: Utiliser [Canva](https://www.canva.com) ou [Figma](https://www.figma.com) pour créer rapidement des assets professionnels.
