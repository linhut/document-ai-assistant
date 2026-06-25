# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Encryption utilities for sensitive data (API keys, etc.).

密钥文件存储在 APP_DATA_DIR/，由 config.py 统一管理路径。
"""
from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path

from config import APP_DATA_DIR


# 密钥文件路径（位于 APP_DATA_DIR 根目录）
_KEY_FILE = str(APP_DATA_DIR / ".encryption_key")


def _get_or_create_key() -> bytes:
    """Get existing encryption key or create new one."""
    os.makedirs(os.path.dirname(_KEY_FILE), exist_ok=True)

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(_KEY_FILE, "wb") as f:
            f.write(key)
        return key


_CIPHER = Fernet(_get_or_create_key())


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value."""
    encrypted = _CIPHER.encrypt(plaintext.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_value(encrypted: str) -> str:
    """Decrypt an encrypted string value."""
    if not encrypted:
        return ""
    encrypted_bytes = base64.b64decode(encrypted.encode())
    decrypted = _CIPHER.decrypt(encrypted_bytes)
    return decrypted.decode()
