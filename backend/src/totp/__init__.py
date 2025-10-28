"""TOTP (Time-based One-Time Password) authentication module.

Implements secure TOTP authentication compliant with:
- RFC 6238 (TOTP: Time-Based One-Time Password Algorithm)
- Employee security spec: ≥160 bits entropy, Base32, SHA256, 6 digits, 30s period
- Kiosk security spec: ES256 JWT, nonce blacklist, rate limiting
"""

from .core import (
    generate_totp_code,
    generate_totp_secret,
    get_provisioning_uri,
    validate_totp_code,
    verify_totp_code,
)
from .encryption import decrypt_secret, encrypt_secret
from .provisioning import activate_totp, initiate_totp_provisioning

__all__ = [
    "generate_totp_secret",
    "generate_totp_code",
    "validate_totp_code",
    "verify_totp_code",
    "get_provisioning_uri",
    "encrypt_secret",
    "decrypt_secret",
    "initiate_totp_provisioning",
    "activate_totp",
]
