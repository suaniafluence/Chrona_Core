# Chrona Mobile App

Application mobile React Native pour le système de pointage sécurisé Chrona.

## Fonctionnalités

- **Authentification sécurisée** : Login avec email/password et JWT
- **Enregistrement d'appareil** : Enregistrement avec device fingerprint
- **QR Code éphémère** : Génération de QR codes RS256 avec durée de vie de 30 secondes
- **Historique des pointages** : Consultation de l'historique avec pull-to-refresh
- **Sécurité renforcée** : Tokens JWT, device binding, replay protection

## Installation

```bash
cd apps/mobile
npm install
```

## Lancement

```bash
npm start
```

Puis scannez le QR code avec l'app Expo Go ou lancez l'émulateur (a = Android, i = iOS).

## Configuration API

L'API backend est configurée automatiquement :
- **Développement** : `http://10.0.2.2:8000` (Android emulator)
- **Production** : `https://api.chrona.com`

## Flux utilisateur

1. **Login** : Email/password → JWT stocké dans AsyncStorage
2. **Enregistrement appareil** : Device fingerprint envoyé au backend
3. **QR Code** : Génération de token éphémère (30s) avec countdown
4. **Historique** : Liste des pointages avec pull-to-refresh

## Documentation complète

Voir `CLAUDE.md` à la racine du projet pour la documentation technique complète.
