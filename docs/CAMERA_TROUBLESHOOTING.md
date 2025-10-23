# Guide de Dépannage: Problèmes d'Affichage Caméra Kiosk

## Problèmes Résolus dans v1.0.1

### 1. Caméra N'Affiche Pas Du Tout

**Symptôme:** Le conteneur du scanner reste vide, pas d'erreur affichée

**Causes Identifiées:**
- Manque de hauteur explicite sur le conteneur `.qr-reader`
- CSS: `pointer-events: none` appliqué aux vidéos, bloquant le feed
- Pas de règles CSS spécifiques pour l'élément `<video>` créé par html5-qrcode
- Conteneur sans dimensions garanties

**Corrections Appliquées:**
```css
/* 1. Conteneur QR reader - hauteur et affichage */
.qr-reader {
  width: 100%;
  max-width: 500px;
  height: 500px;                    /* ← Hauteur explicite */
  aspect-ratio: 1;                  /* ← Ratio carré */
  background-color: #000;           /* ← Fond visible pendant chargement */
  display: flex;                    /* ← Flex pour centrage */
  align-items: center;
  justify-content: center;
  position: relative;               /* ← Contexte d'empilement */
}

/* 2. Élément vidéo - affichage explicite */
.qr-reader video {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;                /* ← Remplir l'espace */
  display: block;
  pointer-events: auto;             /* ← Permettre interaction */
}

/* 3. Canvas html5-qrcode */
.qr-reader canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
```

**Avant / Après:**

| Avant | Après |
|-------|-------|
| Conteneur sans hauteur définie | `height: 500px` + `aspect-ratio: 1` |
| `pointer-events: none` sur `video` | `pointer-events: auto` |
| Pas de règles vidéo spécifiques | Règles vidéo/canvas explicites |
| Pas de fond visible | `background-color: #000` |

---

## Checklist de Diagnostic

### 1. Ouvrir les DevTools (F12)

**Chrome/Edge:**
- Appuyer sur `F12` ou `Ctrl+Shift+I`
- Aller à l'onglet **Console**
- Vérifier pour erreurs (en rouge)

**Firefox:**
- Appuyer sur `F12` ou `Ctrl+Shift+I`
- Aller à l'onglet **Console**

### 2. Vérifier les Logs de l'Initialisation

```javascript
// Les logs devraient afficher:
// QR > Starting scanner initialization...
// QR > Creating Html5Qrcode instance...
// QR > Enumerating cameras...
// QR > Available cameras: [...]
// QR > Starting camera with config: {...}
// QR > Trying candidate: [...]
// QR > Camera started successfully!
```

**Si vous voyez une erreur:**
```
QR > Error initializing scanner: NotAllowedError: Permission denied
```
→ La caméra a été **refusée par le navigateur**. Voir section permissions ci-dessous.

### 3. Inspecter l'Élément DOM

```javascript
// Dans la console DevTools:

// 1. Vérifier que le conteneur existe
document.getElementById('qr-reader')  // Devrait afficher un <div>

// 2. Vérifier les dimensions
const qrEl = document.getElementById('qr-reader')
console.log('Width:', qrEl.offsetWidth)
console.log('Height:', qrEl.offsetHeight)
// Devrait afficher: Width: 500, Height: 500

// 3. Vérifier que le vidéo existe
const video = document.querySelector('#qr-reader video')
console.log('Video element:', video)
console.log('Video src:', video?.src)
console.log('Video readyState:', video?.readyState)  // 4 = HAVE_ENOUGH_DATA
```

### 4. Vérifier les Permissions Caméra

**Chrome/Edge:**
- Ouvrir les **Settings** du navigateur
- Aller à **Privacy and security** → **Camera**
- Vérifier que `localhost:5174` est autorisé

**Firefox:**
- Ouvrir **Preferences** → **Privacy & Security**
- Aller à **Permissions** → **Camera**
- Vérifier que `http://localhost:5174` est autorisé

**Safari (macOS):**
- **System Preferences** → **Security & Privacy** → **Camera**
- Vérifier que Safari est autorisé

---

## Problèmes Courants et Solutions

### Problème 1: "Initialization timeout (10s)"

```
QR > Error initializing scanner: Timeout initialisation caméra (10s)
```

**Causes:**
- Caméra prend plus de 10 secondes à démarrer
- Pas de caméra détectée
- Caméra bloguée/occupée

**Solutions:**

```bash
# 1. Vérifier que la caméra est reconnaissable
# Windows: Vérifier dans Gestionnaire des appareils
# Linux: lsusb | grep Camera
# macOS: System Information → Hardware

# 2. Vérifier les permissions
# Relancer le navigateur ou réinitialiser les permissions

# 3. Vérifier si une autre application utilise la caméra
# Fermer: Zoom, Teams, etc.

# 4. Redémarrer le navigateur
```

### Problème 2: "NotAllowedError: Permission denied"

```
QR > Error initializing scanner: NotAllowedError: Permission denied
```

**Solution - Chrome/Edge:**
```
1. Cliquer sur l'icône de caméra verrouillée (à droite de l'URL)
2. Cliquer sur "Settings"
3. Autoriser la caméra
4. Rafraîchir la page (Ctrl+R)
```

**Solution - Firefox:**
```
1. Une popup devrait apparaître "Allow localhost to access your camera?"
2. Cliquer "Allow"
3. Si déjà refusée:
   - Cliquer l'icône "i" à gauche de l'URL
   - Cliquer "Clear permissions"
   - Rafraîchir la page
```

### Problème 3: Conteneur vide, pas d'erreur visible

**Diagnostic:**
```javascript
// Console:
const qr = document.getElementById('qr-reader')
console.log('Element visible:', qr.offsetHeight > 0)  // Devrait être true
console.log('Display:', window.getComputedStyle(qr).display)  // flex
console.log('Video:', document.querySelector('#qr-reader video'))  // Devrait exister
```

**Solutions:**

**Si `offsetHeight === 0`:**
```css
/* Vérifier QRScanner.css a les dimensions */
.qr-reader {
  height: 500px !important;  /* Ajouter !important si nécessaire */
  min-height: 500px;
}
```

**Si vidéo n'existe pas:**
```javascript
// Vérifier que html5-qrcode démarre bien
// Consulter la section "Vérifier les logs" ci-dessus
```

### Problème 4: Vidéo en noir ou figée

**Cause:** Flux vidéo reçu mais pas d'image

**Solutions:**
```bash
# 1. Vérifier la caméra avec une autre app
# - Ouvrir Skype, Zoom, ou l'app Caméra
# - Si ça fonctionne, c'est un problème de HTML5QRCode

# 2. Vérifier l'accès à /media/getUserMedia()
# Firefox - Console:
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    console.log('Caméra OK:', stream)
    stream.getTracks().forEach(t => t.stop())
  })
  .catch(err => console.error('Erreur caméra:', err))

# 3. Si accès OK mais vidéo figée:
# - Fermer/relancer le navigateur
# - Redémarrer le système
```

### Problème 5: Mode kiosk bloque la caméra

**Symptôme:** Caméra fonctionne en mode normal, mais disparaît en mode kiosk

**Cause:** CSS `pointer-events: none` appliqué aux vidéos

**Solution - Vérifié dans la dernière mise à jour:**
```css
/* ✓ Correct - Vidéo peut être interactive */
.app.kiosk-mode-active video {
  pointer-events: auto;  /* ← Permet l'interaction */
}

/* ✗ Incorrect - Bloque la vidéo */
.app.kiosk-mode-active video {
  pointer-events: none;  /* ← NE PAS FAIRE */
}
```

---

## Mode Test Caméra

Le kiosk inclut un **Mode Test Caméra** pour diagnostiquer les problèmes sans scanner QR:

```bash
# 1. Lancer le kiosk
npm run dev

# 2. Ouvrir http://localhost:5174

# 3. Cliquer sur le bouton "Mode test caméra"

# 4. Vérifier que:
#    - La caméra s'affiche
#    - Le flux vidéo est actif
#    - Vous pouvez voir votre visage/environnement
```

Si la caméra fonctionne en mode test mais pas en mode scan, le problème est dans la logique de scan, pas la caméra elle-même.

---

## Configuration pour Environnements Spécifiques

### HTTPS Requis (Production/Safari)

Safari et certains navigateurs exigent HTTPS pour accéder à la caméra (sauf localhost):

```bash
# Développement: localhost est toléré
http://localhost:5174 ✓

# Production: HTTPS requis
https://kiosk.chrona.com ✓
http://kiosk.chrona.com ✗ (caméra refusée)
```

**Fix pour production:**
```bash
# Générer certificat Let's Encrypt
sudo certbot certonly --standalone -d kiosk.chrona.com

# Configurer Nginx/Apache avec SSL
# Vérifier: https://kiosk.chrona.com → caméra demande permission
```

### Caméra USB en Kiosk Dédié

Si vous utilisez un kiosk dédié (iPad, Android):

**iPad/Safari:**
```
Settings → Privacy → Camera → Safari → Enable
```

**Android/Chrome:**
```
Settings → Apps → Chrome → Permissions → Camera → Allow
```

---

## Ressources Utiles

- **html5-qrcode docs**: https://github.com/mebjas/html5-qrcode
- **MediaDevices.getUserMedia()**: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- **Camera Permissions**: https://developer.mozilla.org/en-US/docs/Web/API/Permissions_API

---

## Checklist Complète de Vérification

- [ ] Caméra détectée par le système (Device Manager / lsusb)
- [ ] Permissions navigateur accordées
- [ ] Pas d'autre app utilisant la caméra
- [ ] DevTools Console sans erreurs
- [ ] Conteneur #qr-reader a offsetHeight > 0
- [ ] Élément `<video>` existe dans le DOM
- [ ] CSS `.qr-reader video { pointer-events: auto }`
- [ ] Mode test caméra fonctionne
- [ ] Logs affichent "Camera started successfully!"
- [ ] HTTPS configuré (production)

---

**Version:** 1.0.1
**Dernière mise à jour:** 23 octobre 2025
**Fixes:** Camera display issues resolved in v1.0.1
