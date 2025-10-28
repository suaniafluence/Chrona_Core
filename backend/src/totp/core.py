"""Core TOTP generation and validation logic.

Implements RFC 6238 TOTP with SHA256 algorithm.
Compliant with employee security spec:
- entropy: >=160 bits
- encoding: Base32
- algorithm: SHA256
- digits: 6
- period: 30s
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote


def generate_totp_secret(entropy_bits: int = 160) -> str:
    """Generate a cryptographically secure TOTP secret.

    Args:
        entropy_bits: Minimum entropy in bits (default: 160, minimum required)

    Returns:
        Base32-encoded secret string (uppercase, no padding)

    Example:
        >>> secret = generate_totp_secret()
        >>> len(secret)  # Will be ~32 characters for 160 bits
        32
    """
    if entropy_bits < 160:
        raise ValueError("TOTP secret must have at least 160 bits of entropy")

    # Calculate bytes needed (round up)
    num_bytes = (entropy_bits + 7) // 8

    # Generate random bytes
    random_bytes = secrets.token_bytes(num_bytes)

    # Encode as Base32 (RFC 3548)
    secret_b32 = base64.b32encode(random_bytes).decode("utf-8")

    # Remove padding (= characters) as per TOTP standard
    return secret_b32.rstrip("=")


def _hotp(secret: str, counter: int, digits: int = 6, algorithm: str = "SHA256") -> str:
    """HOTP (HMAC-based One-Time Password) algorithm (RFC 4226).

    Args:
        secret: Base32-encoded secret
        counter: Counter value (for TOTP, this is time-based)
        digits: Number of digits in OTP (6 or 8)
        algorithm: Hash algorithm (SHA1, SHA256, SHA512)

    Returns:
        OTP code as zero-padded string
    """
    # Decode Base32 secret (add padding if needed)
    secret_padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    secret_bytes = base64.b32decode(secret_padded, casefold=True)

    # Convert counter to 8-byte big-endian
    counter_bytes = struct.pack(">Q", counter)

    # HMAC with specified algorithm
    hash_func = getattr(hashlib, algorithm.lower())
    hmac_hash = hmac.new(secret_bytes, counter_bytes, hash_func).digest()

    # Dynamic truncation (RFC 4226 Section 5.3)
    offset = hmac_hash[-1] & 0x0F
    truncated = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF

    # Generate OTP
    otp = truncated % (10**digits)

    # Zero-pad to correct length
    return str(otp).zfill(digits)


def generate_totp_code(
    secret: str,
    timestamp: int | None = None,
    period: int = 30,
    digits: int = 6,
    algorithm: str = "SHA256",
) -> str:
    """Generate TOTP code for given timestamp.

    Args:
        secret: Base32-encoded TOTP secret
        timestamp: Unix timestamp (default: current time)
        period: Time period in seconds (default: 30)
        digits: Number of digits (default: 6)
        algorithm: Hash algorithm (default: SHA256)

    Returns:
        TOTP code as zero-padded string

    Example:
        >>> secret = "JBSWY3DPEHPK3PXP"
        >>> code = generate_totp_code(secret, timestamp=1234567890)
        >>> len(code)
        6
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Calculate time counter
    counter = timestamp // period

    return _hotp(secret, counter, digits, algorithm)


def validate_totp_code(
    secret: str,
    code: str,
    timestamp: int | None = None,
    period: int = 30,
    digits: int = 6,
    algorithm: str = "SHA256",
    window: int = 1,
) -> bool:
    """Validate TOTP code with time window tolerance.

    Args:
        secret: Base32-encoded TOTP secret
        code: TOTP code to validate
        timestamp: Unix timestamp (default: current time)
        period: Time period in seconds (default: 30)
        digits: Number of digits (default: 6)
        algorithm: Hash algorithm (default: SHA256)
        window: Time window tolerance (±N periods, default: 1)

    Returns:
        True if code is valid within time window

    Example:
        >>> secret = "JBSWY3DPEHPK3PXP"
        >>> code = generate_totp_code(secret)
        >>> validate_totp_code(secret, code)
        True
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Try current time and window around it
    for offset in range(-window, window + 1):
        test_timestamp = timestamp + (offset * period)
        expected_code = generate_totp_code(
            secret, test_timestamp, period, digits, algorithm
        )
        if hmac.compare_digest(code, expected_code):
            return True

    return False


def verify_totp_code(
    secret: str,
    code: str,
    timestamp: int | None = None,
    period: int = 30,
    digits: int = 6,
    algorithm: str = "SHA256",
    window: int = 1,
) -> tuple[bool, int | None]:
    """Verify TOTP code and return time offset if valid.

    Args:
        secret: Base32-encoded TOTP secret
        code: TOTP code to verify
        timestamp: Unix timestamp (default: current time)
        period: Time period in seconds (default: 30)
        digits: Number of digits (default: 6)
        algorithm: Hash algorithm (default: SHA256)
        window: Time window tolerance (±N periods, default: 1)

    Returns:
        Tuple of (is_valid, time_offset_periods)
        time_offset_periods is None if invalid, 0 if current period, ±N if offset

    Example:
        >>> secret = "JBSWY3DPEHPK3PXP"
        >>> code = generate_totp_code(secret)
        >>> is_valid, offset = verify_totp_code(secret, code)
        >>> is_valid
        True
        >>> offset
        0
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Try current time and window around it
    for offset in range(-window, window + 1):
        test_timestamp = timestamp + (offset * period)
        expected_code = generate_totp_code(
            secret, test_timestamp, period, digits, algorithm
        )
        if hmac.compare_digest(code, expected_code):
            return True, offset

    return False, None


def get_provisioning_uri(
    secret: str,
    account_name: str,
    issuer: str = "Chrona",
    algorithm: str = "SHA256",
    digits: int = 6,
    period: int = 30,
) -> str:
    """Generate otpauth:// provisioning URI for QR code.

    Args:
        secret: Base32-encoded TOTP secret
        account_name: Account identifier (e.g., email)
        issuer: Service name (default: "Chrona")
        algorithm: Hash algorithm (default: SHA256)
        digits: Number of digits (default: 6)
        period: Time period in seconds (default: 30)

    Returns:
        otpauth:// URI string for QR code generation

    Example:
        >>> secret = "JBSWY3DPEHPK3PXP"
        >>> uri = get_provisioning_uri(secret, "user@example.com")
        >>> uri.startswith("otpauth://totp/")
        True
    """
    # URL-encode components
    encoded_issuer = quote(issuer)
    encoded_account = quote(account_name)

    # Build otpauth URI (RFC 6238 / Google Authenticator format)
    uri = (
        f"otpauth://totp/{encoded_issuer}:{encoded_account}"
        f"?secret={secret}"
        f"&issuer={encoded_issuer}"
        f"&algorithm={algorithm}"
        f"&digits={digits}"
        f"&period={period}"
    )

    return uri
