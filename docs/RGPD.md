# Conformité RGPD – Chrona

Ce document décrit les mesures de conformité RGPD applicables au projet Chrona (système de gestion des temps), ainsi que les procédures opérationnelles pour exercer les droits des personnes concernées et maîtriser les risques.

## 1. Rôles et périmètre
- Responsable de traitement: l’entité cliente qui utilise Chrona pour gérer la présence de ses salariés.
- Sous-traitant: l’équipe hébergeant et opérant Chrona le cas échéant.
- Données concernées: utilisateurs (administrateurs RH, employés), appareils et kiosques, logs d’audit, évènements de pointage (punches).

## 2. Catégories de données et finalités
- Identité: email, rôle, identifiants internes (finalités: authentification, administration RH).
- Terminaux: device_fingerprint, device_name, kiosks (finalités: sécurité, traçabilité, anti-fraude).
- Pointages: date/heure, type (entrée/sortie), liens device/kiosk (finalités: gestion du temps, paie, obligations légales).
- Audit: événements de sécurité (login, révocation, création/suppression), IP/User-Agent (finalités: sécurité, investigation).

Base légale typique: exécution du contrat de travail et respect d’obligations légales (code du travail), intérêt légitime pour la sécurité. Les organisations doivent confirmer ces bases en fonction de leur contexte.

## 3. Durées de conservation
- Comptes utilisateurs: durée de la relation + 2 ans (archivage), puis suppression/anonymisation.
- Appareils/Kiosks: tant que rattachés à un compte/usage actif; purge ≤ 12 mois après révocation.
- Pointages: 5 ans (référence usuelle RH, à valider selon conventions/lois locales), puis anonymisation ou purge.
- Logs d’audit: 12 à 24 mois selon politique sécurité; agrégation/anonymisation au-delà.

Les durées doivent être paramétrées et documentées par l’exploitant; un job de nettoyage périodique est recommandé.

## 4. Droits des personnes (DSR)
Procédures supportées et à mettre en œuvre opérationnellement:
- Accès/Portabilité: export des données d’un employé (JSON/CSV). Backend: `/admin/reports/attendance?user_id=...` (JSON/CSV) et export des métadonnées utilisateur/devices.
- Rectification: via administration RH (modification d’email/nom si stocké), ou par procédure interne.
- Effacement (“droit à l’oubli”): suppression ou anonymisation des pointages et logs associés au salarié (hors obligations légales contraires). Recommandé: anonymiser les identifiants (hash salé) et conserver l’agrégé.
- Limitation/opposition: gel des traitements non nécessaires (désactivation du compte, révocation appareils), documentation dans les logs d’audit.

Points de vigilance: conserver la preuve d’exécution (horodatage, opérateur), tracer dans `audit_logs` les opérations DSR.

## 5. Sécurité et confidentialité
- Authentification: JWT, séparation des rôles, routes admin protégées.
- Traçabilité: `audit_logs` pour les événements sensibles.
- Chiffrement en transit: HTTPS (Traefik en dev/prod), option HSTS côté backend (`ENABLE_HSTS=true`).
- Chiffrement au repos: à implémenter/valider côté base (ex: pgcrypto, chiffrement disque).
- Limitation d’accès: principes du moindre privilège, segmentation réseau (DB non exposée), pare-feu.
- Journalisation des accès et alerting (intégration SIEM optionnelle).

## 6. Transparence (information)
- Notice de confidentialité: fournir aux employés la finalité, base légale, durées, droits et point de contact DPO.
- Documentation interne: ce document + `docs/SECURITY.md`, `docs/GUIDE_DEPLOIEMENT.md` (HTTPS), et `docs/TODO.md` pour les évolutions.

## 7. Registre des traitements (ROPA)
Modèle recommandé (à adapter en interne):
- Responsable, DPO, sous-traitants.
- Catégories de données, finalités, catégories de personnes.
- Destinataires, transferts hors UE (si applicables).
- Durées de conservation.
- Mesures techniques et organisationnelles.

Un gabarit peut être maintenu sous `docs/rgpd/registre.md` (à créer par l’exploitant). 

## 8. DPIA (AIPD)
- Évaluer la nécessité (ex: surveillance systématique, données sensibles). Chrona traite des horaires/présences: le DPIA peut être requis selon le contexte (ampleur, ciblage, technologies).
- Si nécessaire: réaliser et documenter le DPIA (risques, mesures, résiduels).

## 9. Processus opérationnels (exemples)
- Demande d’accès: 
  1) Vérifier identité du demandeur.
  2) Exporter: `/admin/reports/attendance?user_id=...&from=...&to=...&format=json|csv` + métadonnées.
  3) Livrer via canal sécurisé; journaliser l’opération.
- Demande d’effacement: 
  1) Vérifier obligations légales applicables.
  2) Si effacement permis: anonymiser/supprimer pointages + devices révoqués.
  3) Journaliser (audit_logs) et notifier la clôture.
- Révocation d’accès: 
  - Changer rôle/supprimer compte, révoquer appareils/kiosks.

## 10. Évolutions prévues (TODO)
- Exports dédiés DSR utilisateur (bundle JSON/ZIP): endpoint consolidé.
- Tâches de purge automatisée (durées de rétention paramétrées).
- Chiffrement au repos (colonne/volume) et rotation de clés.
- Politique de mots de passe et anti-bruteforce renforcée.
- Registre RGPD versionné dans `docs/rgpd/` et gabarit DPIA.

---

Dernière mise à jour: {à compléter}

