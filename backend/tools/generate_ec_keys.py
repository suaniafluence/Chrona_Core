"""Generate EC (ECDSA P-256) keys for ES256 JWT signing.

Compliant with kiosk security spec:
- qr_auth.format: JWT (ES256)
- scanner_auth.method: JWT (ES256)

ES256 advantages over RS256:
- Smaller signatures (64 bytes vs 256 bytes)
- Faster signing/verification
- Equivalent security with smaller keys (256-bit vs 2048-bit)
"""

import argparse
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def generate_ec_keys(
    private_key_path: Path, public_key_path: Path, curve: ec.EllipticCurve = ec.SECP256R1()
) -> None:
    """Generate ECDSA key pair for ES256 JWT signing.

    Args:
        private_key_path: Path to save private key (PEM format)
        public_key_path: Path to save public key (PEM format)
        curve: Elliptic curve (default: SECP256R1 / P-256)
    """
    # Generate private key
    private_key = ec.generate_private_key(curve, default_backend())

    # Serialize private key to PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Extract public key
    public_key = private_key.public_key()

    # Serialize public key to PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Write keys to files
    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    public_key_path.parent.mkdir(parents=True, exist_ok=True)

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    # Set restrictive permissions (Unix only)
    try:
        private_key_path.chmod(0o600)  # Owner read/write only
        public_key_path.chmod(0o644)  # Owner read/write, others read
    except Exception:
        pass  # Windows doesn't support chmod

    print(f"✅ EC private key (ES256) saved to: {private_key_path}")
    print(f"✅ EC public key (ES256) saved to: {public_key_path}")
    print()
    print("Key information:")
    print(f"  Curve: SECP256R1 (P-256)")
    print(f"  Algorithm: ES256 (ECDSA with SHA-256)")
    print(f"  Private key size: {len(private_pem)} bytes")
    print(f"  Public key size: {len(public_pem)} bytes")
    print()
    print("Configuration:")
    print(f"  Set ALGORITHM=ES256 in .env")
    print(f"  Set JWT_PRIVATE_KEY_PATH={private_key_path}")
    print(f"  Set JWT_PUBLIC_KEY_PATH={public_key_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate EC (ECDSA P-256) keys for ES256 JWT signing"
    )
    parser.add_argument(
        "--private-key",
        type=Path,
        default=Path("jwt_ec_private_key.pem"),
        help="Path to save private key (default: jwt_ec_private_key.pem)",
    )
    parser.add_argument(
        "--public-key",
        type=Path,
        default=Path("jwt_ec_public_key.pem"),
        help="Path to save public key (default: jwt_ec_public_key.pem)",
    )

    args = parser.parse_args()

    generate_ec_keys(args.private_key, args.public_key)


if __name__ == "__main__":
    main()
