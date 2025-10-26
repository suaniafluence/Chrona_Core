# 💓 Guide - Système de Heartbeat Kiosk

Système de monitoring en temps réel des tablettes kiosk via des pings périodiques au backend.

## 🎯 Objectif

Permettre au backend et au back-office de savoir en temps réel :
- ✅ Quels kiosks sont en ligne
- ✅ Quand un kiosk a envoyé son dernier ping
- ✅ La version de l'app mobile installée
- ✅ Les informations sur le device (modèle, OS)
- ✅ Durée d'inactivité si offline

## 🏗️ Architecture

```
Kiosk Mobile App                Backend                 Back-office
    |                              |                          |
    |--- Heartbeat (every 60s) --->|                          |
    |                              |                          |
    |<-- Response (timestamp) -----|                          |
    |                              |                          |
    |                              |<-- GET /kiosk/all-status |
    |                              |                          |
    |                              |--- Kiosks status list -->|
```

### Données envoyées

**Heartbeat Request** (`POST /kiosk/heartbeat`) :
```json
{
  "app_version": "1.0.0",
  "device_info": "Android/11 - Samsung Galaxy Tab A8"
}
```

**Heartbeat Response** :
```json
{
  "success": true,
  "message": "Heartbeat recorded successfully",
  "kiosk_id": 1,
  "last_heartbeat_at": "2025-10-26T14:30:15.123Z",
  "server_time": "2025-10-26T14:30:15.456Z"
}
```

## ⚙️ Configuration

### Backend

**Champs ajoutés au modèle `Kiosk`** :
- `last_heartbeat_at` (DateTime) : Date du dernier ping reçu
- `app_version` (String) : Version de l'app mobile
- `device_info` (String) : Modèle et OS du device

**Migration Alembic** :
```bash
# Appliquer la migration
cd backend
alembic upgrade head
```

**Endpoints** :
- `POST /kiosk/heartbeat` - Recevoir un heartbeat
- `GET /kiosk/status` - Statut du kiosk authentifié
- `GET /kiosk/all-status` - Statut de tous les kiosks (admin)

### Mobile App

**Service automatique** :
- Démarre automatiquement au lancement de l'app
- Envoie un ping toutes les **60 secondes**
- S'arrête si l'app passe en arrière-plan
- Reprend automatiquement au retour en premier plan

**Configuration** (dans `src/services/heartbeat.ts`) :
```typescript
const HEARTBEAT_INTERVAL = 60000; // 60 secondes
```

## 📊 Statut des kiosks

### Critères d'état en ligne

Un kiosk est considéré **en ligne** si :
- Il a envoyé un heartbeat dans les **5 dernières minutes** (300 secondes)

Un kiosk est considéré **hors ligne** si :
- Aucun heartbeat reçu depuis > 5 minutes
- Ou jamais connecté (`last_heartbeat_at` = null)

### Données de statut

**`KioskStatusResponse`** :
```json
{
  "kiosk_id": 1,
  "kiosk_name": "Kiosk-Entrance",
  "location": "Building A - Main Entrance",
  "is_active": true,
  "last_heartbeat_at": "2025-10-26T14:30:00Z",
  "app_version": "1.0.0",
  "device_info": "Android/11 - Samsung Galaxy Tab A8",
  "is_online": true,
  "offline_duration_seconds": null
}
```

Si hors ligne :
```json
{
  "is_online": false,
  "offline_duration_seconds": 900  // 15 minutes
}
```

## 🖥️ Intégration Back-office

### Endpoint à consommer

```typescript
GET /kiosk/all-status

Response: KioskStatusResponse[]
```

### Exemple de dashboard

```typescript
// Fetch kiosks status
const response = await fetch('http://backend:8000/kiosk/all-status');
const kiosks = await response.json();

// Afficher les kiosks
kiosks.forEach(kiosk => {
  console.log(`${kiosk.kiosk_name}: ${kiosk.is_online ? 'Online' : 'Offline'}`);

  if (!kiosk.is_online && kiosk.offline_duration_seconds) {
    const minutes = Math.floor(kiosk.offline_duration_seconds / 60);
    console.log(`  Offline depuis ${minutes} minutes`);
  }
});
```

### UI suggeré

**Liste des kiosks** :
```
┌────────────────────────────────────────────────────┐
│ Kiosk Entrance         🟢 Online                   │
│ Building A - Main      Version: 1.0.0              │
│ Last ping: Il y a 45s  Android/11 - Samsung Tab   │
├────────────────────────────────────────────────────┤
│ Kiosk Cafeteria        🔴 Offline                  │
│ Building B - Floor 1   Version: 1.0.0              │
│ Last ping: Il y a 15m  Android/10 - Lenovo M10    │
└────────────────────────────────────────────────────┘
```

**Indicateurs** :
- 🟢 Vert : En ligne (< 5 min)
- 🟡 Jaune : Attention (5-10 min)
- 🔴 Rouge : Hors ligne (> 10 min)
- ⚫ Gris : Jamais connecté

## 🔧 Fonctionnement technique

### Mobile App

**Initialisation** (App.tsx) :
```typescript
useEffect(() => {
  // Load config
  await config.loadConfig();

  // Start heartbeat
  const heartbeatService = HeartbeatService.getInstance();
  heartbeatService.start();

  // Cleanup
  return () => {
    heartbeatService.stop();
  };
}, []);
```

**Service de heartbeat** :
```typescript
class HeartbeatService {
  start() {
    // Envoyer immédiatement
    this.sendHeartbeat();

    // Puis toutes les 60s
    this.intervalId = setInterval(() => {
      this.sendHeartbeat();
    }, 60000);
  }

  private async sendHeartbeat() {
    await api.post('/kiosk/heartbeat', {
      app_version: this.appVersion,
      device_info: this.deviceInfo
    });
  }
}
```

**Gestion du cycle de vie** :
- **App active** : Heartbeat actif
- **App en arrière-plan** : Heartbeat en pause
- **App revient au premier plan** : Heartbeat reprend

### Backend

**Endpoint de heartbeat** :
```python
@router.post("/kiosk/heartbeat")
async def send_heartbeat(
    heartbeat: HeartbeatRequest,
    kiosk: Annotated[Kiosk, Depends(get_current_kiosk)],
    session: Session
):
    # Mettre à jour le timestamp
    kiosk.last_heartbeat_at = datetime.utcnow()
    kiosk.app_version = heartbeat.app_version
    kiosk.device_info = heartbeat.device_info

    session.commit()
    return {"success": True, ...}
```

**Calcul du statut** :
```python
def is_kiosk_online(kiosk: Kiosk) -> bool:
    if not kiosk.last_heartbeat_at:
        return False

    elapsed = (datetime.utcnow() - kiosk.last_heartbeat_at).total_seconds()
    return elapsed < 300  # 5 minutes
```

## 📈 Monitoring et alertes

### Métriques à surveiller

1. **Taux de disponibilité**
   - % de kiosks en ligne
   - Objectif : > 95%

2. **Durée d'indisponibilité**
   - Temps moyen hors ligne
   - Objectif : < 10 minutes

3. **Versions de l'app**
   - Distribution des versions
   - Détecter les tablettes non à jour

4. **Fréquence des heartbeats**
   - Vérifier que les pings arrivent bien toutes les 60s
   - Détecter les problèmes réseau

### Alertes recommandées

**Alertes critiques** :
- ⚠️ Kiosk hors ligne > 30 minutes
- ⚠️ Aucun kiosk en ligne
- ⚠️ Taux de disponibilité < 50%

**Alertes warning** :
- 🔔 Kiosk hors ligne > 10 minutes
- 🔔 Version obsolète détectée
- 🔔 Taux de disponibilité < 90%

## 🐛 Dépannage

### Kiosk reste offline malgré l'app ouverte

1. **Vérifier la connexion réseau**
   ```bash
   # Sur la tablette
   curl http://backend:8000/health
   ```

2. **Vérifier les logs de l'app**
   ```
   Heartbeat: Sent successfully
   # ou
   Heartbeat: Network error
   ```

3. **Vérifier la clé API**
   - Tester avec Postman/curl
   ```bash
   curl -X POST http://backend:8000/kiosk/heartbeat \
     -H "X-Kiosk-API-Key: votre-cle" \
     -H "Content-Type: application/json" \
     -d '{"app_version":"1.0.0","device_info":"Test"}'
   ```

### Heartbeats trop fréquents ou trop rares

**Modifier l'intervalle** (`src/services/heartbeat.ts`) :
```typescript
const HEARTBEAT_INTERVAL = 30000;  // 30 secondes au lieu de 60
```

**Modifier le seuil d'offline** (backend) :
```python
# Dans kiosk_heartbeat.py
is_online = time_since_heartbeat < 180  # 3 minutes au lieu de 5
```

### Backend ne reçoit pas les heartbeats

1. Vérifier que le router est enregistré (`main.py`) :
   ```python
   app.include_router(kiosk_heartbeat_router)
   ```

2. Vérifier la migration :
   ```bash
   alembic current  # Doit afficher 0007_add_kiosk_heartbeat
   ```

3. Vérifier l'authentification :
   ```bash
   # Test avec clé API valide
   curl -X POST http://localhost:8000/kiosk/heartbeat \
     -H "X-Kiosk-API-Key: votre-cle" \
     -H "Content-Type: application/json" \
     -d '{"app_version":"1.0.0"}'
   ```

## 🧪 Tests

**Lancer les tests** :
```bash
cd backend
pytest tests/test_heartbeat.py -v
```

**Tests inclus** :
- ✅ Envoi de heartbeat avec succès
- ✅ Heartbeat sans authentification (doit échouer)
- ✅ Heartbeat avec clé API invalide (doit échouer)
- ✅ Statut kiosk en ligne
- ✅ Statut kiosk hors ligne
- ✅ Statut kiosk jamais connecté
- ✅ Liste de tous les kiosks
- ✅ Mise à jour du timestamp à chaque heartbeat

## 📚 Références

- **Code mobile** : `apps/kiosk-mobile/src/services/heartbeat.ts`
- **Code backend** : `backend/src/routers/kiosk_heartbeat.py`
- **Modèle** : `backend/src/models/kiosk.py`
- **Migration** : `backend/alembic/versions/0007_add_kiosk_heartbeat.py`
- **Tests** : `backend/tests/test_heartbeat.py`

---

✨ **Le système de heartbeat est maintenant opérationnel !**
