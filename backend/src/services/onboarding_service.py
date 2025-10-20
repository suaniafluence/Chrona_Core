"""Onboarding session service for Level B security flow."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.onboarding_session import OnboardingSession


class OnboardingService:
    """Service for managing onboarding sessions."""

    SESSION_EXPIRY_MINUTES = 30

    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure random session token.

        Returns:
            Random hex token (64 characters)
        """
        return secrets.token_hex(32)

    @staticmethod
    async def create_session(
        session: AsyncSession,
        email: str,
        hr_code_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expiry_minutes: int = SESSION_EXPIRY_MINUTES,
    ) -> OnboardingSession:
        """Create a new onboarding session.

        Args:
            session: Database session
            email: Employee email
            hr_code_id: Associated HR code ID
            ip_address: Request IP address
            user_agent: User agent string
            expiry_minutes: Session expiration time in minutes

        Returns:
            Created OnboardingSession instance
        """
        # Invalidate any existing incomplete sessions for this email
        await OnboardingService.invalidate_previous_sessions(session, email)

        session_token = OnboardingService.generate_session_token()
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=expiry_minutes)

        onboarding_session = OnboardingSession(
            session_token=session_token,
            email=email,
            hr_code_id=hr_code_id,
            step="hr_code",
            created_at=now,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(onboarding_session)
        await session.commit()
        await session.refresh(onboarding_session)

        return onboarding_session

    @staticmethod
    async def get_session(
        session: AsyncSession, session_token: str
    ) -> Optional[OnboardingSession]:
        """Get onboarding session by token.

        Args:
            session: Database session
            session_token: Session token

        Returns:
            OnboardingSession instance or None
        """
        result = await session.execute(
            select(OnboardingSession).where(
                OnboardingSession.session_token == session_token
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def validate_session(
        session: AsyncSession, session_token: str
    ) -> tuple[bool, Optional[OnboardingSession], Optional[str]]:
        """Validate onboarding session.

        Args:
            session: Database session
            session_token: Session token to validate

        Returns:
            Tuple of (is_valid, session_obj, error_message)
        """
        onboarding_session = await OnboardingService.get_session(
            session, session_token
        )

        if not onboarding_session:
            return False, None, "Session invalide"

        now = datetime.now(timezone.utc)
        if onboarding_session.expires_at < now:
            return False, onboarding_session, "Session expirée"

        if onboarding_session.completed_at:
            return False, onboarding_session, "Session déjà terminée"

        return True, onboarding_session, None

    @staticmethod
    async def update_session_step(
        session: AsyncSession,
        onboarding_session: OnboardingSession,
        step: str,
        device_fingerprint_candidate: Optional[str] = None,
    ) -> None:
        """Update onboarding session step.

        Args:
            session: Database session
            onboarding_session: OnboardingSession instance
            step: New step value (hr_code, otp_sent, otp_verified, device_attestation, completed)
            device_fingerprint_candidate: Device fingerprint (optional)
        """
        onboarding_session.step = step
        if device_fingerprint_candidate:
            onboarding_session.device_fingerprint_candidate = (
                device_fingerprint_candidate
            )
        session.add(onboarding_session)
        await session.commit()

    @staticmethod
    async def complete_session(
        session: AsyncSession, onboarding_session: OnboardingSession
    ) -> None:
        """Mark onboarding session as completed.

        Args:
            session: Database session
            onboarding_session: OnboardingSession instance
        """
        onboarding_session.step = "completed"
        onboarding_session.completed_at = datetime.now(timezone.utc)
        session.add(onboarding_session)
        await session.commit()

    @staticmethod
    async def invalidate_previous_sessions(
        session: AsyncSession, email: str
    ) -> None:
        """Invalidate all previous incomplete sessions for an email.

        Args:
            session: Database session
            email: Employee email
        """
        result = await session.execute(
            select(OnboardingSession).where(
                OnboardingSession.email == email,
                OnboardingSession.completed_at.is_(None),
            )
        )
        old_sessions = result.scalars().all()

        for old_session in old_sessions:
            # Set expired to invalidate
            old_session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
            session.add(old_session)

        await session.commit()
