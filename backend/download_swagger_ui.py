#!/usr/bin/env python3
"""Download Swagger UI files for offline use."""
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def download_swagger_ui():
    """Download Swagger UI files from unpkg CDN."""
    output_dir = Path("/app/static/swagger-ui")
    output_dir.mkdir(parents=True, exist_ok=True)

    base_url = "https://unpkg.com/swagger-ui-dist@5/"
    files = [
        "swagger-ui.css",
        "swagger-ui-bundle.js",
        "swagger-ui-standalone-preset.js",
        "favicon-16x16.png",
        "favicon-32x32.png",
    ]

    for filename in files:
        url = base_url + filename
        output_path = output_dir / filename
        print(f"Downloading {filename}...", end=" ", flush=True)
        try:
            # Validate URL scheme to prevent file:// attacks
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https"):
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")
            # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected
            # URL is hardcoded, not user-controlled, and scheme is validated
            urllib.request.urlretrieve(url, str(output_path))
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")


if __name__ == "__main__":
    download_swagger_ui()
