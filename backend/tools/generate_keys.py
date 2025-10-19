#!/usr/bin/env python3
"""Generate RS256 key pair for JWT signing.

This script generates a private/public key pair for RS256 JWT signatures.
Keys are saved to the backend/ directory by default.

Usage:
    python tools/generate_keys.py [--output-dir path/to/keys]
"""

import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys(output_dir: Path, key_size: int = 2048):
    """Generate RS256 key pair and save to files.

    Args:
        output_dir: Directory to save keys
        key_size: RSA key size in bits (default: 2048)
    """
    print(f"Generating {key_size}-bit RSA key pair...")

    # Generate private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Generate public key
    public_key = private_key.public_key()

    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save keys to files
    private_key_path = output_dir / "jwt_private_key.pem"
    public_key_path = output_dir / "jwt_public_key.pem"

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    print(f"[OK] Private key saved to: {private_key_path}")
    print(f"[OK] Public key saved to: {public_key_path}")
    print("\n[WARNING] IMPORTANT SECURITY NOTES:")
    print("1. Add 'jwt_private_key.pem' to .gitignore (NEVER commit it)")
    print("2. Store private key securely (AWS KMS, GCP Secret Manager, etc. in production)")
    print("3. Public key can be distributed to kiosks for validation")
    print("\n[INFO] Add to .env:")
    print(f'JWT_PRIVATE_KEY_PATH="{private_key_path.absolute()}"')
    print(f'JWT_PUBLIC_KEY_PATH="{public_key_path.absolute()}"')


def main():
    parser = argparse.ArgumentParser(
        description="Generate RS256 key pair for JWT signing"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Directory to save keys (default: backend/)",
    )
    parser.add_argument(
        "--key-size",
        type=int,
        default=2048,
        choices=[2048, 4096],
        help="RSA key size in bits (default: 2048)",
    )

    args = parser.parse_args()
    generate_keys(args.output_dir, args.key_size)


if __name__ == "__main__":
    main()
