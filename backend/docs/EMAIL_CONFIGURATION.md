# Email Configuration Guide

Ce guide explique comment configurer l'envoi d'emails pour les codes OTP et notifications dans Chrona.

## Vue d'ensemble

Chrona supporte trois méthodes d'envoi d'emails :

1. **Console** (développement) - Affiche les emails dans la console
2. **SMTP** (production) - Utilise un serveur SMTP (Gmail, Outlook, etc.)
3. **SendGrid** (production) - Utilise l'API SendGrid

## Configuration de base

Toutes les configurations se font via variables d'environnement dans le fichier `.env`.

### Mode Console (Développement)

Parfait pour le développement local - les emails sont affichés dans la console au lieu d'être envoyés.

```bash
EMAIL_PROVIDER=console
EMAIL_FROM_ADDRESS=noreply@chrona.com
EMAIL_FROM_NAME=Chrona - Time Tracking
```

## Configuration SMTP

### Gmail

1. **Activer l'authentification à deux facteurs** sur votre compte Gmail

2. **Générer un mot de passe d'application** :
   - Allez sur https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et "Autre"
   - Nommez-le "Chrona Backend"
   - Copiez le mot de passe généré (16 caractères)

3. **Configuration `.env`** :
```bash
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-application
SMTP_USE_TLS=true

EMAIL_FROM_ADDRESS=votre-email@gmail.com
EMAIL_FROM_NAME=Chrona - Time Tracking
```

### Outlook / Office 365

```bash
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@outlook.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_USE_TLS=true

EMAIL_FROM_ADDRESS=votre-email@outlook.com
EMAIL_FROM_NAME=Chrona - Time Tracking
```

### Serveur SMTP personnalisé

```bash
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.votre-domaine.com
SMTP_PORT=587  # ou 465 pour SSL
SMTP_USERNAME=votre-username
SMTP_PASSWORD=votre-password
SMTP_USE_TLS=true  # false si port 465 avec SSL

EMAIL_FROM_ADDRESS=noreply@votre-domaine.com
EMAIL_FROM_NAME=Chrona - Time Tracking
```

## Configuration SendGrid

SendGrid est recommandé pour la production à grande échelle.

1. **Créer un compte SendGrid** : https://signup.sendgrid.com/

2. **Générer une API Key** :
   - Dashboard → Settings → API Keys
   - Créer "Full Access" API Key
   - Copier la clé (elle ne sera affichée qu'une fois)

3. **Vérifier votre domaine sender** (recommandé) :
   - Dashboard → Settings → Sender Authentication
   - Suivez les instructions pour vérifier votre domaine

4. **Configuration `.env`** :
```bash
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

EMAIL_FROM_ADDRESS=noreply@votre-domaine-verifie.com
EMAIL_FROM_NAME=Chrona - Time Tracking
```

5. **Installer la dépendance SendGrid** :
```bash
pip install sendgrid
```

## Configuration avancée

### Personnaliser le sujet et l'expiration OTP

```bash
OTP_SUBJECT=Votre code de vérification Chrona
OTP_EXPIRY_MINUTES=10
```

### Mode test

Utile pour les tests automatisés - log les emails sans les envoyer :

```bash
EMAIL_TEST_MODE=true
EMAIL_TEST_RECIPIENT=test@example.com  # Optionnel : override recipient
```

## Test de la configuration

### Test via console Python

```python
import asyncio
from src.services.email_service import get_email_service

async def test_email():
    service = get_email_service()
    success = await service.send_otp_email("test@example.com", "123456")
    print(f"Email sent: {success}")

asyncio.run(test_email())
```

### Test via API

1. Créer un code HR (en tant qu'admin) :
```bash
curl -X POST http://localhost:8000/admin/hr-codes \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_email": "employee@example.com",
    "employee_name": "Test User",
    "expires_in_days": 7
  }'
```

2. Initier l'onboarding :
```bash
curl -X POST http://localhost:8000/onboarding/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "hr_code": "EMPL-2025-XXXXX",
    "email": "employee@example.com"
  }'
```

3. Vérifier que l'email OTP a été envoyé (console ou boîte mail)

## Dépannage

### Gmail : "Authentification échouée"

- Vérifiez que l'authentification à deux facteurs est activée
- Utilisez un mot de passe d'application, pas votre mot de passe normal
- Vérifiez que "Accès moins sécurisé" est désactivé (mots de passe d'application sont plus sécurisés)

### SMTP : "Connection timeout"

- Vérifiez le port (587 pour TLS, 465 pour SSL)
- Vérifiez que votre firewall autorise les connexions sortantes
- Essayez avec `SMTP_USE_TLS=false` si port 465

### SendGrid : "403 Forbidden"

- Vérifiez que votre API key est valide
- Vérifiez que `EMAIL_FROM_ADDRESS` est vérifié dans SendGrid
- Vérifiez les permissions de l'API key (Full Access recommandé)

### Les emails vont dans les spams

- Configurez SPF, DKIM et DMARC pour votre domaine
- Utilisez un domaine vérifié (SendGrid Sender Authentication)
- Évitez les mots "spam" dans le contenu
- Utilisez un service de réputation email (SendGrid, etc.)

## Sécurité

⚠️ **Important** :

- **Ne commitez JAMAIS** vos mots de passe SMTP ou API keys dans Git
- Utilisez des variables d'environnement (`.env` est dans `.gitignore`)
- Utilisez des mots de passe d'application pour Gmail (pas votre mot de passe principal)
- Limitez les permissions des API keys au strict nécessaire
- Renouvelez régulièrement vos credentials
- En production, utilisez un gestionnaire de secrets (AWS Secrets Manager, Azure Key Vault, etc.)

## Templates d'email

Les templates sont dans `backend/src/services/email_service.py` :

- `_generate_otp_html()` : Template HTML avec CSS inline
- `_generate_otp_text()` : Template texte brut (fallback)

Pour personnaliser les templates, modifiez ces méthodes.

## Logs

Les logs d'envoi d'email sont dans les logs applicatifs :

```bash
# Voir les logs en temps réel
tail -f logs/chrona-backend.log | grep EMAIL
```

Niveaux de log :
- `INFO` : Email envoyé avec succès
- `ERROR` : Échec d'envoi avec détails

## Production

### Recommandations

1. **Utilisez SendGrid ou AWS SES** pour la production
   - Meilleure délivrabilité
   - Gestion automatique des rebonds
   - Analytics et monitoring

2. **Configurez un domaine dédié** pour les emails
   - `noreply@chrona.votre-entreprise.com`
   - Vérifiez SPF/DKIM/DMARC

3. **Monitoring**
   - Surveillez le taux de délivrabilité
   - Configurez des alertes sur les échecs d'envoi
   - Logs centralisés (Sentry, CloudWatch, etc.)

4. **Limites de débit**
   - Gmail: ~500 emails/jour (compte gratuit)
   - SendGrid: 100 emails/jour (gratuit), illimité (payant)
   - Configurez des retries avec backoff exponentiel

## Support

Pour toute question sur la configuration email, consultez :

- Documentation FastAPI : https://fastapi.tiangolo.com/
- Documentation SendGrid : https://docs.sendgrid.com/
- Gmail App Passwords : https://support.google.com/accounts/answer/185833
