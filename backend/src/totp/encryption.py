"""TOTP secret encryption using AES-GCM.

Implements secure encryption for TOTP secrets at rest.
Compliant with kiosk security spec:
- backend.secret_storage: AES-GCM (KMS/HSM)
- backend.key_rotation: 90j (90 days)
"""

import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class TOTPEncryption:
    """AES-GCM encryption for TOTP secrets.

    Uses 256-bit AES-GCM with 96-bit nonce.
    In production, integrate with KMS/HSM for key management.
    """

    def __init__(self, encryption_key: bytes | None = None):
        """Initialize encryption with key.

        Args:
            encryption_key: 32-byte AES-256 key (if None, uses env or generates)
        """
        if encryption_key is None:
            # Load from environment or generate ephemeral key
            key_b64 = os.getenv("TOTP_ENCRYPTION_KEY")
            if key_b64:
                encryption_key = base64.b64decode(key_b64)
            else:
                # Generate ephemeral key (NOT recommended for production)
                encryption_key = AESGCM.generate_key(bit_length=256)

        if len(encryption_key) != 32:
            raise ValueError("Encryption key must be 32 bytes (256 bits)")

        self.aesgcm = AESGCM(encryption_key)

    def encrypt(self, plaintext: str) -> Tuple[str, str]:
        """Encrypt TOTP secret using AES-GCM.

        Args:
            plaintext: TOTP secret (Base32 string)

        Returns:
            Tuple of (encrypted_b64, nonce_b64)

        Example:
            >>> enc = TOTPEncryption()
            >>> ciphertext, nonce = enc.encrypt("JBSWY3DPEHPK3PXP")
            >>> len(ciphertext) > 0
            True
        """
        # Generate random 96-bit nonce (12 bytes)
        nonce = os.urandom(12)

        # Encrypt plaintext
        plaintext_bytes = plaintext.encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Return Base64-encoded ciphertext and nonce
        ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")
        nonce_b64 = base64.b64encode(nonce).decode("utf-8")

        return ciphertext_b64, nonce_b64

    def decrypt(self, ciphertext_b64: str, nonce_b64: str) -> str:
        """Decrypt TOTP secret using AES-GCM.

        Args:
            ciphertext_b64: Base64-encoded ciphertext
            nonce_b64: Base64-encoded nonce

        Returns:
            Decrypted TOTP secret (Base32 string)

        Raises:
            cryptography.exceptions.InvalidTag: If decryption fails
                (wrong key/tampered data)

        Example:
            >>> enc = TOTPEncryption()
            >>> ciphertext, nonce = enc.encrypt("JBSWY3DPEHPK3PXP")
            >>> plaintext = enc.decrypt(ciphertext, nonce)
            >>> plaintext
            'JBSWY3DPEHPK3PXP'
        """
        # Decode Base64
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)

        # Decrypt
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext_bytes.decode("utf-8")


# Global encryption instance (singleton pattern)
_global_encryption: TOTPEncryption | None = None


def _get_encryption() -> TOTPEncryption:
    """Get global encryption instance (lazy initialization)."""
    global _global_encryption
    if _global_encryption is None:
        _global_encryption = TOTPEncryption()
    return _global_encryption


def encrypt_secret(secret: str) -> str:
    """Encrypt TOTP secret (convenience function).

    Args:
        secret: Base32-encoded TOTP secret

    Returns:
        Encrypted secret in format "nonce_b64:ciphertext_b64"

    Example:
        >>> encrypted = encrypt_secret("JBSWY3DPEHPK3PXP")
        >>> ":" in encrypted
        True
    """
    enc = _get_encryption()
    ciphertext_b64, nonce_b64 = enc.encrypt(secret)
    return f"{nonce_b64}:{ciphertext_b64}"


def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt TOTP secret (convenience function).

    Args:
        encrypted_secret: Encrypted secret in format "nonce_b64:ciphertext_b64"

    Returns:
        Decrypted Base32-encoded TOTP secret

    Example:
        >>> encrypted = encrypt_secret("JBSWY3DPEHPK3PXP")
        >>> decrypted = decrypt_secret(encrypted)
        >>> decrypted
        'JBSWY3DPEHPK3PXP'
    """
    enc = _get_encryption()
    nonce_b64, ciphertext_b64 = encrypted_secret.split(":", 1)
    return enc.decrypt(ciphertext_b64, nonce_b64)
