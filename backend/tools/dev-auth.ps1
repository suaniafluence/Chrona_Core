param(
  [string]$Email = "dev@example.com",
  [string]$Password = "Passw0rd!",
  [string]$Api = "http://localhost:8000"
)

Write-Host "Registering user $Email at $Api ..."
try {
  $register = Invoke-RestMethod -Method Post -Uri "$Api/auth/register" -ContentType 'application/json' -Body (@{ email=$Email; password=$Password } | ConvertTo-Json)
  Write-Host "Registered: $($register.email)"
} catch {
  Write-Warning "Register may have failed (possibly already exists): $($_.Exception.Message)"
}

Write-Host "Logging in ..."
$form = "username=$Email&password=$Password"
$tokenResp = Invoke-RestMethod -Method Post -Uri "$Api/auth/token" -ContentType 'application/x-www-form-urlencoded' -Body $form
$token = $tokenResp.access_token
if (!$token) { throw "Login failed" }
Write-Host "Token:" $token

Write-Host "Me endpoint ..."
$me = Invoke-RestMethod -Method Get -Uri "$Api/auth/me" -Headers @{ Authorization = "Bearer $token" }
$me | ConvertTo-Json -Depth 4

