# 📡 Architecture Réseau Chrona - PME

## Vue d'ensemble

Ce document décrit l'architecture réseau recommandée pour déployer Chrona dans une PME avec isolation réseau par VLAN, serveurs centralisés, et accès distant pour les employés.

---

## 🏢 Topologie Réseau PME

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTERNET (Sortie)                            │
│                  Passerelle NAT/Routeur Principal                   │
│                    192.168.211.1 (Routeur)                          │
└────────────────┬──────────────────────────────────────────────────┘
                 │
        ┌────────┴────────────────────────────────────────┐
        │                                                 │
   ┌────▼─────────────┐                      ┌──────────▼──────┐
   │ Switch Principal │                      │    Firewall     │
   │  (Manageable)    │◄─────────────────────┤   (Optionnel)   │
   └────┬─────────────┘                      └────────────────┘
        │
    ┌───┴──────────────────────────────────────┐
    │                                          │
┌───▼──────────────────┐        ┌─────────────▼────────┐
│  VLAN 211 (Général)  │        │ VLAN 212 (Chrona)    │
│  Réseau Standard PME │        │ Réseau Dédié Chrona  │
└───┬──────────────────┘        └──────────┬───────────┘
    │                                      │
    │                          ┌───────────┼───────────┐
    │                          │           │           │
    │                  ┌───────▼──┐  ┌────▼────┐  ┌──▼──────┐
    │                  │  Kiosk 1  │  │ Kiosk 2 │  │ Kiosk 3 │
    │                  │ 192.168.  │  │ 192.168.│  │192.168. │
    │                  │ 212.10    │  │ 212.11  │  │ 212.12  │
    │                  └───────────┘  └────────┘  └─────────┘
    │                      (Android)     (Android)  (Android)
    │
    │
    └────────────────────┬────────────────────────┐
                         │                        │
              ┌──────────▼──────────┐   ┌────────▼────────┐
              │   Serveur Chrona    │   │   Serveur Mail  │
              │  (Backend + DB)     │   │  (Optionnel)    │
              │   192.168.211.100   │   │  192.168.211.50 │
              │   (ou 192.168.212?) │   │                 │
              └─────────────────────┘   └─────────────────┘
```

---

## 📊 Détail des VLANs

### **VLAN 211 - Réseau Général (Entreprise)**

| Élément | IP | Description |
|---------|-----|-------------|
| **Routeur/Passerelle** | `192.168.211.1` | Accès à Internet |
| **Serveur Chrona (Backend)** | `192.168.211.100` | Base de données + API |
| **Backoffice Chrona** | `192.168.211.101` | Portail HR/Admin |
| **Serveur Mail** | `192.168.211.50` | Communication entreprise |
| **Ordinateurs de bureau** | `192.168.211.150-200` | Postes de travail |
| **Imprimantes** | `192.168.211.200-250` | Périphériques réseau |
| **Plage DHCP** | `192.168.211.51-149` | Attribution dynamique |

**Masque de sous-réseau** : `255.255.255.0` (/24)
**Capacité** : ~254 appareils

---

### **VLAN 212 - Réseau Chrona (Dédié/Sécurisé)**

| Élément | IP | Description |
|---------|-----|-------------|
| **Passerelle VLAN 212** | `192.168.212.1` | Routeur local VLAN |
| **Serveur Chrona (Alt)** | `192.168.212.100` | Backend alternatif (HA) |
| **Kiosk 1 (Entrée)** | `192.168.212.10` | Point d'accès punch |
| **Kiosk 2 (Atelier)** | `192.168.212.11` | Point d'accès punch |
| **Kiosk 3 (Bureau)** | `192.168.212.12` | Point d'accès punch |
| **Plage DHCP** | `192.168.212.50-149` | Appareils futurs |
| **Plage réservée** | `192.168.212.150-254` | Expansion |

**Masque de sous-réseau** : `255.255.255.0` (/24)
**Capacité** : ~254 appareils
**Isolation** : Accès restreint depuis VLAN 211

---

## 🔗 Routage Inter-VLAN

### Règles de Routage

```
┌─ VLAN 211 (General) ─────────────────────────────────┐
│                                                      │
│  • Accès INTERNET : ✅ OUI (Routeur principal)      │
│  • Accès VLAN 212 : ✅ LIMITÉ (Firewall rules)     │
│  • Accès Kiosks : ✅ OUI (Requêtes API)            │
│                                                      │
└──────────────────────────────────────────────────────┘

┌─ VLAN 212 (Chrona) ──────────────────────────────────┐
│                                                      │
│  • Accès INTERNET : ❌ NON (Direct)                 │
│  • Accès VLAN 211 : ✅ LIMITÉ (Vers backend)       │
│  • Accès Kiosks : ✅ OUI (Local)                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Configuration Firewall Recommandée

```
Rule 1: Allow VLAN 211 → VLAN 212 (Port 8000/backend)
        Source: 192.168.211.0/24
        Dest:   192.168.212.100:8000
        Action: ALLOW

Rule 2: Allow Kiosks → Internet (sortie)
        Source: 192.168.212.0/24
        Dest:   Any
        Port:   80, 443
        Action: ALLOW (via Routeur)

Rule 3: Block Kiosks ← Internet (entrée)
        Source: Any
        Dest:   192.168.212.0/24
        Action: BLOCK (Sauf réponses)

Rule 4: Allow VPN/Remote → Backend
        Source: VPN_Network
        Dest:   192.168.212.100:8000
        Action: ALLOW
```

---

## 📱 Architecture Mobile

### Scénario 1 : Employé sur WiFi Entreprise (VLAN 211)

```
Mobile (WiFi)
   ↓
192.168.211.XXX (DHCP)
   ↓
[App Chrona Mobile]
   ↓ (requête API + QR)
Routeur Firewall
   ↓ (NAT source 192.168.211.1)
   ↓
Serveur Backend
192.168.211.100:8000
   ↓ (réponse JWT + QR)
Mobile (reçoit QR)
```

**Flux** :
1. Mobile obtient une IP via DHCP : `192.168.211.150-200`
2. App Chrona contacte : `http://192.168.211.100:8000` (local)
3. Backend génère JWT signé + QR code
4. Mobile affiche QR (valide 30 secondes)
5. Kiosk scanne → punch enregistré

---

### Scénario 2 : Employé Hors Réseau (4G/LTE)

```
Mobile (4G/LTE)
   ↓
[App Chrona Mobile]
   ↓ (requête API via HTTPS)
Internet (Sortie NAT)
   ↓
Routeur NAT (192.168.211.1)
   ↓
DNS Résolution: chrona.example.com → IP_Publique
   ↓
VPN/Tunnel sécurisé (optionnel)
   ↓
Serveur Backend (Accès sécurisé)
   ↓ (réponse JWT + QR)
Mobile (reçoit QR en 4G)
```

**Flux** :
1. Mobile en 4G (IP publique via opérateur)
2. App contacte : `https://chrona.example.com/api` (DNS public)
3. Requête routée via Internet → Routeur NAT
4. Backend génère JWT + QR
5. Mobile revient au bureau → scanne via WiFi/Kiosk

---

## 🖥️ Serveur Chrona - Options de Placement

### Option A : Serveur sur VLAN 211 (Recommandé pour PME simple)

```
Serveur Chrona
   │
   ├─ IP: 192.168.211.100
   ├─ Backend: http://192.168.211.100:8000
   ├─ DB: PostgreSQL sur port 5432 (Local)
   └─ Accès: Direct depuis VLAN 211 + 212
```

**Avantages** :
- ✅ Configuration simple
- ✅ Accès immédiat depuis VLAN 211
- ✅ Backup local facile

**Inconvénients** :
- ❌ Moins sécurisé (exposed au réseau général)
- ❌ Impact réseau si charge importante

---

### Option B : Serveur sur VLAN 212 (Sécurité accrue)

```
Serveur Chrona
   │
   ├─ IP: 192.168.212.100
   ├─ Backend: http://192.168.212.100:8000
   ├─ DB: PostgreSQL 5432 (Local)
   └─ Accès: Uniquement VLAN 212 (+ Firewall)
```

**Firewall Rule** :
```
Allow 192.168.211.100:* → 192.168.212.100:8000
```

**Avantages** :
- ✅ Isolé sur VLAN Chrona
- ✅ Sécurité renforcée
- ✅ Performance dédiée

**Inconvénients** :
- ❌ Nécessite règles firewall
- ❌ Configuration plus complexe

---

### Option C : Serveur Cloud (Pour croissance/HA)

```
Serveur Chrona (AWS/Azure/OVH)
   │
   ├─ URL: https://chrona.example.com
   ├─ API: :443 (HTTPS)
   ├─ DB: Managed PostgreSQL
   └─ Accès: Internet public (avec authentification)
```

**Avantages** :
- ✅ Scalabilité automatique
- ✅ Haute disponibilité (HA)
- ✅ Sauvegarde automatique
- ✅ Accès depuis n'importe où

**Inconvénients** :
- ❌ Coût mensuel
- ❌ Dépendance Internet
- ❌ Latence réseau

---

## 🔒 Sécurité Réseau

### 1. Authentification API

```
Mobile → Request
   + Header: Authorization: Bearer <JWT>
   + Header: X-Device-ID: <device_fingerprint>
   + TLS 1.2+
   ↓
Backend Validation
   • Signature RS256 valide?
   • Device enregistré?
   • IP whitelist (optionnel)?
   ↓
Réponse: 200 OK + QR
```

### 2. Isolation VLAN

```
┌─────────────────────────────────────────┐
│ VLAN 211 (Général) - Utilisateurs       │
│ • Pouvoirs limités                      │
│ • Pas d'accès SSH/Admin                 │
└─────────────────────────────────────────┘
         ↓ (firewall rules)
         │
┌────────▼────────────────────────────────┐
│ VLAN 212 (Chrona) - Sécurisé             │
│ • Accès restreint                       │
│ • Logs audit activés                    │
│ • Backup régulier                       │
└─────────────────────────────────────────┘
```

### 3. Gestion des Accès Distants

```
Employé à domicile / 4G
         │
         ├─ VPN (OptionL1: OpenVPN/WireGuard)
         │  └─ Tunnel chiffré vers réseau
         │
         ├─ DNS Public (Option L2)
         │  └─ chrona.example.com → IP serveur cloud
         │
         └─ API Direct (Option L3)
            └─ HTTPS avec JWT + Device binding
```

---

## 📊 Flux d'Authentification Complet

### Scénario: Employé punch-in (WiFi + Kiosk)

```
1. MOBILE (WiFi 192.168.211.XXX)
   └─ Ouvre App Chrona
      └─ POST /auth/token (email + password)
         └─ Backend valide credentials
            └─ Retour: JWT access_token (60 min)

2. MOBILE (Demande QR)
   └─ POST /punch/request-token
      Header: Authorization: Bearer <JWT>
      Body: { device_id: 123 }
      └─ Backend génère:
         • Nonce aléatoire
         • JTI unique
         • Expiration: 30 secondes
         • JWT signé RS256
         └─ Retour: QR code string

3. KIOSK (VLAN 212 192.168.212.10)
   └─ Caméra détecte QR
      └─ Extrait JWT string du QR
         └─ POST /punch/validate
            Header: X-Kiosk-API-Key: <api_key>
            Body: { qr_token: <JWT>, kiosk_id: 1 }
            └─ Backend vérifie:
               • Signature RS256 valide?
               • Token non expiré?
               • Nonce unique (lookup table)?
               • JTI pas déjà utilisé?
               • Device enregistré & actif?
               • Kiosk autorisé?
               └─ Atomiquement mark nonce/JTI as used
                  └─ INSERT audit_log
                     └─ INSERT punches
                        └─ Retour: 200 OK + punch_id

4. AUDIT LOG
   ├─ Event: punch_validated
   ├─ User: Jean Dupont
   ├─ Device: Samsung Galaxy A50 (fingerprint: xxx)
   ├─ Kiosk: Kiosk-Entrée (192.168.212.10)
   ├─ Timestamp: 2024-10-24 14:32:15 UTC
   ├─ IP Kiosk: 192.168.212.10
   └─ JWT JTI: abc123def456...
```

---

## 🚀 Déploiement Réseau (Checklist)

### Phase 1 : Infrastructure Réseau

- [ ] Switch VLAN compatible configuré
- [ ] VLAN 211 créé (Général)
- [ ] VLAN 212 créé (Chrona)
- [ ] Routeur inter-VLAN configuré
- [ ] Firewall rules testées
- [ ] Accès Internet vérifié

### Phase 2 : Serveur Chrona

- [ ] Serveur déployé (VLAN 211 ou 212)
- [ ] PostgreSQL en production
- [ ] Certificats TLS (autosigné ou Let's Encrypt)
- [ ] DNS (interne ou public)
- [ ] Backups configurés (quotidiens)
- [ ] Logs centralisés activés

### Phase 3 : Kiosks

- [ ] 3 Kiosks Android déployés
- [ ] Connectés à VLAN 212
- [ ] IPs statiques assignées (ou réservations DHCP)
- [ ] Chrona Kiosk app installée
- [ ] Clés API générées et sauvegardées
- [ ] Démarrage automatique configuré

### Phase 4 : Mobiles Employés

- [ ] Chrona Mobile app distribuée (Play Store/TestFlight)
- [ ] Onboarding employés (device enregistrement)
- [ ] Accès WiFi VLAN 211 configuré
- [ ] VPN optionnel testé (pour accès distants)
- [ ] Support utilisateur planifié

### Phase 5 : Monitoring & Support

- [ ] Logs Chrona centralisés (ex: ELK Stack)
- [ ] Alertes réseau activées
- [ ] Procédure incident documentée
- [ ] Support utilisateur 24/7 (ou heures bureau)
- [ ] Tests mensuels de failover

---

## 📈 Croissance Réseau

### PME Phase 2 (50-100 employés)

```
Options:
1. Ajouter serveur HA en 192.168.212.101
   └─ Réplication BD PostgreSQL
   └─ Load balancer (Traefik)

2. Ajouter VPN pour employés distants
   └─ OpenVPN server sur 192.168.211.1
   └─ Tunnel chiffré + isolation réseau

3. Ajouter kiosks additionnels
   └─ VLAN 212 supporte jusqu'à 254 appareils
   └─ Ajouter 192.168.212.13, .14, .15...

4. Migration Cloud
   └─ Chrona version SaaS sur AWS/Azure
   └─ Synchronisation BD repliquée
```

---

## 🔧 Commandes Configuration Réseau (Cisco/Juniper)

### Configuration VLAN Cisco

```bash
# Switch Cisco IOS

# VLAN 211 (Général)
vlan 211
  name General

# VLAN 212 (Chrona)
vlan 212
  name Chrona

# Interface Trunk (vers Routeur)
interface GigabitEthernet0/1
  switchport mode trunk
  switchport trunk allowed vlan 211,212
  description "Trunk to Router"

# Interface VLAN 211 (Gateway)
interface Vlan211
  ip address 192.168.211.1 255.255.255.0
  no shutdown

# Interface VLAN 212 (Gateway)
interface Vlan212
  ip address 192.168.212.1 255.255.255.0
  no shutdown

# Routage inter-VLAN
ip routing

# Port d'accès VLAN 211 (ordinateurs)
interface range GigabitEthernet0/2-10
  switchport mode access
  switchport access vlan 211

# Port d'accès VLAN 212 (Kiosks)
interface range GigabitEthernet0/11-13
  switchport mode access
  switchport access vlan 212
```

### Configuration ACL Firewall (Accès restreint)

```bash
# ACL 101: Allow VLAN211 → Backend Chrona
access-list 101 permit tcp 192.168.211.0 0.0.0.255 192.168.212.100 eq 8000
access-list 101 deny tcp any any
access-list 101 permit ip any any

# Application sur interface
interface Vlan211
  ip access-group 101 out
```

---

## 📞 Dépannage Réseau Courant

### Problème 1 : Kiosk ne peut pas atteindre Backend

```bash
# Sur Kiosk (192.168.212.10):
ping 192.168.212.100       # Test connectivité L3
curl http://192.168.212.100:8000/health  # Test application

# Si échec:
# 1. Vérifier VLAN routing (ping passerelle 192.168.212.1)
# 2. Vérifier firewall rules
# 3. Vérifier backend status
```

### Problème 2 : Mobile ne peut pas accéder en 4G

```bash
# Vérifier:
1. DNS résolution: chrona.example.com → IP publique
2. Port forwarding: 192.168.211.1:443 → 192.168.211.100:443
3. Certificat TLS valide (éviter self-signed)
4. Logs backend: tail -f /var/log/chrona/api.log
```

### Problème 3 : QR code expire trop vite

```bash
# Backend logs:
grep "token.*expired" /var/log/chrona/api.log

# Solutions:
1. Augmenter TTL: JWT exp += 10 sec (total 40 sec)
2. Vérifier horloge NTP synchronisée (kiosk + backend)
3. Réduire temps d'affichage QR (optimiser app mobile)
```

---

## 📚 Documentation Additionnelle

- **Chrona Architecture** : `docs/ARCHITECTURE.md`
- **Sécurité** : `docs/SECURITY.md`
- **API Reference** : `http://192.168.211.100:8000/docs`
- **Kiosk Setup** : `KIOSK_ANDROID.md`
- **Threat Model** : `docs/threat-model/`

---

**Version** : 1.0
**Dernière mise à jour** : 2024-10-24
**Auteur** : Claude Code
**Statut** : Production Ready
