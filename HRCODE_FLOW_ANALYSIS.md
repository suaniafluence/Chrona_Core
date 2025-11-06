# Analyse du Flux de Création et Affichage du QR Code HR

## Vue d'ensemble

Ce document décortique le processus complet de création d'un code RH et l'affichage de son QR code, avec tous les appels à la base de données.

---

## 🔄 PROCESSUS COMPLET

### ÉTAPE 1: L'admin crée un code RH (Frontend → Backend → DB)

#### 1.1 Frontend: `HRCodesPage.tsx`
**Fichier:** `apps/backoffice/src/pages/HRCodesPage.tsx`

```typescript
// L'admin remplit le formulaire et clique "Créer le code"
const handleCreateHRCode = async (data: CreateHRCodeRequest) => {
  try {
    await hrCodesAPI.create(data);  // ← Appel API
    await loadHRCodes();            // ← Recharge la liste
    setShowCreateModal(false);
  } catch (err) {
    setError('Erreur lors de la création du code RH');
  }
};
```

**Données envoyées:**
```typescript
{
  employee_email: string;      // Ex: "john@example.com"
  employee_name?: string;      // Ex: "John Doe" (optionnel)
  expires_in_days?: number;    // Ex: 7 (par défaut)
}
```

#### 1.2 API Layer: `api.ts`
**Fichier:** `apps/backoffice/src/lib/api.ts`

```typescript
export const hrCodesAPI = {
  create: async (data: CreateHRCodeRequest): Promise<HRCode> => {
    const res = await api.post<HRCode>('/admin/hr-codes', data);
    return res.data;
  },
};
```

**Endpoint appelé:** `POST /admin/hr-codes`

#### 1.3 Backend Router: `admin.py`
**Fichier:** `backend/src/routers/admin.py` (lignes 604-633)

```python
@router.post("/hr-codes", response_model=HRCodeRead, status_code=status.HTTP_201_CREATED)
async def create_hr_code(
    hr_code_data: HRCodeCreate,
    current_user: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Create a new HR code for employee onboarding (admin only)."""
    from src.services.hr_code_service import HRCodeService

    hr_code = await HRCodeService.create_hr_code(
        session=session,
        employee_email=hr_code_data.employee_email,
        employee_name=hr_code_data.employee_name,
        created_by_admin_id=current_user.id,  # ← ID de l'admin connecté
        expires_in_days=hr_code_data.expires_in_days,
    )

    return HRCodeRead.model_validate(hr_code)
```

**Sécurité:** Nécessite le rôle `admin` (token JWT)

#### 1.4 Service Backend: `hr_code_service.py`
**Fichier:** `backend/src/services/hr_code_service.py` (lignes 36-98)

```python
@staticmethod
async def create_hr_code(
    session: AsyncSession,
    employee_email: str,
    employee_name: Optional[str] = None,
    created_by_admin_id: Optional[int] = None,
    expires_in_days: int = 7,
) -> HRCode:
    """Create a new HR code for employee onboarding."""

    # 🔍 APPEL DB #1: Vérifier si un code valide existe déjà
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(HRCode).where(
            HRCode.employee_email == employee_email,
            HRCode.is_used.is_(False),
            HRCode.expires_at > now,
        )
    )
    existing_code = result.scalar_one_or_none()

    if existing_code:
        return existing_code  # ← Retourne le code existant

    # 🔄 GÉNÉRATION: Créer un code unique (ex: "EMPL-2025-A7K9X")
    max_retries = 5
    for _ in range(max_retries):
        code = HRCodeService.generate_hr_code()  # Ex: "EMPL-2025-A7K9X"

        # 🔍 APPEL DB #2: Vérifier l'unicité du code
        result = await session.execute(
            select(HRCode).where(HRCode.code == code)
        )
        if result.scalar_one_or_none() is None:
            break  # Code unique trouvé
    else:
        raise Exception("Failed to generate unique HR code after retries")

    # 📝 APPEL DB #3: Insérer le nouveau code HR
    expires_at = now + timedelta(days=expires_in_days)
    hr_code = HRCode(
        code=code,
        employee_email=employee_email,
        employee_name=employee_name,
        created_by_admin_id=created_by_admin_id,
        created_at=now,
        expires_at=expires_at,
        is_used=False,
    )
    session.add(hr_code)
    await session.commit()
    await session.refresh(hr_code)

    return hr_code
```

**Table DB:** `hr_codes`

**Colonnes insérées:**
```sql
INSERT INTO hr_codes (
    code,              -- Ex: "EMPL-2025-A7K9X"
    employee_email,    -- Ex: "john@example.com"
    employee_name,     -- Ex: "John Doe"
    created_by_admin_id, -- Ex: 1
    created_at,        -- Ex: "2025-01-06T12:00:00Z"
    expires_at,        -- Ex: "2025-01-13T12:00:00Z" (7 jours plus tard)
    is_used            -- FALSE
) VALUES (?, ?, ?, ?, ?, ?, ?)
```

---

### ÉTAPE 2: L'admin affiche la liste des codes RH (Frontend → Backend → DB)

#### 2.1 Frontend: `HRCodesPage.tsx`
```typescript
const loadHRCodes = async () => {
  setIsLoading(true);
  try {
    const data = await hrCodesAPI.getAll({
      include_used: includeUsed,      // Filtres
      include_expired: includeExpired,
    });
    setHRCodes(data);
  } catch (err) {
    setError('Erreur lors du chargement des codes RH');
  }
};
```

**Endpoint appelé:** `GET /admin/hr-codes?include_used=false&include_expired=false`

#### 2.2 Backend Router: `admin.py`
**Fichier:** `backend/src/routers/admin.py` (lignes 636-670)

```python
@router.get("/hr-codes", response_model=list[HRCodeRead])
async def list_hr_codes(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    include_used: bool = False,
    include_expired: bool = False,
    offset: int = 0,
    limit: int = 50,
):
    """List HR codes with optional filters (admin only)."""
    from src.services.hr_code_service import HRCodeService

    hr_codes = await HRCodeService.list_hr_codes(
        session=session,
        include_used=include_used,
        include_expired=include_expired,
    )

    # Apply pagination
    return [
        HRCodeRead.model_validate(code) for code in hr_codes[offset : offset + limit]
    ]
```

#### 2.3 Service Backend: `hr_code_service.py`
```python
@staticmethod
async def list_hr_codes(
    session: AsyncSession,
    include_used: bool = False,
    include_expired: bool = False,
) -> list[HRCode]:
    """List HR codes with optional filtering."""

    # 🔍 APPEL DB #4: Récupérer les codes HR avec filtres
    query = select(HRCode)

    if not include_used:
        query = query.where(HRCode.is_used.is_(False))

    if not include_expired:
        now = datetime.now(timezone.utc)
        query = query.where(
            (HRCode.expires_at.is_(None)) | (HRCode.expires_at > now)
        )

    result = await session.execute(query.order_by(HRCode.created_at.desc()))
    return list(result.scalars().all())
```

**Requête SQL générée:**
```sql
SELECT * FROM hr_codes
WHERE is_used = FALSE
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY created_at DESC
```

---

### ÉTAPE 3: L'admin clique sur "QR" pour afficher le QR code (Frontend uniquement)

#### 3.1 Frontend: `HRCodesPage.tsx`
```typescript
// Ligne 228: L'admin clique sur le bouton QR
<button
  onClick={() => setSelectedQRCode(code)}
  className="..."
>
  <QrCode className="w-4 h-4" />
  <span>QR</span>
</button>

// Ligne 254: Le modal s'affiche
{selectedQRCode && (
  <HRCodeQRDisplay
    hrCode={selectedQRCode.code}           // Ex: "EMPL-2025-A7K9X"
    employeeEmail={selectedQRCode.employee_email}
    employeeName={selectedQRCode.employee_name}
    expiresAt={selectedQRCode.expires_at}
    onClose={() => setSelectedQRCode(null)}
  />
)}
```

#### 3.2 Composant QR: `HRCodeQRDisplay.tsx`
**Fichier:** `apps/backoffice/src/components/HRCodeQRDisplay.tsx`

```typescript
export default function HRCodeQRDisplay({
  hrCode,        // Ex: "EMPL-2025-A7K9X"
  employeeEmail,
  employeeName,
  expiresAt,
  onClose,
}: HRCodeQRDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 📦 Charge la librairie QRCode depuis CDN
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
    script.async = true;

    script.onload = () => {
      if (containerRef.current && window.QRCode) {
        containerRef.current.innerHTML = '';

        // 🎨 GÉNÈRE LE QR CODE directement dans le navigateur
        new window.QRCode(containerRef.current, {
          text: hrCode,       // ← Texte encodé: "EMPL-2025-A7K9X"
          width: 300,
          height: 300,
          colorDark: '#000000',
          colorLight: '#ffffff',
          correctLevel: window.QRCode.CorrectLevel.H,  // Haute redondance
        });
      }
    };
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [hrCode]);

  // ... Boutons télécharger/imprimer ...
}
```

**⚠️ IMPORTANT:** Le QR code est généré **côté client** (navigateur), il n'y a **AUCUN appel backend** pour afficher le QR code !

---

## 📊 RÉSUMÉ DES APPELS À LA BASE DE DONNÉES

### Création d'un code RH (Étape 1)
1. **SELECT** - Vérifier si un code valide existe déjà pour cet email
2. **SELECT** (x5 max) - Vérifier l'unicité du code généré
3. **INSERT** - Insérer le nouveau code HR dans `hr_codes`
4. **SELECT** - Refresh après insertion (automatic SQLModel)

**Total: 3-7 requêtes DB**

### Affichage de la liste (Étape 2)
1. **SELECT** - Récupérer tous les codes HR avec filtres

**Total: 1 requête DB**

### Affichage du QR code (Étape 3)
**Total: 0 requête DB** (généré côté client)

---

## 🐛 PROBLÈMES POTENTIELS IDENTIFIÉS

### Problème #1: Le QR code encode seulement le code texte
**Ligne 34 de `HRCodeQRDisplay.tsx`:**
```typescript
text: hrCode,  // ← Encode "EMPL-2025-A7K9X"
```

**Conséquence:** L'application mobile doit:
- Scanner le QR code
- Extraire le texte "EMPL-2025-A7K9X"
- L'utiliser pour l'onboarding

**Solution actuelle:** Simple et fonctionnelle ✅

---

### Problème #2: Endpoint `/admin/hr-codes/{hr_code_id}/qr-data` existe mais n'est PAS utilisé

**Backend:** `admin.py` lignes 673-714
```python
@router.get("/hr-codes/{hr_code_id}/qr-data", response_model=HRCodeQRData)
async def get_hr_code_qr_data(
    hr_code_id: int,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Generate QR code data for employee onboarding (admin only)."""

    # 🔍 APPEL DB: Récupérer le code HR
    result = await session.execute(select(HRCode).where(HRCode.id == hr_code_id))
    hr_code = result.scalar_one_or_none()

    if not hr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code RH introuvable",
        )

    # Get API URL from environment (fallback to localhost)
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    return HRCodeQRData(
        api_url=api_url,
        hr_code=hr_code.code,
        employee_email=hr_code.employee_email,
        employee_name=hr_code.employee_name,
    )
```

**Frontend:** Cet endpoint est défini dans `api.ts` mais **jamais appelé**:
```typescript
getQRData: async (hrCodeId: number): Promise<HRCodeQRData> => {
  const res = await api.get<HRCodeQRData>(`/admin/hr-codes/${hrCodeId}/qr-data`);
  return res.data;
},
```

**Conséquence:** Le QR code pourrait encoder des données plus riches (API URL + code + email), mais actuellement encode juste le code.

---

## ✅ FLUX ACTUEL (FONCTIONNEL)

```
Admin Back-Office
    ↓
[1] Créer Code RH
    ↓
Frontend (HRCodesPage.tsx)
    → POST /admin/hr-codes { email, name, expires_in_days }
    ↓
Backend (admin.py)
    → HRCodeService.create_hr_code()
    ↓
Service (hr_code_service.py)
    → SELECT (vérif code existant)
    → SELECT (vérif unicité)
    → INSERT INTO hr_codes
    ↓
Response: HRCode { id, code: "EMPL-2025-A7K9X", ... }
    ↓
Frontend: Affiche dans la table

─────────────────────────────────────

[2] Cliquer bouton "QR"
    ↓
Frontend (HRCodesPage.tsx)
    → setSelectedQRCode(code)  # État local
    ↓
Frontend (HRCodeQRDisplay.tsx)
    → Charge QRCode.js depuis CDN
    → Génère QR avec text="EMPL-2025-A7K9X"
    ↓
Affiche le QR code dans le modal
```

---

## 🔍 TEST MANUEL

Pour tester le flux complet:

```bash
# 1. Backend
cd backend
uvicorn src.main:app --reload

# 2. Frontend
cd apps/backoffice
npm run dev

# 3. Se connecter en admin
# 4. Aller à "Codes RH"
# 5. Créer un code avec:
#    - Email: test@example.com
#    - Nom: Test User
#    - Expiration: 7 jours
# 6. Cliquer sur le bouton "QR"
# 7. Vérifier que le QR code s'affiche
# 8. Utiliser un scanner QR pour vérifier le contenu
```

**Contenu du QR code attendu:**
```
EMPL-2025-A7K9X
```

---

## 📝 RECOMMANDATIONS

### Option A: Garder le flux actuel (SIMPLE) ✅
- **Avantages:** Simple, pas d'appel API supplémentaire, rapide
- **Inconvénients:** QR code contient uniquement le code texte

### Option B: Utiliser l'endpoint `/qr-data` (RICHE)
- **Avantages:** QR code contient API URL + code + email (JSON)
- **Inconvénients:** Appel API supplémentaire, plus complexe
- **Modification nécessaire:** Appeler `hrCodesAPI.getQRData(hrCode.id)` avant affichage

**Recommandation:** Garder l'option A sauf besoin spécifique de l'app mobile.

---

## 🎯 DIAGNOSTIC

Si l'erreur persiste, vérifier:

1. ✅ TypeScript compile sans erreur
2. ✅ Backend répond à `POST /admin/hr-codes`
3. ✅ Token JWT admin valide
4. ✅ QRCode.js charge depuis CDN
5. ❓ Console navigateur pour erreurs JavaScript
6. ❓ Network tab pour voir la requête HTTP
7. ❓ Backend logs pour voir l'erreur exacte

**Prochaine étape:** Tester l'appel API avec `curl` ou Postman pour isoler le problème.
