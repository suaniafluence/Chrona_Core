# Back-office RH Chrona

Portail web d'administration pour le système de gestion des temps Chrona. Interface moderne et responsive pour les administrateurs RH.

## Fonctionnalités

### Authentification
- Login sécurisé avec JWT
- Vérification du rôle administrateur
- Session persistante avec localStorage
- Déconnexion sécurisée

### Tableau de bord
- Vue d'ensemble des statistiques en temps réel
- Graphiques d'activité hebdomadaire (barres et lignes)
- Liste des activités récentes
- Rafraîchissement automatique toutes les 30 secondes
- Cartes de statistiques (utilisateurs, appareils, kiosques, pointages)

### Gestion des utilisateurs
- Liste complète des utilisateurs
- Création de nouveaux utilisateurs (avec rôle)
- Modification du rôle (user ↔ admin)
- Suppression d'utilisateurs
- Affichage des dates de création

### Gestion des appareils
- Liste de tous les appareils enregistrés
- Filtrage par statut (actifs/révoqués)
- Révocation d'appareils compromis
- Affichage des informations de dernier usage
- Indicateur visuel du statut (actif/révoqué)

### Gestion des kiosques
- Vue en grilles des kiosques
- Création de nouveaux kiosques avec génération de clé API
- Activation/désactivation des kiosques
- Affichage de la localisation
- Alerte pour copie sécurisée de la clé API (affichée une seule fois)

### Rapports de présence
- Génération de rapports configurables
- Filtrage par période (date début/fin)
- Filtrage par utilisateur (optionnel)
- Export multi-format:
  - **JSON**: Données structurées pour analyse
  - **CSV**: Compatible Excel/Google Sheets
  - **PDF**: Rapport imprimable
- Informations de conformité RGPD

### Logs d'audit
- Journal immutable de tous les événements
- Filtrage avancé:
  - Par type d'événement
  - Par utilisateur
  - Par période
- Affichage détaillé des métadonnées (IP, user-agent, données JSON)
- Codage couleur par type d'événement
- Vue détaillée expandable

## Technologies

- **React 18** avec TypeScript
- **Vite** pour le build et dev server
- **React Router 6** pour le routing
- **Tailwind CSS** pour le styling
- **Axios** pour les appels API
- **Recharts** pour les graphiques
- **Lucide React** pour les icônes
- **date-fns** pour la gestion des dates

## Installation

```bash
# Installer les dépendances
npm install

# Configurer l'environnement
cp .env.example .env
# Éditer .env pour configurer VITE_API_URL
```

## Configuration

Fichier `.env`:

```env
# Base URL pour le backend Chrona
VITE_API_URL=http://localhost:8000
```

## Développement

```bash
# Lancer le serveur de développement
npm run dev

# L'application sera accessible sur http://localhost:5173
```

Le serveur Vite inclut un proxy qui redirige `/api/*` vers le backend pour éviter les problèmes CORS en développement.

## Build de production

```bash
# Compiler l'application
npm run build

# Prévisualiser le build
npm run preview
```

## Linting et formatage

```bash
# Vérifier le code TypeScript
npm run type-check

# Linter le code
npm run lint
```

## Structure du projet

```
apps/backoffice/
├── src/
│   ├── components/          # Composants réutilisables
│   │   └── ProtectedRoute.tsx
│   ├── contexts/            # Contextes React
│   │   └── AuthContext.tsx
│   ├── layouts/             # Layouts de page
│   │   └── DashboardLayout.tsx
│   ├── lib/                 # Utilitaires et configuration
│   │   └── api.ts          # Client API Axios
│   ├── pages/               # Pages de l'application
│   │   ├── AuditLogsPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── DevicesPage.tsx
│   │   ├── KiosksPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── ReportsPage.tsx
│   │   └── UsersPage.tsx
│   ├── types/               # Définitions TypeScript
│   │   └── index.ts
│   ├── App.tsx              # Composant racine avec routing
│   ├── main.tsx             # Point d'entrée
│   └── index.css            # Styles globaux
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API Backend

Le back-office communique avec les endpoints suivants :

### Auth
- `POST /auth/token` - Login
- `GET /auth/me` - Profil utilisateur

### Admin - Users
- `GET /admin/users` - Liste des utilisateurs
- `POST /admin/users` - Créer un utilisateur
- `PATCH /admin/users/{id}/role` - Modifier le rôle
- `DELETE /admin/users/{id}` - Supprimer un utilisateur

### Admin - Devices
- `GET /admin/devices` - Liste des appareils
- `POST /admin/devices/{id}/revoke` - Révoquer un appareil

### Admin - Kiosks
- `GET /admin/kiosks` - Liste des kiosques
- `POST /admin/kiosks` - Créer un kiosque
- `PATCH /admin/kiosks/{id}` - Modifier un kiosque
- `DELETE /admin/kiosks/{id}` - Supprimer un kiosque

### Admin - Reports & Logs
- `GET /admin/punches` - Historique des pointages
- `GET /admin/audit-logs` - Logs d'audit
- `GET /admin/reports/attendance` - Rapport de présence
- `GET /admin/dashboard/stats` - Statistiques du dashboard

## Sécurité

- Authentification JWT obligatoire
- Vérification du rôle admin sur toutes les pages
- Protection des routes avec `ProtectedRoute`
- Gestion automatique de l'expiration de session (401)
- Pas de stockage de mots de passe côté client
- Clés API kiosque affichées une seule fois

## Conformité RGPD

- Informations de conformité affichées sur la page Rapports
- Conservation recommandée: 5 ans maximum
- Export des données en format machine-readable
- Respect des droits des utilisateurs (accès, rectification, suppression)

## TODO

- [ ] Implémenter endpoint backend `/admin/dashboard/stats`
- [ ] Ajouter la pagination sur les tables
- [ ] Implémenter la recherche textuelle
- [ ] Ajouter des tests unitaires (Vitest)
- [ ] Ajouter des tests E2E (Playwright)
- [ ] Améliorer l'accessibilité (ARIA)
- [ ] Mode sombre
- [ ] Export Excel natif
- [ ] Notifications temps réel (WebSocket)

## Licence

Projet interne - Tous droits réservés
