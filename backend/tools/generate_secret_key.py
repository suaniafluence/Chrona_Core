#!/usr/bin/env python3
"""
Generate secure SECRET_KEY for Chrona backend.

Usage:
    python tools/generate_secret_key.py              # Generate and display
    python tools/generate_secret_key.py --env dev    # Generate and append to .env.dev
    python tools/generate_secret_key.py --env prod   # Generate and append to .env.prod
"""

import argparse
import secrets
import sys
from pathlib import Path


def generate_secret_key(length: int = 64) -> str:
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(length)


def main():
    parser = argparse.ArgumentParser(
        description="Generate secure SECRET_KEY for Chrona backend"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=64,
        help="Key length in characters (default: 64)",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "prod"],
        help="Append to .env.{env} file (default: just display)",
    )
    parser.add_argument(
        "--no-urlsafe",
        action="store_true",
        help="Use base64 instead of URL-safe encoding",
    )

    args = parser.parse_args()

    # Generate the key
    if args.no_urlsafe:
        # Use base64 encoding (like openssl rand -base64)
        import base64

        random_bytes = secrets.token_bytes(args.length)
        secret_key = base64.b64encode(random_bytes).decode("utf-8").rstrip("\n")
    else:
        # Use URL-safe encoding (more secure, no special chars issues)
        secret_key = generate_secret_key(args.length)

    # Display
    print(f"Generated SECRET_KEY ({len(secret_key)} chars):")
    print(f"  {secret_key}")
    print()

    if args.env:
        # Append to .env file
        env_file = Path(__file__).parent.parent / f".env.{args.env}"
        try:
            with open(env_file, "a") as f:
                f.write(f"\nSECRET_KEY={secret_key}\n")
            print(f"✓ Appended to {env_file}")
            print(f"  Verify with: grep SECRET_KEY {env_file}")
        except Exception as e:
            print(f"✗ Error writing to {env_file}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
