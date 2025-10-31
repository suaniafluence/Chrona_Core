# Fix Backend Login Issue - Diagnostic et Solution

## Problème identifié

Le backoffice ne peut pas se connecter au backend à cause de configurations manquantes :
1. ❌ Fichier `.env` manquant dans `apps/backoffice/`
2. ❌ Fichier `.env` manquant dans `backend/`
3. ⚠️ Configuration CORS incohérente entre Docker et développement local

## Solutions appliquées

### 1. Configuration du backend
✅ Mis à jour `.env.example` pour inclure les ports 5173 et 5174 dans ALLOWED_ORIGINS

**Action requise** : Créer le fichier .env du backend
```bash
cd /home/user/Chrona_Core/backend
cp .env.example .env
# Puis éditer .env si besoin (par défaut SQLite pour dev local)
```

### 2. Configuration du frontend
**Action requise** : Créer le fichier .env du backoffice
```bash
cd /home/user/Chrona_Core/apps/backoffice
echo "VITE_API_URL=http://localhost:8000" > .env
```

## Étapes de vérification

### 1. Redémarrer le backend
```bash
cd /home/user/Chrona_Core

# Si vous utilisez Docker Compose
docker compose restart backend

# Si vous lancez le backend directement
cd backend
# Arrêter uvicorn (Ctrl+C) puis relancer :
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Redémarrer le frontend backoffice
```bash
cd /home/user/Chrona_Core/apps/backoffice

# Arrêter npm dev (Ctrl+C) puis relancer :
npm run dev
```

### 3. Tester le login via l'interface

Ouvrez votre navigateur et :
1. Accédez à `http://localhost:5173`
2. Ouvrez la console développeur (F12)
3. Essayez de vous connecter avec :
   - Email: `admin@atelier.com`
   - Password: `admin1234`

### 4. Vérifier les logs

**Dans la console du navigateur**, vous devriez voir :
- Les requêtes HTTP vers `http://localhost:8000/auth/token`
- Si erreur CORS : message en rouge mentionnant "CORS" ou "Access-Control-Allow-Origin"
- Si erreur 401 : identifiants incorrects
- Si erreur réseau : le backend n'est pas accessible

**Dans les logs du backend**, vous devriez voir :
```
INFO:     127.0.0.1:XXXXX - "POST /auth/token HTTP/1.1" 200 OK
```

## Diagnostic des erreurs courantes

### Erreur CORS dans la console
```
Access to XMLHttpRequest at 'http://localhost:8000/auth/token' from origin 'http://localhost:5173'
has been blocked by CORS policy
```

**Solution** : Vérifiez que le backend a bien chargé le fichier `.env` :
```bash
cd backend
grep ALLOWED_ORIGINS .env
# Devrait afficher : ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

### Pas de requête dans les logs backend
**Causes possibles** :
1. Le frontend n'envoie pas la requête (erreur JavaScript)
2. Proxy Vite mal configuré
3. Variable `VITE_API_URL` non chargée

**Solution** : Dans la console du navigateur, tapez :
```javascript
localStorage.clear()  // Nettoyer le cache
location.reload()     // Recharger la page
```

### Erreur 401 Unauthorized
**Solution** : Vérifiez que l'utilisateur existe dans la base de données :
```bash
docker compose exec backend python tools/create_admin_user.py \
  --email admin@atelier.com \
  --password admin1234 \
  --role admin
```

### Erreur bcrypt warning
L'erreur suivante est un simple warning, pas un blocage :
```
(trapped) error reading bcrypt version
```
L'utilisateur est bien créé malgré ce message.

## Test manuel via curl

Vérifiez que l'API fonctionne :
```bash
# 1. Login
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@atelier.com&password=admin1234"

# Devrait retourner :
# {"access_token":"eyJ...","token_type":"bearer"}

# 2. Récupérer le token et tester /auth/me
TOKEN="<coller_le_token_ici>"
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Devrait retourner :
# {"id":X,"email":"admin@atelier.com","role":"admin","created_at":"..."}
```

## Checklist finale

- [ ] Le backend a un fichier `.env` avec ALLOWED_ORIGINS incluant port 5173
- [ ] Le backoffice a un fichier `.env` avec VITE_API_URL=http://localhost:8000
- [ ] Le backend est redémarré et écoute sur le port 8000
- [ ] Le backoffice est redémarré et accessible sur http://localhost:5173
- [ ] La console du navigateur ne montre pas d'erreur JavaScript
- [ ] La console du navigateur montre les requêtes vers /auth/token
- [ ] Les logs du backend montrent les requêtes POST /auth/token

## Si le problème persiste

1. **Vérifiez la configuration Vite** :
```bash
cd apps/backoffice
cat vite.config.ts
# Le proxy /api doit pointer vers http://localhost:8000
```

2. **Testez directement l'API depuis le navigateur** :
   - Ouvrez http://localhost:8000/docs
   - Testez l'endpoint `/auth/token` via Swagger UI

3. **Vérifiez les variables d'environnement** :
   - Dans le navigateur, console : `console.log(import.meta.env)`
   - Devrait afficher `VITE_API_URL: "http://localhost:8000"`

## Contact et support

Si le problème persiste après avoir suivi ces étapes, fournissez :
1. Le contenu de la console du navigateur (F12)
2. Les logs du backend (dernières 20 lignes)
3. La sortie de `curl http://localhost:8000/health`
