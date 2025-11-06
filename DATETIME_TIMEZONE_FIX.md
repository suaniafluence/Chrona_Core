# Fix DateTime Timezone Issue

## Problem Description

The application was experiencing errors when comparing datetime values:

```
sqlalchemy.exc.DBAPIError: invalid input for query argument $2:
datetime.datetime(2025, 11, 6, 16, 5, 52...
(can't subtract offset-naive and offset-aware datetimes)
```

**Root Cause**:
- Python code uses `datetime.now(timezone.utc)` → timezone-aware datetime
- PostgreSQL columns are `TIMESTAMP WITHOUT TIME ZONE` → timezone-naive
- SQLAlchemy cannot compare/subtract them

## Solution

Migration `0011_fix_datetime_timezone.py` converts all datetime columns to `TIMESTAMP WITH TIME ZONE`.

## Apply the Migration

### Option 1: Using Docker Compose (Recommended)

If your backend is running in Docker:

```bash
# Apply migration inside the backend container
docker compose exec backend alembic upgrade head

# Or restart the backend to auto-apply migrations
docker compose restart backend
```

### Option 2: Local Development

If running locally with virtualenv:

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
alembic upgrade head
```

### Option 3: Manual SQL (if needed)

If you need to apply the fix manually to an existing database:

```sql
-- Example for users table (repeat for all tables)
ALTER TABLE users
  ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

-- See migration file for complete list of tables
```

## Verify the Fix

After applying the migration, test HR code creation:

```bash
# From the backoffice or using curl
curl -X POST http://localhost:8000/admin/hr-codes \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_email": "test@example.com",
    "employee_name": "Test Employee",
    "expires_in_days": 7
  }'
```

Expected response: HR code created successfully without timezone errors.

## Tables Affected

The migration updates datetime columns in these tables:

1. `users` (created_at)
2. `audit_logs` (created_at)
3. `devices` (registered_at, last_seen_at)
4. `kiosks` (created_at, last_heartbeat_at)
5. `kiosk_access` (granted_at, expires_at)
6. `punches` (punched_at, created_at)
7. `token_tracking` (issued_at, expires_at, consumed_at)
8. `hr_codes` (created_at, expires_at, used_at)
9. `otp_verifications` (created_at, expires_at, verified_at)
10. `onboarding_sessions` (created_at, expires_at, completed_at)
11. `totp_secrets` (provisioning_qr_expires_at, activated_at, created_at, last_used_at, key_rotation_due_at)
12. `totp_nonce_blacklist` (jwt_expires_at, consumed_at)
13. `totp_lockouts` (locked_at, locked_until, released_at)
14. `totp_recovery_codes` (used_at, created_at, expires_at)
15. `totp_validation_attempts` (attempted_at)

## Why TIMESTAMP WITH TIME ZONE?

For Chrona (GDPR-compliant audit system), timezone-aware timestamps are essential:

- **Accurate audit logs**: Know exactly when events occurred, regardless of server timezone
- **Compliance**: GDPR requires precise timestamp records
- **International operations**: Handles daylight saving time and timezone changes correctly
- **Best practice**: PostgreSQL documentation recommends `timestamptz` for most use cases

## Rollback (if needed)

```bash
alembic downgrade -1
```

This reverts all columns back to `TIMESTAMP WITHOUT TIME ZONE`, but you'll need to ensure all Python code uses timezone-naive datetimes (`datetime.utcnow()` instead of `datetime.now(timezone.utc)`).

## Next Steps

After applying this migration, all datetime operations will work correctly with timezone-aware values. The service layer already uses `datetime.now(timezone.utc)` consistently, so no code changes are needed.
