# Environment Setup Fix for JWT Keys

## Problem

When running tests or the application, you may encounter this error:

```
RuntimeError: JWT keys not found: [Errno 2] No such file or directory: 'C:/Program Files/Git/app/jwt_private_key.pem'.
Run 'python tools/generate_keys.py' to generate RS256 keys.
```

## Root Cause

Conflicting environment variables set to `/app/` path:

```
JWT_PRIVATE_KEY_PATH=/app/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=/app/jwt_public_key.pem
```

On Windows, `/app/` maps to `C:/Program Files/Git/app/` which doesn't contain the JWT keys.

## Solution

### Option 1: Clear Environment Variables (Quick Fix)

Before running tests or the app, clear these variables:

```bash
# In Bash (Git Bash, WSL, etc.)
unset JWT_PRIVATE_KEY_PATH
unset JWT_PUBLIC_KEY_PATH

# In PowerShell
$env:JWT_PRIVATE_KEY_PATH = ""
$env:JWT_PUBLIC_KEY_PATH = ""

# In Windows Command Prompt
set JWT_PRIVATE_KEY_PATH=
set JWT_PUBLIC_KEY_PATH=
```

Then run your tests:
```bash
cd backend
python -m pytest tests/test_admin_hr_codes.py -v
```

### Option 2: Set Correct Paths (Recommended)

Set the environment variables to the correct locations:

```bash
# In Bash
export JWT_PRIVATE_KEY_PATH=/c/Gemini_CLI/Chrona_Core/backend/jwt_private_key.pem
export JWT_PUBLIC_KEY_PATH=/c/Gemini_CLI/Chrona_Core/backend/jwt_public_key.pem

# In PowerShell
$env:JWT_PRIVATE_KEY_PATH = "C:\Gemini_CLI\Chrona_Core\backend\jwt_private_key.pem"
$env:JWT_PUBLIC_KEY_PATH = "C:\Gemini_CLI\Chrona_Core\backend\jwt_public_key.pem"
```

### Option 3: Create .env File (Best Practice)

Create a `.env` file in the `backend/` directory:

```env
# JWT Configuration
JWT_PRIVATE_KEY_PATH=./jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=./jwt_public_key.pem

# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Algorithm (RS256 or ES256)
ALGORITHM=RS256

# Token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Ephemeral token for QR codes (seconds)
EPHEMERAL_TOKEN_EXPIRE_SECONDS=30
```

Then load it with:
```bash
cd backend
source .env  # Bash
# or
dotenv -f .env python -m uvicorn src.main:app --reload  # Using python-dotenv
```

## Verification

To verify the fix works, run a quick test:

```bash
cd backend
python -c "
import os
from pathlib import Path

# Check current settings
print('JWT_PRIVATE_KEY_PATH:', os.getenv('JWT_PRIVATE_KEY_PATH', 'Not set'))
print('JWT_PUBLIC_KEY_PATH:', os.getenv('JWT_PUBLIC_KEY_PATH', 'Not set'))

# Check if files exist
project_root = Path.cwd().parent
private_key = project_root / 'backend' / 'jwt_private_key.pem'
public_key = project_root / 'backend' / 'jwt_public_key.pem'

print('\\nPrivate key exists:', private_key.exists())
print('Public key exists:', public_key.exists())
"
```

## File Locations

The JWT keys should be in the `backend/` directory:

```
Chrona_Core/
├── backend/
│   ├── jwt_private_key.pem    ← Private key (RS256)
│   ├── jwt_public_key.pem     ← Public key (RS256)
│   ├── jwt_ec_private_key.pem ← Private key (ES256, if using ES256)
│   ├── jwt_ec_public_key.pem  ← Public key (ES256, if using ES256)
│   └── tests/
│       └── test_admin_hr_codes.py
├── jwt_private_key.pem  ← Copy for project root compatibility
└── jwt_public_key.pem
```

## Generating Keys

If keys are missing, generate them:

```bash
cd backend
python tools/generate_keys.py  # For RS256
# or
python tools/generate_ec_keys.py  # For ES256
```

## Running Tests After Fix

```bash
cd backend

# Clear conflicting vars (if still set)
unset JWT_PRIVATE_KEY_PATH JWT_PUBLIC_KEY_PATH

# Run all tests
python -m pytest tests/test_admin_hr_codes.py -v

# Run specific test
python -m pytest tests/test_admin_hr_codes.py::test_create_hr_code_success -v

# Run with coverage
python -m pytest tests/test_admin_hr_codes.py --cov=src --cov-report=html
```

## Running Application After Fix

```bash
cd backend

# Clear conflicting vars (if still set)
unset JWT_PRIVATE_KEY_PATH JWT_PUBLIC_KEY_PATH

# Create Python venv (if needed)
python -m venv .venv
source .venv/bin/activate  # Bash
# or
.venv\Scripts\activate     # PowerShell/CMD

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Checking Current Environment

To see all environment variables related to JWT:

```bash
env | grep JWT
# or
echo $JWT_PRIVATE_KEY_PATH
echo $JWT_PUBLIC_KEY_PATH
```

To permanently unset problematic variables in your shell profile:

**Bash/Zsh** (~/.bashrc or ~/.zshrc):
```bash
unset JWT_PRIVATE_KEY_PATH
unset JWT_PUBLIC_KEY_PATH
```

**PowerShell** ($PROFILE):
```powershell
Remove-Item env:JWT_PRIVATE_KEY_PATH -ErrorAction SilentlyContinue
Remove-Item env:JWT_PUBLIC_KEY_PATH -ErrorAction SilentlyContinue
```

---

**Note**: These environment variables were likely set during a previous Docker or container setup. They can be safely removed as the application resolves paths correctly based on file locations.
