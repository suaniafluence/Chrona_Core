# 🔐 VPN Chrona - Guide Rapide

## Situation Actuelle

✗ **Problème** : Votre réseau `widome_volvic` bloque l'accès direct aux ports 5174/8000 du kiosk
✅ **Solution** : VPN Wireguard pour tunnel sécurisé

---

## 3 Options pour Accéder à Chrona

### Option 1️⃣ : Sans VPN (Si ça marche)

```
Android sur WiFi widome_volvic
    ↓
http://192.168.211.14:5174  (Kiosk)
http://192.168.211.14:8000  (API)
```

**À essayer en premier !** Si ça ne marche pas → passer à Option 2

---

### Option 2️⃣ : VPN Wireguard (Recommandé) ⭐

**Avantages** :
- ✅ Facile à mettre en place (5 minutes)
- ✅ Rapide et sécurisé
- ✅ Meilleure batterie que OpenVPN
- ✅ Android supporté

**Étapes** :

**Étape 1 : Ouvrir PowerShell en tant qu'administrateur**

```powershell
cd C:\Gemini_CLI\Chrona_Core
```

**Étape 2 : Exécuter le script de test**

```powershell
.\setup-vpn-optional.ps1
```

Le script va :
- Tester l'accès direct (5174/8000)
- Si bloqué → proposer VPN Wireguard
- Si OK → dire "pas besoin de VPN"

**Étape 3 : Répondre "oui" si demandé**

```
Voulez-vous configurer un VPN Wireguard? (oui/non)
oui
```

Le script va lancer Wireguard automatiquement.

**Étape 4 : Sur votre Pixel 7**

1. Installer l'app **Wireguard** (Google Play Store)
2. Copier le fichier : `wireguard/peer_android-pixel7/wg0.conf`
3. L'importer dans l'app Wireguard
4. Activer la connexion VPN
5. Ouvrir : `http://192.168.211.14:5174`

---

### Option 3️⃣ : VPN OpenVPN (Alternative)

Si Wireguard ne marche pas, vous pouvez essayer OpenVPN.

Voir : `docs/VPN_SETUP.md` (section "Option 2 : Wireguard")

---

## 🧪 Tester la Connexion VPN

### Sur Android (avec VPN activé)

1. Ouvrir le navigateur
2. Essayer cette URL :

```
http://192.168.211.14:8000/health
```

Vous devriez voir :
```
{"status":"ok","db":"ok"}
```

### Accéder au Kiosk

```
http://192.168.211.14:5174
```

Vous devriez voir l'interface Chrona Kiosk.

---

## ⚙️ Configuration Firewall (Si besoin)

Si VPN se connecte mais ne fonctionne pas, autoriser le port 51820 :

```powershell
# En tant qu'administrateur
netsh advfirewall firewall add rule name="Wireguard VPN" `
  dir=in action=allow protocol=udp localport=51820
```

---

## 🔧 Dépannage Rapide

### VPN refuse de démarrer

```powershell
# Vérifier que Docker est actif
docker --version

# Vérifier que le fichier exists
Test-Path "docker-compose.vpn.yml"

# Lancer manuellement
docker compose -f docker-compose.yml -f docker-compose.vpn.yml up -d wireguard
```

### VPN activé mais Pixel 7 ne se connecte pas

1. Vérifier l'IP du PC : `ipconfig` (rechercher "Wi-Fi")
2. Adapter dans `docker-compose.vpn.yml` : changer `SERVERURL=192.168.211.14` si l'IP change
3. Relancer : `docker compose -f docker-compose.yml -f docker-compose.vpn.yml up -d wireguard`

### Pixel 7 connecté au VPN mais pas d'accès à Chrona

```powershell
# Vérifier que Chrona tourne
docker compose ps

# Vérifier que les ports sont actifs
netstat -ano | findstr ":5174"
netstat -ano | findstr ":8000"
```

---

## 📋 Checklist VPN

- [ ] Télécharger les fichiers VPN (ou `git pull`)
- [ ] Exécuter `setup-vpn-optional.ps1`
- [ ] Choisir "oui" si VPN nécessaire
- [ ] Installer Wireguard sur Pixel 7
- [ ] Importer config VPN
- [ ] Activer connexion VPN
- [ ] Tester : `http://192.168.211.14:8000/health`
- [ ] Accéder au Kiosk : `http://192.168.211.14:5174`

---

## 📞 Besoin d'aide ?

Voir la documentation complète :
- **VPN Détaillée** : `docs/VPN_SETUP.md`
- **Architecture Réseau** : `docs/NETWORK_ARCHITECTURE.md`
- **Kiosk Android** : `KIOSK_ANDROID.md`

---

**Statut** : Prêt à tester 🚀

Si c'est OK → dites-moi "VPN OK" ou "VPN pas OK" et je vous aide ! 📱
