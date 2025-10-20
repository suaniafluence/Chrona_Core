# Chrona Kiosk App

Application React/TypeScript pour les bornes de pointage Chrona. Cette application permet de scanner les QR codes générés par les employés pour enregistrer leurs pointages (clock-in/clock-out).

## 🚀 Fonctionnalités

- ✅ **Scanner QR Code** : Utilise la caméra pour scanner les tokens QR
- ✅ **Mode Kiosk** : Mode plein écran avec interface verrouillée
- ✅ **Feedback Audio/Visuel** : Sons et animations pour chaque scan
- ✅ **Indicateur de Connexion** : Statut en temps réel (online/offline)
- ✅ **Authentification API Key** : Sécurisé par clé API unique
- ✅ **Auto-reprise** : Le scanner redémarre automatiquement après chaque scan

## 📋 Prérequis

- Node.js 18+ et npm
- Backend Chrona en cours d'exécution
- Kiosk enregistré dans le backend avec API key générée

## 🛠️ Installation

### 1. Installer les dépendances

```bash
cd apps/kiosk
npm install
```

### 2. Configuration (`.env`)

Copiez `.env.example` vers `.env` et configurez :

```bash
# URL du backend
VITE_API_URL=http://localhost:8000

# ID du kiosk (obtenu lors de la création du kiosk)
VITE_KIOSK_ID=1

# Type de pointage (clock_in ou clock_out)
VITE_PUNCH_TYPE=clock_in

# API Key du kiosk (générée avec tools/generate_kiosk_api_key.py)
VITE_KIOSK_API_KEY=votre-api-key-ici

# Mode kiosk automatique au démarrage (optionnel)
VITE_AUTO_KIOSK_MODE=false
```

### 3. Générer l'API Key du Kiosk

Depuis le backend :

```bash
cd backend
python -m tools.generate_kiosk_api_key 1
```

Copiez la clé générée dans `VITE_KIOSK_API_KEY`.

## 🚀 Démarrage

### Mode Développement

```bash
npm run dev
```

Accessible sur http://localhost:5174/

### Mode Production

```bash
# Build
npm run build

# Preview
npm run preview
```

## 🖥️ Utilisation

### Mode Normal

1. Ouvrez l'application dans un navigateur
2. Cliquez sur "Enter Kiosk Mode" pour passer en mode kiosk
3. Le scanner QR démarre automatiquement
4. Positionnez le QR code devant la caméra
5. Le pointage est validé automatiquement

### Mode Kiosk Automatique

Configurez `VITE_AUTO_KIOSK_MODE=true` pour :
- Démarrage automatique en plein écran
- Interface verrouillée
- Empêche la navigation hors de l'app

### Sortir du Mode Kiosk

1. Cliquez sur l'icône ⚙️ en haut à droite
2. Confirmez la sortie du mode kiosk
3. L'application revient en mode normal

## 🔧 Configuration Matérielle Recommandée

### Tablette/iPad

- **OS** : Android 8+ ou iPadOS 14+
- **Caméra** : Résolution minimale 720p
- **Écran** : 10 pouces minimum recommandé
- **Support** : Support de tablette avec orientation fixe

### Navigateur

- Chrome/Edge 90+
- Safari 14+ (iOS/macOS)
- Firefox 88+

### Configuration Réseau

- Connexion Wi-Fi stable
- Accès au backend (même réseau local ou VPN)
- Port 8000 accessible pour l'API backend

## 🎨 Interface

### En-tête (Mode Kiosk)
- **Nom du kiosk** : Affiché en haut à gauche
- **Localisation** : Sous le nom du kiosk
- **Statut connexion** : Indicateur online/offline
- **Bouton sortie** : Icône ⚙️ pour quitter le mode kiosk

### Zone de Scan
- Aperçu caméra en temps réel
- Cadre de visée QR code
- Messages d'instructions

### Résultats
- **Succès** : Icône verte + son de confirmation + détails du pointage
- **Erreur** : Icône rouge + son d'erreur + message d'erreur
- Auto-reset après 3 secondes

## 🔒 Sécurité

### Authentification
- Chaque requête inclut le header `X-Kiosk-API-Key`
- API key unique par kiosk
- Validation côté backend

### Tokens QR
- JWT RS256 éphémères (30s d'expiration)
- Nonce anti-replay
- JTI single-use enforcement

### Mode Kiosk
- Plein écran verrouillé
- Navigation bloquée
- Sortie protégée par confirmation

## 📱 Responsive Design

L'application s'adapte automatiquement :
- **Tablette** (recommandé) : Interface optimisée
- **Ordinateur** : Mode développement/test
- **Mobile** : Non recommandé (écran trop petit)

## 🐛 Dépannage

### Le scanner ne démarre pas
- Vérifiez les permissions caméra du navigateur
- Utilisez HTTPS ou localhost (requis pour caméra)
- Testez avec un autre navigateur

### API Key invalide
- Vérifiez que l'API key est correctement configurée dans `.env`
- Régénérez une nouvelle clé si nécessaire
- Vérifiez que le kiosk est actif (`is_active=true`)

### Connexion backend perdue
- Vérifiez que le backend est en cours d'exécution
- Testez l'URL du backend directement (`/health`)
- Vérifiez les paramètres réseau/firewall

### QR codes non reconnus
- Assurez-vous que le token QR n'a pas expiré (30s)
- Vérifiez que le type de pointage correspond (`clock_in`/`clock_out`)
- Testez avec un QR code fraîchement généré

## 📚 Technologies Utilisées

- **React 18** : Framework UI
- **TypeScript 5** : Typage statique
- **Vite 6** : Build tool moderne
- **html5-qrcode** : Scanner QR code
- **Axios** : Client HTTP
- **Web Audio API** : Feedback sonore

## 🔗 Endpoints API Utilisés

- `GET /health` : Vérification connexion backend
- `POST /punch/validate` : Validation QR code et création pointage

## 📄 Licence

© 2025 Chrona - Tous droits réservés

## 👥 Support

Pour toute assistance :
- Consultez la documentation principale (`CLAUDE.md`)
- Vérifiez les logs du navigateur (Console DevTools)
- Contactez l'administrateur système
