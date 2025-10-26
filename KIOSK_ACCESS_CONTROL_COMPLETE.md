# ✅ Système de contrôle d'accès par kiosk - Terminé

## 🎯 Objectif

Permettre de configurer **quels employés peuvent accéder à quels kiosks**, avec 3 modes de contrôle.

## 🔒 Modes de contrôle d'accès

### 1. **PUBLIC** (par défaut)
- ✅ **Tout le monde** peut accéder
- Idéal pour : Entrée principale, zones communes

### 2. **WHITELIST** (Liste blanche)
- ✅ Seuls les utilisateurs **explicitement autorisés** peuvent accéder
- ❌ Tous les autres sont **refusés**
- Idéal pour : Bureau direction, salle serveurs, R&D

### 3. **BLACKLIST** (Liste noire)
- ✅ Tout le monde peut accéder **SAUF** les utilisateurs bloqués
- ❌ Utilisateurs spécifiques sont **refusés**
- Idéal pour : Zones avec exceptions (ex: interdire stagiaires)

## 🏗️ Architecture

### Modèle de données

**Table `kiosks`** - Ajout du champ :
- `access_mode` : `"public"` | `"whitelist"` | `"blacklist"`

**Nouvelle table `kiosk_access`** :
```sql
CREATE TABLE kiosk_access (
    id INT PRIMARY KEY,
    kiosk_id INT REFERENCES kiosks(id),
    user_id INT REFERENCES users(id),
    granted BOOLEAN,                  -- TRUE=autorisé, FALSE=bloqué
    granted_by_admin_id INT REFERENCES users(id),
    granted_at TIMESTAMP,
    expires_at TIMESTAMP NULL,        -- Accès temporaire (optionnel)
    UNIQUE(kiosk_id, user_id)
);
```

### Migration

```bash
cd backend
alembic upgrade head  # Applique 0008_add_kiosk_access_control
```

## 🔐 Validation lors du punch

### Workflow

```
1. Employé scanne QR au kiosk
2. Backend valide le JWT
3. Backend vérifie le device
4. ✨ NOUVEAU: Backend vérifie l'accès au kiosk ✨
   ├─ Mode PUBLIC → OK
   ├─ Mode WHITELIST → Vérifier autorisation
   └─ Mode BLACKLIST → Vérifier non-bloqué
5. SI REFUSÉ → HTTP 403 + Audit log
6. SI AUTORISÉ → Enregistre le punch
```

### Code

```python
# backend/src/services/access_control.py
def check_kiosk_access(user_id, kiosk_id, session):
    """
    Returns: (authorized: bool, reason: str)
    """
    # PUBLIC: tout le monde passe
    # WHITELIST: chercher dans kiosk_access
    # BLACKLIST: rejeter si bloqué
```

Intégré dans `punch.py` :
```python
# Après validation JWT et device
access_ok, reason = check_kiosk_access(user_id, kiosk_id, session)
if not access_ok:
    raise HTTPException(403, f"Accès refusé: {reason}")
```

## 🔧 API Admin

### Endpoints créés

**Consulter les accès**
```http
GET /admin/kiosks/{kiosk_id}/access
Authorization: Bearer <admin_token>

Response:
{
  "kiosk_id": 1,
  "kiosk_name": "Bureau Direction",
  "access_mode": "whitelist",
  "authorized_users": [
    {
      "user_id": 5,
      "email": "jean.dupont@example.com",
      "granted": true,
      "granted_at": "2025-01-15T10:00:00Z",
      "expires_at": null
    }
  ]
}
```

**Changer le mode d'accès**
```http
PATCH /admin/kiosks/{kiosk_id}/access-mode
{
  "access_mode": "whitelist"  // ou "public", "blacklist"
}
```

**Accorder l'accès (pour whitelist)**
```http
POST /admin/kiosks/{kiosk_id}/grant-access
{
  "user_id": 5,
  "expires_at": "2025-12-31T23:59:59Z"  // optionnel
}
```

**Révoquer l'accès**
```http
DELETE /admin/kiosks/{kiosk_id}/revoke-access/{user_id}
```

**Bloquer l'accès (pour blacklist)**
```http
POST /admin/kiosks/{kiosk_id}/block-access
{
  "user_id": 5
}
```

## 📊 Exemples d'usage

### Scénario 1 : Entrée principale (PUBLIC)

```python
# Kiosk "Entrée Principale"
kiosk.access_mode = "public"

# Tous les employés peuvent pointer
# Aucune configuration nécessaire
```

### Scénario 2 : Bureau direction (WHITELIST)

```python
# Kiosk "Bureau Direction"
kiosk.access_mode = "whitelist"

# Accorder l'accès uniquement à :
grant_access(kiosk_id=2, user_id=5)  # Directeur
grant_access(kiosk_id=2, user_id=8)  # Secrétaire

# Tous les autres employés = REFUSÉS
```

### Scénario 3 : Zone commune sauf stagiaires (BLACKLIST)

```python
# Kiosk "Salle de repos"
kiosk.access_mode = "blacklist"

# Bloquer uniquement les stagiaires
block_access(kiosk_id=3, user_id=15)  # Stagiaire 1
block_access(kiosk_id=3, user_id=16)  # Stagiaire 2

# Tous les autres = AUTORISÉS
```

### Scénario 4 : Accès temporaire

```python
# Accès temporaire pour un prestataire
grant_access(
    kiosk_id=2,
    user_id=20,
    expires_at=datetime(2025, 6, 30, 23, 59, 59)
)

# Après le 30 juin 2025 → REFUSÉ automatiquement
```

## 🧪 Tests

```bash
cd backend
pytest tests/test_kiosk_access.py -v
```

**Tests inclus** :
- ✅ Kiosk public autorise tout le monde
- ✅ Kiosk whitelist refuse sans autorisation
- ✅ Kiosk whitelist autorise avec permission
- ✅ Kiosk blacklist autorise par défaut
- ✅ Kiosk blacklist refuse si bloqué
- ✅ Kiosk inactif refuse tout
- ✅ Admin peut changer le mode
- ✅ Admin peut accorder/révoquer accès
- ✅ Non-admin ne peut pas gérer

## 🖥️ Interface Back-office suggérée

### Page de gestion d'un kiosk

```
┌────────────────────────────────────────────────────────┐
│  Kiosk: Bureau Direction                               │
│  Location: Bâtiment A - Étage 2                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Mode d'accès:                                         │
│  ○ Public  ◉ Whitelist  ○ Blacklist                  │
│                                                        │
│  [Enregistrer le mode]                                 │
│                                                        │
├────────────────────────────────────────────────────────┤
│  Utilisateurs autorisés                                │
├────────────────────────────────────────────────────────┤
│  ✅ Jean Dupont (jean@example.com)                    │
│     Accordé le: 15/01/2025                             │
│     Expire le: Jamais                                  │
│     [🗑️ Révoquer]                                      │
├────────────────────────────────────────────────────────┤
│  ✅ Marie Martin (marie@example.com)                  │
│     Accordé le: 20/01/2025                             │
│     Expire le: 30/06/2025                              │
│     [🗑️ Révoquer] [⏰ Prolonger]                        │
├────────────────────────────────────────────────────────┤
│  [➕ Ajouter un utilisateur]                           │
└────────────────────────────────────────────────────────┘
```

### Code React exemple

```typescript
// Get kiosk access list
const response = await fetch(`/admin/kiosks/${kioskId}/access`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Display users
data.authorized_users.forEach(user => {
  console.log(`${user.email}: ${user.granted ? 'Autorisé' : 'Bloqué'}`);
});

// Grant access
await fetch(`/admin/kiosks/${kioskId}/grant-access`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: selectedUserId,
    expires_at: expirationDate  // optionnel
  })
});
```

## 📋 Audit et logs

Tous les refus d'accès sont enregistrés dans `audit_logs` :

```json
{
  "event_type": "punch_access_denied",
  "user_id": 15,
  "kiosk_id": 2,
  "event_data": {
    "reason": "Accès non autorisé pour ce kiosk",
    "jti": "abc123..."
  },
  "ip_address": "192.168.1.50",
  "timestamp": "2025-01-26T15:30:00Z"
}
```

Permet de :
- Détecter les tentatives d'accès non autorisé
- Auditer les refus
- Alerter en cas d'abus

## 🔐 Sécurité

### Protections

✅ **Validation côté backend** : Pas de bypass possible
✅ **Logs d'audit** : Tous les refus tracés
✅ **Accès temporaires** : Expiration automatique
✅ **Admin uniquement** : Seuls les admins gèrent les accès
✅ **Atomic checks** : Validation dans la transaction du punch

### Recommandations

1. **Mode par défaut** : Utiliser PUBLIC pour les zones communes
2. **Principe du moindre privilège** : WHITELIST pour zones sensibles
3. **Audit régulier** : Vérifier les logs de refus
4. **Rotation** : Revoir les accès tous les 6 mois
5. **Expiration** : Utiliser `expires_at` pour accès temporaires

## 📚 Fichiers créés/modifiés

**Backend** :
- `src/models/kiosk_access.py` - Nouveau modèle
- `src/models/kiosk.py` - Ajout `access_mode`
- `src/services/access_control.py` - Service de validation
- `src/routers/kiosk_access_admin.py` - API admin
- `src/routers/punch.py` - Intégration validation
- `src/main.py` - Enregistrement router
- `alembic/versions/0008_add_kiosk_access_control.py` - Migration
- `tests/test_kiosk_access.py` - Tests complets

## ✨ Résumé

**Avant** :
- ❌ Tous les employés peuvent accéder à tous les kiosks

**Après** :
- ✅ Contrôle granulaire par kiosk
- ✅ 3 modes : PUBLIC, WHITELIST, BLACKLIST
- ✅ Accès temporaires avec expiration
- ✅ Gestion admin complète (API + futurs UI)
- ✅ Audit des refus d'accès
- ✅ Tests couvrant tous les scénarios

## 🎯 Cas d'usage types

| Lieu | Mode | Config |
|------|------|--------|
| Entrée principale | PUBLIC | Tous autorisés |
| Bureau direction | WHITELIST | Direction + secrétariat |
| Salle serveurs | WHITELIST | Équipe IT uniquement |
| Cantine | PUBLIC | Tous autorisés |
| Zone RH | WHITELIST | Service RH uniquement |
| Parking | BLACKLIST | Tous sauf stagiaires |
| R&D | WHITELIST | Équipe R&D + direction |

---

🚀 **Le système de contrôle d'accès est prêt pour la production !**
