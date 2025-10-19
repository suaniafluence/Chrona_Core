param(
  [string]$Email = "dev@example.com",
  [string]$Password = "Passw0rd!",
  [string]$Api = "http://localhost:8000",
  [int]$KioskId = 1,
  [string]$DeviceFingerprint = "e2e-device-001",
  [ValidateSet("clock_in","clock_out")] [string]$PunchType = "clock_in"
)

$ErrorActionPreference = 'Stop'

function Write-Step($msg) { Write-Host "[STEP] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }

try {
  Write-Step "API: $Api"

  # 1) Register (idempotent)
  $regBody = @{ email = $Email; password = $Password } | ConvertTo-Json -Compress
  try {
    $null = Invoke-RestMethod -Uri "$Api/auth/register" -Method Post -ContentType 'application/json' -Body $regBody
    Write-Ok "Registered user $Email"
  } catch {
    $code = $_.Exception.Response.StatusCode.Value__
    if ($code -in  (400,409)) { Write-Warn "User exists ($code)" } else { throw }
  }

  # 2) Token
  $tokenResp = Invoke-RestMethod -Uri "$Api/auth/token" -Method Post -ContentType 'application/x-www-form-urlencoded' -Body "username=$Email&password=$Password"
  $token = $tokenResp.access_token
  if (-not $token) { throw "Token acquisition failed" }
  $auth = @{ Authorization = "Bearer $token" }
  Write-Ok "Token acquired"

  # 3) Register device or fetch existing
  $deviceBody = @{ device_fingerprint = $DeviceFingerprint; device_name = "E2E Device"; attestation_data = $null } | ConvertTo-Json -Compress
  $device = $null
  try {
    $device = Invoke-RestMethod -Uri "$Api/devices/register" -Method Post -Headers $auth -ContentType 'application/json' -Body $deviceBody
    Write-Ok "Device registered (id=$($device.id))"
  } catch {
    $code = $_.Exception.Response.StatusCode.Value__
    if ($code -eq 500) { Write-Warn "Device registration error (500), will list devices" } elseif ($code -eq 409) { Write-Warn "Device already exists" } else { throw }
  }
  if (-not $device) {
    $list = Invoke-RestMethod -Uri "$Api/devices/me" -Headers $auth -Method Get
    $device = $list | Where-Object { $_.device_fingerprint -eq $DeviceFingerprint } | Select-Object -First 1
  }
  if (-not $device) { throw "Device not available" }
  $deviceId = [int]$device.id

  # 4) Request QR token
  $qrReq = @{ device_id = $deviceId } | ConvertTo-Json -Compress
  $qr = Invoke-RestMethod -Uri "$Api/punch/request-token" -Method Post -Headers $auth -ContentType 'application/json' -Body $qrReq
  $qr_token = $qr.qr_token
  if (-not $qr_token) { throw "QR token not received" }
  Write-Ok "QR token length: $($qr_token.Length) (expires_in=$($qr.expires_in)s)"

  # 5) Validate punch from kiosk
  $validateReq = @{ qr_token = $qr_token; kiosk_id = $KioskId; punch_type = $PunchType } | ConvertTo-Json -Compress
  $punch = Invoke-RestMethod -Uri "$Api/punch/validate" -Method Post -ContentType 'application/json' -Body $validateReq

  Write-Ok "Punch $PunchType success: id=$($punch.punch_id) at $($punch.punched_at)"
  $punch | ConvertTo-Json -Depth 5
  exit 0
}
catch {
  Write-Err $_
  if ($_.InvocationInfo.PositionMessage) { Write-Host $_.InvocationInfo.PositionMessage }
  exit 1
}

