"""HR Code service for Level B onboarding."""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.hr_code import HRCode


class HRCodeService:
    """Service for managing HR codes during employee onboarding."""

    @staticmethod
    def generate_hr_code(prefix: str = "EMPL") -> str:
        """Generate a unique HR code.

        Format: PREFIX-YYYY-RANDOM (e.g., EMPL-2025-A7K9X)

        Args:
            prefix: Code prefix (default: EMPL)

        Returns:
            Generated HR code string
        """
        year = datetime.now(timezone.utc).year
        random_part = "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
        return f"{prefix}-{year}-{random_part}"

    @staticmethod
    async def create_hr_code(
        session: AsyncSession,
        employee_email: str,
        employee_name: Optional[str] = None,
        created_by_admin_id: Optional[int] = None,
        expires_in_days: int = 7,
    ) -> HRCode:
        """Create a new HR code for employee onboarding.

        Args:
            session: Database session
            employee_email: Employee email address
            employee_name: Employee full name (optional)
            created_by_admin_id: Admin user ID who created the code
            expires_in_days: Expiration time in days (default: 7)

        Returns:
            Created HRCode instance

        Raises:
            Exception if code generation fails after retries
        """
        # Check if employee already has an unused, non-expired HR code
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(HRCode).where(
                HRCode.employee_email == employee_email,
                HRCode.is_used.is_(False),
                HRCode.expires_at > now,
            )
        )
        existing_code = result.scalar_one_or_none()

        if existing_code:
            # Return existing valid code
            return existing_code

        # Generate unique code (retry if collision)
        max_retries = 5
        for _ in range(max_retries):
            code = HRCodeService.generate_hr_code()
            result = await session.execute(select(HRCode).where(HRCode.code == code))
            if result.scalar_one_or_none() is None:
                break
        else:
            raise Exception("Failed to generate unique HR code after retries")

        # Create HR code
        expires_at = now + timedelta(days=expires_in_days)
        hr_code = HRCode(
            code=code,
            employee_email=employee_email,
            employee_name=employee_name,
            created_by_admin_id=created_by_admin_id,
            created_at=now,
            expires_at=expires_at,
            is_used=False,
        )
        session.add(hr_code)
        await session.commit()
        await session.refresh(hr_code)

        return hr_code

    @staticmethod
    async def validate_hr_code(
        session: AsyncSession, code: str, email: str
    ) -> tuple[bool, Optional[HRCode], Optional[str]]:
        """Validate HR code for onboarding.

        Args:
            session: Database session
            code: HR code to validate
            email: Employee email (must match code)

        Returns:
            Tuple of (is_valid, hr_code_obj, error_message)
        """
        result = await session.execute(select(HRCode).where(HRCode.code == code))
        hr_code = result.scalar_one_or_none()

        if not hr_code:
            return False, None, "Code HR invalide"

        if hr_code.employee_email != email:
            return False, None, "Code HR ne correspond pas à cet email"

        if hr_code.is_used:
            return False, None, "Code HR déjà utilisé"

        now = datetime.now(timezone.utc)
        if hr_code.expires_at and hr_code.expires_at < now:
            return False, None, "Code HR expiré"

        return True, hr_code, None

    @staticmethod
    async def mark_hr_code_used(
        session: AsyncSession, hr_code: HRCode, used_by_user_id: int
    ) -> None:
        """Mark HR code as used after successful onboarding.

        Args:
            session: Database session
            hr_code: HRCode instance to mark as used
            used_by_user_id: User ID who redeemed the code
        """
        hr_code.is_used = True
        hr_code.used_at = datetime.now(timezone.utc)
        hr_code.used_by_user_id = used_by_user_id
        session.add(hr_code)
        await session.commit()

    @staticmethod
    async def list_hr_codes(
        session: AsyncSession,
        include_used: bool = False,
        include_expired: bool = False,
    ) -> list[HRCode]:
        """List HR codes with optional filtering.

        Args:
            session: Database session
            include_used: Include used codes (default: False)
            include_expired: Include expired codes (default: False)

        Returns:
            List of HRCode instances
        """
        query = select(HRCode)

        if not include_used:
            query = query.where(HRCode.is_used.is_(False))

        if not include_expired:
            now = datetime.now(timezone.utc)
            query = query.where(
                (HRCode.expires_at.is_(None)) | (HRCode.expires_at > now)
            )

        result = await session.execute(query.order_by(HRCode.created_at.desc()))
        return list(result.scalars().all())
