# Plan directeur pour l'application Chrona

## 1. Vision produit & gouvernance
- **Objectif** : offrir un pointage fiable et sécurisé BYOD grâce à un écosystème mobile–borne–backend totalement maîtrisé.
- **Public** : PME ~25 salariés, sans annuaire LDAP, usage exclusivement en ligne.
- **Gouvernance** : comité projet transverse (Produit, Tech, Sécurité, RH) avec rituels mensuels, reporting conformité (RGPD/CNIL) et pilotage qualité.

## 2. Architecture fonctionnelle & responsabilités
| Domaine | Composants clés | Responsabilités |
| --- | --- | --- |
| Mobile (iOS/Android) | App native ou cross-plateforme, SDK anti-tampering, stockage sécurisé, attestation device | Authentification employé, génération/scan QR, transmission sécurisée |
| Borne kiosque | Tablette verrouillée, application borne dédiée, mode kiosque, anti-USB | Interface scan, vérification présence, remontée temps réel |
| Backend | FastAPI, modules auth, signature JWT, gestion devices, journaux | Vérification QR, gestion nonce/jti, back-office RH (phase ultérieure) |
| Base de données | PostgreSQL chiffrée, tables employees, devices, punches, audit_logs | Persistance, historiques immuables, exports réglementaires |
| Infra | Docker, orchestrateur (Docker Compose/Swarm/K8s), secrets manager, monitoring | Déploiement, observabilité (metrics/logs), CI/CD sécurisée |

## 3. Sécurité & threat model (T1–T8)
1. **T1 — Relecture QR / Replay** : QR éphémère (30 s), nonce & jti single-use, liste noire côté backend.
2. **T2 — Appareil compromis** : attestation hardware, intégrité binaire, stockage clé privée dans enclave, révocation immédiate.
3. **T3 — Interception réseau** : TLS 1.2+, pinning certif mobile, HSTS borne, rotation certificats.
4. **T4 — Vol d’identifiants** : OTP initial, MFA optionnel pour RH, hash PBKDF2/Argon2.
5. **T5 — Compromission borne** : mode kiosque, MDM, verrouillage ports, supervision active.
6. **T6 — Fuite back-end** : segmentation réseau, pare-feu, comptes de service dédiés, audit trail immuable.
7. **T7 — Attaques API** : rate limiting, WAF, validation stricte schemas, tests fuzz.
8. **T8 — Incident interne** : séparation des rôles, 4-eyes sur clés, journaux scellés (WORM/SIEM).

## 4. Flux métier détaillés
### Onboarding niveau B
1. RH émet code d’activation + OTP (canal distinct).
2. Employé installe l’app, saisit code + OTP.
3. Attestation device (API Google SafetyNet/Apple DeviceCheck) → backend.
4. Backend enregistre device, génère clé publique, signature server → confirmation.

### Pointage
1. Borne génère QR JWT (RS256) signé côté backend contenant `employee_id`, `device_id`, `nonce`, `jti`, `exp`.
2. Mobile scanne, ajoute double canal (timestamp + signature locale), renvoie au backend.
3. Backend vérifie : signature, validité nonce/jti, statut borne, device non révoqué, géolocalisation optionnelle.
4. Enregistrement punch + journaux (audit, SIEM). Notification RH en cas d’anomalie.

## 5. Spécifications techniques
- **JWT** : header RS256 + kid, payload (iss, aud, iat, exp<30s, employee_id, device_id, nonce, jti, kiosk_id, attestation_hash). Stockage clé privée dans HSM/KMS.
- **API FastAPI**  
  - `/auth/onboard`, `/auth/device/attest`, `/punch/request`, `/punch/validate`, `/admin/devices`, `/admin/reports`.  
  - AuthN via OAuth2 service-to-service pour borne, tokens courts pour mobile.  
  - Schéma Pydantic, dépendances (rate limit, audit logging).
- **PostgreSQL** : schéma normalisé avec tables `employees`, `devices`, `device_attestations`, `punches`, `nonces`, `audit_logs`, `revoked_devices`, `kiosks`. Colonnes sensibles chiffrées (pgcrypto).
- **Mobile** : frameworks natifs (Swift/Kotlin) ou Flutter/React Native + libs anti-capture (prevent screenshot, root/jailbreak detection).  
- **Borne** : app web embarquée (React/TypeScript) ou native (Android kiosk) avec gestion offline limitée et resynchronisation.

## 6. Monorepo & arborescence
```
chrona/
 ├── apps/
 │   ├── mobile/
 │   ├── kiosk/
 │   └── backoffice/ (phase 5)
 ├── backend/
 │   ├── src/
 │   ├── tests/
 │   └── openapi/
 ├── infra/
 │   ├── docker/
 │   ├── terraform/ (optionnel)
 │   └── helm/
 ├── docs/
 │   ├── specs/
 │   ├── threat-model/
 │   └── rgpd/
 ├── workflows/ (CI GitHub Actions ou GitLab CI)
 └── tools/ (scripts, sbom, e2e)
```

## 7. CI/CD avec preuves
1. **Pre-commit** : linters (ruff/eslint), formatters, secret scan (gitleaks).
2. **Build** : compilation mobile (CI + émulateurs), backend docker multi-stage, kiosk build.
3. **SAST & SBOM** : Semgrep, Dependency Track, CycloneDX artefacts.
4. **Tests** : unitaires (pytest, jest), contract tests, e2e (mobile simulateurs + Playwright).
5. **Sécurité** : scan images (Trivy), signature Notary/KMS, policy OPA.
6. **Déploiement** : staging → production avec approbation manuelle, smoke tests automatisés, monitoring (Prometheus/Grafana, Loki, Sentry).
7. **Preuves** : chaque job publie logs signés, rapports PDF, enregistrement vidéo e2e, exports dashboards.

## 8. Réversibilité & gestion incidents
- **Révocation device** : endpoint `/admin/devices/revoke`, propagation en <5 min, blocage QR.
- **Rotation clés** : KMS + versioning, procédures trimestrielles, double contrôle.
- **Sauvegardes** : snapshots chiffrés PostgreSQL (RPO 15 min), tests de restauration mensuelle.
- **Journaux immuables** : stockage append-only (S3 + Object Lock) + SIEM (Elastic/Chronicle).
- **Plan incidents** : runbook (détection, communication RH/employés, post-mortem), exercices semestriels.

## 9. Roadmap condensée
1. **Phase 1 — Backend fondations (1 sprint)** : schéma DB minimal, endpoints signature, threat model.
2. **Phase 2 — Borne kiosque (1 sprint)** : app kiosk, intégration QR, verrouillage tablette.
3. **Phase 3 — Mobile (2 sprints)** : app employé, onboarding, attestation, bêta interne.
4. **Phase 4 — CI/CD & observabilité (1 sprint)** : pipeline complet, monitoring initial.
5. **Phase 5 — Back-office RH & analytics (continu)** : dashboards, exports, premiers insights IA.

## 10. Livrables & documentation
- Spécifications versionnées (docs/specs), OpenAPI, manuels RH/employés.
- Scripts e2e, rapports sécurité, SBOM, registre RGPD, politique de confidentialité.
- Tableaux de bord (Grafana, Sentry), rapports CNIL (registre traitements, DPIA si nécessaire).

## 11. Stratégie conformité RGPD
- Minimisation données (identité, horaires, device).
- Politique d’information transparente, consentement explicite.
- Processus DSR (accès, rectification, effacement).
- Délégué protection des données impliqué (DPO).
- Revue annuelle, tests de résilience, analyses d’impact.

## 12. Identité de marque & UX
- **Palette** : Bleu nuit (#0D1B2A) dominance, accents cyan (#00AEEF), interfaces claires (#E5E5E5/#FFFFFF).
- **Typo** : Montserrat Bold pour titres, Inter Regular contenu, JetBrains Mono pour chiffres/horaires.
- **Logo** : ‘C’ cadran + point IA, animations lentes pour feedback visuel.
- **Ton** : clarté, sérénité, confiance. Microcopy orientée assistance (ex. “Scannez pour enregistrer votre présence en toute sécurité.”).
- **Accessibilité** : contrastes AA, localisation FR/EN, parcours sans friction.

## 13. Squelette du dépôt implémenté
La structure suivante est matérialisée dans le dépôt avec des fichiers `README.md` descriptifs pour documenter chaque espace de travail :
```
apps/
  mobile/
  kiosk/
  backoffice/
backend/
  src/
  tests/
  openapi/
docs/
  specs/
  threat-model/
  rgpd/
infra/
  docker/
  terraform/
  helm/
tools/
workflows/
```
