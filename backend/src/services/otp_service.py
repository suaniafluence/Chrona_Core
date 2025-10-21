"""OTP service for Level B onboarding verification."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.otp_verification import OTPVerification


class OTPService:
    """Service for generating and verifying OTP codes."""

    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5

    @staticmethod
    def generate_otp_code(length: int = 6) -> str:
        """Generate a random numeric OTP code.

        Args:
            length: Length of OTP code (default: 6)

        Returns:
            Numeric OTP string
        """
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    @staticmethod
    def hash_otp(otp_code: str) -> str:
        """Hash OTP code for secure storage.

        Args:
            otp_code: Plain OTP code

        Returns:
            SHA-256 hash of OTP code
        """
        return hashlib.sha256(otp_code.encode()).hexdigest()

    @staticmethod
    async def create_otp(
        session: AsyncSession,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expiry_minutes: int = OTP_EXPIRY_MINUTES,
    ) -> tuple[OTPVerification, str]:
        """Create a new OTP for email verification.

        Args:
            session: Database session
            email: Email address for OTP delivery
            ip_address: Request IP address
            user_agent: User agent string
            expiry_minutes: OTP expiration time in minutes

        Returns:
            Tuple of (OTPVerification instance, plain OTP code)
        """
        # Invalidate any existing unverified OTPs for this email
        await OTPService.invalidate_previous_otps(session, email)

        # Generate OTP
        otp_code = OTPService.generate_otp_code(OTPService.OTP_LENGTH)
        otp_hash = OTPService.hash_otp(otp_code)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=expiry_minutes)

        # Create OTP record
        otp_record = OTPVerification(
            email=email,
            otp_code=otp_code,  # Store plain code temporarily for email
            otp_hash=otp_hash,
            created_at=now,
            expires_at=expires_at,
            is_verified=False,
            attempt_count=0,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(otp_record)
        await session.commit()
        await session.refresh(otp_record)

        return otp_record, otp_code

    @staticmethod
    async def verify_otp(
        session: AsyncSession, email: str, otp_code: str
    ) -> tuple[bool, Optional[OTPVerification], Optional[str]]:
        """Verify OTP code for email.

        Args:
            session: Database session
            email: Email address
            otp_code: OTP code to verify

        Returns:
            Tuple of (is_valid, otp_record, error_message)
        """
        # Find most recent unverified OTP for this email
        result = await session.execute(
            select(OTPVerification)
            .where(
                OTPVerification.email == email,
                OTPVerification.is_verified.is_(False),
            )
            .order_by(OTPVerification.created_at.desc())
        )
        otp_record = result.scalar_one_or_none()

        if not otp_record:
            return False, None, "Aucun code OTP trouvé pour cet email"

        # Check if expired
        now = datetime.now(timezone.utc)
        if otp_record.expires_at < now:
            return False, otp_record, "Code OTP expiré"

        # Check attempt count
        if otp_record.attempt_count >= OTPService.MAX_ATTEMPTS:
            return False, otp_record, "Nombre maximum de tentatives dépassé"

        # Increment attempt count
        otp_record.attempt_count += 1
        session.add(otp_record)
        await session.commit()

        # Verify OTP hash
        otp_hash = OTPService.hash_otp(otp_code)
        if otp_hash != otp_record.otp_hash:
            await session.commit()  # Commit attempt count increment
            return False, otp_record, "Code OTP invalide"

        # Mark as verified
        otp_record.is_verified = True
        otp_record.verified_at = now
        session.add(otp_record)
        await session.commit()

        return True, otp_record, None

    @staticmethod
    async def invalidate_previous_otps(session: AsyncSession, email: str) -> None:
        """Invalidate all previous unverified OTPs for an email.

        This prevents OTP reuse and ensures only the latest OTP is valid.

        Args:
            session: Database session
            email: Email address
        """
        result = await session.execute(
            select(OTPVerification).where(
                OTPVerification.email == email,
                OTPVerification.is_verified.is_(False),
            )
        )
        old_otps = result.scalars().all()

        for otp in old_otps:
            # Set expired to invalidate
            otp.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
            session.add(otp)

        await session.commit()

    @staticmethod
    async def send_otp_email(email: str, otp_code: str) -> bool:
        """Send OTP code via email.

        Args:
            email: Recipient email address
            otp_code: OTP code to send

        Returns:
            True if email sent successfully
        """
        from src.services.email_service import get_email_service

        email_service = get_email_service()
        return await email_service.send_otp_email(email, otp_code)
