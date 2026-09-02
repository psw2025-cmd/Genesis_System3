"""
Genesis System3 — Native Windows DPAPI Local Secure Secret Vault
Provides OS-level encrypted local credential storage using
Windows DPAPI (CryptProtectData / CryptUnprotectData) tied to the user login/TPM.

Created By: Gemini CLI Laptop & Codex
Last Edited By: Gemini CLI Laptop
"""

import os
import sys
import json
import base64
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Optional, Dict, Any

VAULT_DIR = Path(os.environ.get("USERPROFILE", "C:\\Users\\ADMIN")) / ".genesis_vault"
VAULT_FILE = VAULT_DIR / "secrets.bin"
VAULT_ENTROPY = b"genesis_system3_dpapi_entropy_v1"

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]

CryptProtectData = ctypes.windll.crypt32.CryptProtectData
CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
LocalFree = ctypes.windll.kernel32.LocalFree

def _dpapi_encrypt(plaintext: bytes) -> bytes:
    """Encrypt bytes using Windows kernel DPAPI with optional entropy."""
    data_in = DATA_BLOB(len(plaintext), ctypes.cast(ctypes.create_string_buffer(plaintext), ctypes.POINTER(ctypes.c_byte)))
    entropy_in = DATA_BLOB(len(VAULT_ENTROPY), ctypes.cast(ctypes.create_string_buffer(VAULT_ENTROPY), ctypes.POINTER(ctypes.c_byte)))
    data_out = DATA_BLOB()
    # dwFlags = 0x01 (CRYPTPROTECT_UI_FORBIDDEN)
    if not CryptProtectData(ctypes.byref(data_in), "Genesis System3 Local Vault", ctypes.byref(entropy_in), None, None, 0x01, ctypes.byref(data_out)):
        raise ctypes.WinError()
    buf = ctypes.string_at(data_out.pbData, data_out.cbData)
    LocalFree(data_out.pbData)
    return buf

def _dpapi_decrypt(ciphertext: bytes) -> bytes:
    """Decrypt bytes using Windows kernel DPAPI."""
    data_in = DATA_BLOB(len(ciphertext), ctypes.cast(ctypes.create_string_buffer(ciphertext), ctypes.POINTER(ctypes.c_byte)))
    entropy_in = DATA_BLOB(len(VAULT_ENTROPY), ctypes.cast(ctypes.create_string_buffer(VAULT_ENTROPY), ctypes.POINTER(ctypes.c_byte)))
    data_out = DATA_BLOB()
    if not CryptUnprotectData(ctypes.byref(data_in), None, ctypes.byref(entropy_in), None, None, 0x01, ctypes.byref(data_out)):
        raise ctypes.WinError()
    buf = ctypes.string_at(data_out.pbData, data_out.cbData)
    LocalFree(data_out.pbData)
    return buf

def _read_all_secrets() -> Dict[str, str]:
    """Read and decrypt all secrets from local vault file."""
    if not VAULT_FILE.exists():
        return {}
    raw = VAULT_FILE.read_bytes()
    if not raw:
        return {}
    
    # 1. Try Native DPAPI Decrypt
    try:
        dec = _dpapi_decrypt(raw)
        return json.loads(dec.decode("utf-8"))
    except Exception:
        pass

    # 2. Backward compatibility fallback: Try Fernet decrypt and auto-migrate to DPAPI
    try:
        from cryptography.fernet import Fernet
        user = os.environ.get("USERNAME", "ADMIN")
        comp = os.environ.get("COMPUTERNAME", "LOCAL_HOST")
        import hashlib
        key = base64.urlsafe_b64encode(hashlib.sha256(f"{user}:{comp}:genesis_system3_local_vault_key".encode()).digest())
        f = Fernet(key)
        dec = f.decrypt(raw).decode("utf-8")
        secrets = json.loads(dec)
        # Auto-migrate to native DPAPI
        _write_all_secrets(secrets)
        return secrets
    except Exception:
        return {}

def _write_all_secrets(secrets: Dict[str, str]) -> bool:
    """Encrypt and write all secrets to local vault file."""
    try:
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        raw_json = json.dumps(secrets).encode("utf-8")
        encrypted = _dpapi_encrypt(raw_json)
        with open(VAULT_FILE, "wb") as fp:
            fp.write(encrypted)
        return True
    except Exception as exc:
        print(f"[VAULT] Error writing secrets: {exc}")
        return False

def save_secret(key: str, value: str) -> bool:
    """Save a secret encrypted with Windows DPAPI."""
    secrets = _read_all_secrets()
    secrets[key] = value
    return _write_all_secrets(secrets)

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve and decrypt a secret using Windows DPAPI."""
    # 1. Environment variable override
    if val := os.environ.get(key):
        return val
    # 2. Local DPAPI encrypted vault
    secrets = _read_all_secrets()
    return secrets.get(key, default)
