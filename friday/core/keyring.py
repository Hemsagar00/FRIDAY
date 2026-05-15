"""FRIDAY Keyring — Secure API key storage.

Reads from D:\Friday\.env (primary), then environment variables.
"""

import os
from pathlib import Path
from typing import Optional


def _read_env_file():
    """Read D:\Friday\.env (Windows) or ~/Friday/.env (fallback)."""
    # Primary: D:\Friday\.env on Windows
    env_path = Path("D:/Friday/.env")
    if not env_path.exists():
        # Fallback: project root .env
        env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            if value and key not in os.environ:
                os.environ[key] = value


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get API key by name. Checks env > D:\Friday\.env > default."""
    _read_env_file()
    return os.environ.get(key, default)


def require(key: str) -> str:
    """Get key or raise RuntimeError."""
    value = get(key)
    if not value:
        raise RuntimeError(f"Missing required API key: {key}. Set in D:\\Friday\\.env or environment.")
    return value
