# 🔐 Configuration VPN pour Chrona - Accès Distant

## Problème

Le réseau WiFi `widome_volvic` (192.168.211.0/24) est **isolé** ou **restreint** :
- ❌ Tablettes Android ne peuvent pas accéder au port 5174/8000
- ❌ Pas de sortie Internet directe depuis VLAN 212
- ❌ Besoin d'une sortie sécurisée pour accès distant

## Solution : VPN

Nous allons configurer un **serveur VPN OpenVPN** sur le PC/Serveur Chrona pour :
1. ✅ Tunnel sécurisé depuis Android
2. ✅ Contourner restrictions réseau
3. ✅ Accès aux services Chrona via VPN
4. ✅ Chiffrement bout-à-bout

---

## 🚀 Option 1 : VPN OpenVPN (Recommandé)

### Architecture

```
Android Pixel 7 (4G ou WiFi distant)
    ↓ (Connexion VPN)
OpenVPN Client
    ↓ (Tunnel TLS 1.2)
    ↓ (Chiffré AES-256)
OpenVPN Server (192.168.211.XXX:1194)
    ↓
Chrona Kiosk (localhost:5174)
Chrona Backend (localhost:8000)
```

### Installation OpenVPN sur Windows (PC Chrona)

#### Étape 1 : Télécharger OpenVPN

```powershell
# Option A : Installer via Chocolatey
choco install openvpn -y

# Option B : Télécharger manuel
# https://openvpn.net/community-downloads/
# Télécharger: openvpn-install-2.6.x-I601-amd64.msi
```

#### Étape 2 : Générer les Clés et Certificats

```powershell
# Ouvrir "OpenVPN GUI" → Accéder au répertoire config
# Par défaut: C:\Program Files\OpenVPN\config

cd "C:\Program Files\OpenVPN\easy-rsa"

# Si easy-rsa n'existe pas, initialiser
.\EasyRSA-Start.bat

# Ou manuellement via PowerShell (alternative)
# Créer un script batch pour générer les clés
```

**Créer fichier** `generate-keys.bat` :

```batch
@echo off
cd "C:\Program Files\OpenVPN\easy-rsa"

REM Initialize PKI
.\easyrsa.exe init-pki

REM Build CA
.\easyrsa.exe build-ca nopass

REM Generate server cert
.\easyrsa.exe gen-req server nopass
.\easyrsa.exe sign-req server server

REM Generate client cert
.\easyrsa.exe gen-req client nopass
.\easyrsa.exe sign-req client client

REM Generate DH parameters
.\easyrsa.exe gen-dh

echo Done! Keys generated in pki/ folder
pause
```

**Exécuter** :
```powershell
cd "C:\Program Files\OpenVPN\easy-rsa"
.\generate-keys.bat
```

#### Étape 3 : Créer Configuration Serveur OpenVPN

Créer fichier `C:\Program Files\OpenVPN\config\chrona-vpn.ovpn` :

```
# OpenVPN Server Configuration for Chrona
# Fichier: chrona-vpn.ovpn

port 1194
proto udp
dev tun

ca easy-rsa/pki/ca.crt
cert easy-rsa/pki/issued/server.crt
key easy-rsa/pki/private/server.key
dh easy-rsa/pki/dh.pem

server 10.8.0.0 255.255.255.0

# Push routes to connect to Chrona network
push "route 192.168.211.0 255.255.255.0"
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 8.8.4.4"

keepalive 10 120
cipher AES-256-CBC
auth SHA256
tls-version-min 1.2

comp-lzo
max-clients 20

user nobody
group nogroup

persist-key
persist-tun

status openvpn-status.log
log openvpn.log
verb 3

mute 20
```

#### Étape 4 : Démarrer le Serveur OpenVPN

```powershell
# Via GUI
Start-Process "C:\Program Files\OpenVPN\bin\openvpn-gui.exe"

# Via CLI (Administrator)
cd "C:\Program Files\OpenVPN\bin"
.\openvpn.exe --config "C:\Program Files\OpenVPN\config\chrona-vpn.ovpn"
```

#### Étape 5 : Configurer Client Android

1. **Installer l'app OpenVPN** :
   - Google Play Store : "OpenVPN Connect"
   - https://play.google.com/store/apps/details?id=net.openvpn.openvpn

2. **Exporter le certificat client** :
   ```powershell
   # Sur PC
   # Copier le fichier .crt/.key vers Android
   Copy-Item "C:\Program Files\OpenVPN\easy-rsa\pki\issued\client.crt" `
             -Destination "C:\Users\$env:USERNAME\Downloads\client.crt"
   Copy-Item "C:\Program Files\OpenVPN\easy-rsa\pki\private\client.key" `
             -Destination "C:\Users\$env:USERNAME\Downloads\client.key"
   ```

3. **Créer fichier client** `client.ovpn` :
   ```
   client
   dev tun
   proto udp

   remote 192.168.211.14 1194  # ← IP de votre PC

   resolv-retry infinite
   nobind

   ca ca.crt
   cert client.crt
   key client.key

   cipher AES-256-CBC
   auth SHA256
   tls-version-min 1.2

   verb 3
   mute 20
   ```

4. **Transférer vers Android** :
   - Via USB ou email les fichiers :
     - `client.ovpn`
     - `ca.crt`
     - `client.crt`
     - `client.key`

5. **Importer dans OpenVPN Android** :
   - Ouvrir l'app OpenVPN Connect
   - Menu → Import
   - Sélectionner `client.ovpn`
   - L'app importera aussi les certs référencés

6. **Se connecter** :
   - Cliquer sur le profil "client"
   - Appuyer sur "Connect"
   - Attendre la connexion (statut "Connected")

---

## 🔗 Option 2 : Wireguard (Plus léger et rapide)

**Avantages** :
- ✅ Plus rapide qu'OpenVPN
- ✅ Meilleure batterie sur mobile
- ✅ Configuration plus simple
- ✅ Moderne (2015+)

**Installation** :

```powershell
# Windows
choco install wireguard -y

# Générer clés
wg genkey | tee privatekey | wg pubkey > publickey

# Créer config /etc/wireguard/chrona.conf (Linux style)
# Ou via GUI Wireguard
```

**Android** :
- Google Play : "WireGuard"
- Importer QR code ou config

---

## 🐳 Option 3 : VPN via Docker Compose (Intégré)

Ajouter un serveur VPN **directement dans Docker** :

### Modification `docker-compose.yml`

```yaml
services:
  # ... autres services ...

  wireguard:
    image: linuxserver/wireguard
    container_name: chrona-vpn
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - SERVERURL=192.168.211.14  # ← Remplacer par votre IP
      - SERVERPORT=51820
      - PEERS=android-pixel7,android-backup
      - PEERDNS=auto
      - INTERNAL_SUBNET=10.6.0.0
      - ALLOWEDIPS=10.6.0.1/32,192.168.211.0/24
    ports:
      - "51820:51820/udp"
    volumes:
      - ./wireguard:/config
      - /lib/modules:/lib/modules
    networks:
      - default
    restart: unless-stopped
```

**Récupérer QR Codes** :

```bash
# Une fois le container lancé
docker compose exec wireguard cat /config/peer_android-pixel7/QR.png

# Ou afficher en texte
docker compose exec wireguard cat /config/peer_android-pixel7/wg0.conf
```

---

## 📱 Accès Chrona via VPN

### Une fois connecté au VPN

#### Via OpenVPN

```
Android VPN Status: Connected
VPN IP: 10.8.0.6
Tunnel: Vers 192.168.211.14:1194

Ouvrir navigateur:
URL: http://192.168.211.14:5174
(Vous êtes "dans" le réseau via le VPN)
```

#### Via Wireguard

```
Android VPN Status: Connected
Wireguard IP: 10.6.0.2
Tunnel: Vers 192.168.211.14:51820

Ouvrir navigateur:
URL: http://192.168.211.14:5174
```

---

## 🔒 Firewall Configuration pour VPN

### Autoriser Port VPN dans Windows Defender

```powershell
# OpenVPN (port 1194)
netsh advfirewall firewall add rule name="OpenVPN Server" `
  dir=in action=allow protocol=udp localport=1194

# Wireguard (port 51820)
netsh advfirewall firewall add rule name="Wireguard VPN" `
  dir=in action=allow protocol=udp localport=51820
```

### Autoriser Trafic VPN → Chrona

```powershell
# Permettre VPN clients → Backend API
netsh advfirewall firewall add rule name="VPN to Chrona API" `
  dir=in action=allow protocol=tcp localport=8000 `
  remoteip="10.8.0.0/24"  # Réseau VPN OpenVPN

netsh advfirewall firewall add rule name="VPN to Kiosk" `
  dir=in action=allow protocol=tcp localport=5174 `
  remoteip="10.8.0.0/24"
```

---

## 📊 Flux de Connectivité VPN

### Avant VPN (Bloqué par réseau)

```
Android (192.168.211.XXX) ─X→ Kiosk (5174)  ❌ Blocage réseau
```

### Après VPN (Tunnel sécurisé)

```
Android (WiFi ou 4G)
    ↓
OpenVPN Client (Port 1194 UDP)
    ↓ (Tunnel chiffré)
PC/Serveur (192.168.211.14:1194)
    ↓
Kiosk Service (localhost:5174)
    ↓
Backend API (localhost:8000)
    ↓
PostgreSQL (localhost:5432)
    ✅ ACCÈS RÉUSSI
```

---

## 🧪 Tests de Connectivité

### Test 1 : VPN Connecté?

```bash
# Sur Android via Termux ou adb shell
ping 192.168.211.14      # Doit répondre si VPN OK
```

### Test 2 : Accès Backend?

```bash
# Via navigateur Android (VPN activé)
http://192.168.211.14:8000/health

# Doit afficher:
{"status":"ok","db":"ok"}
```

### Test 3 : Accès Kiosk?

```bash
# Via navigateur Android (VPN activé)
http://192.168.211.14:5174

# Doit afficher l'interface Kiosk
```

---

## 📋 Checklist Déploiement VPN

- [ ] OpenVPN ou Wireguard installé sur PC
- [ ] Certificats/clés générés
- [ ] Fichier config serveur créé
- [ ] Firewall rules ajoutées (port 1194 ou 51820)
- [ ] Serveur VPN démarré et écoutant
- [ ] Fichiers client exportés
- [ ] App OpenVPN/Wireguard installée sur Android
- [ ] Profil VPN importé dans l'app
- [ ] Test de connexion réussi (status "Connected")
- [ ] Accès à http://192.168.211.14:5174 via VPN fonctionnel
- [ ] Logs sans erreurs

---

## 🐛 Dépannage VPN

### Problème 1 : Erreur "Connection refused"

```
Solution:
1. Vérifier serveur VPN actif:
   tasklist | findstr openvpn    # Windows

2. Vérifier port ouvert:
   netstat -ano | findstr 1194

3. Vérifier firewall:
   netsh advfirewall firewall show rule name="OpenVPN Server"
```

### Problème 2 : VPN connecté mais pas d'accès à Chrona

```
Solution:
1. Vérifier route réseau:
   # Android Wireguard: Settings → Allowed IPs
   # Doit contenir: 192.168.211.0/24

2. Vérifier firewall PC:
   netsh advfirewall firewall show rule name="VPN to Kiosk"

3. Vérifier API accessible:
   curl http://192.168.211.14:8000/health
```

### Problème 3 : VPN se déconnecte régulièrement

```
Solution:
1. Augmenter keepalive dans config:
   keepalive 10 120  →  keepalive 5 30

2. Vérifier signal WiFi (si via WiFi)

3. Augmenter MTU (size paquet):
   mtu 1500  →  mtu 1300
```

---

## 📞 Support et Ressources

- **OpenVPN** : https://openvpn.net/
- **Wireguard** : https://www.wireguard.com/
- **OpenVPN Android** : https://play.google.com/store/apps/details?id=net.openvpn.openvpn
- **Wireguard Android** : https://play.google.com/store/apps/details?id=com.wireguard.android

---

**Version** : 1.0
**Dernière mise à jour** : 2024-10-24
**Auteur** : Claude Code
**Statut** : Draft - À tester en production
