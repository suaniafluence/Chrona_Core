"""
End-to-end test script for QR code punch flow.

This script simulates the complete flow:
1. User registers/logs in
2. User registers a device
3. User requests an ephemeral QR token
4. Kiosk scans and validates the QR token
5. Punch record is created
"""

import asyncio
import os
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import Device, Kiosk, Punch, User
from src.security import create_ephemeral_qr_token, decode_token


async def main() -> None:
    """Run the complete end-to-end QR punch flow (script mode)."""
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("[INFO] Starting end-to-end QR flow script...")
        print()

        # Step 1: Get or create a test user
        print("[STEP 1] Get test user...")
        from sqlalchemy import select

        result = await session.execute(
            select(User).where(User.email == "testuser@example.com")
        )
        user = result.scalar_one_or_none()

        if not user:
            print("  [!] No test user found. Please create one first.")
            print("  [TIP] Run: cd backend && python -m tools.create_test_user")
            return

        print(f"  [OK] User: {user.email} (ID: {user.id})")
        print()

        # Step 2: Get or create a test device for the user
        print("[STEP 2] Get or create test device...")
        result = await session.execute(
            select(Device).where(Device.user_id == user.id).where(Device.is_revoked == False)
        )
        device = result.scalar_one_or_none()

        if device:
            print(f"  [OK] Found device: {device.device_name} (ID: {device.id})")
        else:
            device = Device(
                user_id=user.id,
                device_fingerprint=f"test-device-{datetime.utcnow().timestamp()}",
                device_name="Test Device E2E",
                attestation_data="test-attestation",
                is_revoked=False,
            )
            session.add(device)
            await session.commit()
            await session.refresh(device)
            print(f"  [OK] Created device: {device.device_name} (ID: {device.id})")
        print()

        # Step 3: Generate ephemeral QR token
        print("[STEP 3] Generate ephemeral QR token...")
        qr_token, payload = create_ephemeral_qr_token(
            user_id=user.id, device_id=device.id, expires_seconds=30
        )
        print("  [OK] Token generated")
        print(f"      User ID: {payload['sub']}")
        print(f"      Device ID: {payload['device_id']}")
        print(f"      JTI: {payload['jti']}")
        print(f"      Nonce: {payload['nonce']}")
        print(f"      Expires: {payload['exp']}")
        print(f"      Token (first 50 chars): {qr_token[:50]}...")
        print()

        # Step 4: Get test kiosk
        print("[STEP 4] Get test kiosk...")
        kiosk = await session.get(Kiosk, 1)
        if not kiosk:
            print("  [!] No test kiosk found. Run: cd backend && python -m tools.seed_kiosk")
            return

        print(f"  [OK] Kiosk: {kiosk.kiosk_name} (ID: {kiosk.id})")
        print(f"      Location: {kiosk.location}")
        print(f"      Active: {kiosk.is_active}")
        print()

        # Step 5: Verify token (simulate kiosk scanning)
        print("[STEP 5] Verify token (kiosk validation)...")
        try:
            decoded = decode_token(qr_token)
            if decoded is None:
                print("  [ERROR] Token verification failed: Invalid or expired token")
                return
            print("  [OK] Token verified successfully")
            print(f"      User ID: {decoded['sub']}")
            print(f"      Device ID: {decoded['device_id']}")
            print(f"      Type: {decoded.get('type', 'N/A')}")
        except Exception as e:
            print(f"  [ERROR] Token verification failed: {e}")
            return
        print()

        # Step 6: Simulate punch creation (would normally be via /punch/validate)
        print("[STEP 6] Simulate punch record creation...")
        from src.models import PunchType

        punch = Punch(
            user_id=user.id,
            device_id=device.id,
            kiosk_id=kiosk.id,
            punch_type=PunchType.CLOCK_IN,
            punched_at=datetime.now(timezone.utc),
            jwt_jti=payload["jti"],
        )
        session.add(punch)
        await session.commit()
        await session.refresh(punch)

        print("  [OK] Punch created successfully!")
        print(f"      Punch ID: {punch.id}")
        print(f"      User: {user.email}")
        print(f"      Kiosk: {kiosk.kiosk_name}")
        print(f"      Type: {punch.punch_type.value}")
        print(f"      Timestamp: {punch.punched_at}")
        print()

        print("[SUCCESS] End-to-end flow completed successfully!")
        print()
        print("Summary:")
        print(
            f"  - User '{user.email}' generated QR token from device '{device.device_name}'"
        )
        print(
            f"  - Kiosk '{kiosk.kiosk_name}' scanned and validated the token"
        )
        print(
            f"  - Punch record created: {punch.punch_type.value} at {punch.punched_at}"
        )


if __name__ == "__main__":
    asyncio.run(main())

