"""
Log Sanitizer - Masks secrets and sensitive data in logs
"""

import re
from typing import Any


# JWT pattern: xxxxx.yyyyy.zzzzz (base64-like)
JWT_PATTERN = re.compile(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")

# Common secret patterns
SECRET_PATTERNS = [
    (re.compile(r"Bearer\s+[A-Za-z0-9_-]+", re.IGNORECASE), "Bearer <REDACTED>"),
    (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', re.IGNORECASE), r'api_key="<REDACTED>"'),
    (
        re.compile(r'client[_-]?secret["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{10,})', re.IGNORECASE),
        r'client_secret="<REDACTED>"',
    ),
    (re.compile(r'token["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', re.IGNORECASE), r'token="<REDACTED>"'),
    (re.compile(r'password["\']?\s*[:=]\s*["\']?([^\s"\']+)', re.IGNORECASE), r'password="<REDACTED>"'),
    (re.compile(r"Feed token obtained:\s*([A-Za-z0-9_-]+)", re.IGNORECASE), "Feed token obtained: <REDACTED>"),
    (re.compile(r'jwtToken["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.-]+)', re.IGNORECASE), r'jwtToken="<REDACTED>"'),
    (re.compile(r'feed[_-]?token["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]+)', re.IGNORECASE), r'feed_token="<REDACTED>"'),
]


def sanitize_log_message(message: str) -> str:
    """
    Sanitize a log message by masking secrets.

    Args:
        message: Original log message

    Returns:
        Sanitized message with secrets masked
    """
    if not message or not isinstance(message, str):
        return str(message) if message is not None else ""

    sanitized = message

    # Mask JWT tokens
    sanitized = JWT_PATTERN.sub("<JWT_REDACTED>", sanitized)

    # Apply other secret patterns
    for pattern, replacement in SECRET_PATTERNS:
        if isinstance(replacement, str):
            sanitized = pattern.sub(replacement, sanitized)
        else:
            sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def sanitize_dict(data: dict, max_depth: int = 5) -> dict:
    """
    Recursively sanitize a dictionary by masking secrets in values.

    Args:
        data: Dictionary to sanitize
        max_depth: Maximum recursion depth

    Returns:
        Sanitized dictionary
    """
    if max_depth <= 0:
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_log_message(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[key] = [
                (
                    sanitize_dict(item, max_depth - 1)
                    if isinstance(item, dict)
                    else sanitize_log_message(item) if isinstance(item, str) else item
                )
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def scan_for_secrets(text: str) -> list:
    """
    Scan text for potential secrets.

    Args:
        text: Text to scan

    Returns:
        List of matched patterns (redacted)
    """
    found = []

    # Check for JWT
    jwt_matches = JWT_PATTERN.findall(text)
    if jwt_matches:
        found.append(f"JWT pattern: {len(jwt_matches)} matches")

    # Check for other patterns
    for pattern, _ in SECRET_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            found.append(f"{pattern.pattern[:30]}...: {len(matches)} matches")

    return found
