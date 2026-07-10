"""
JWT token creation and verification.

Design:
  - HS256 (symmetric) signing — the backend is the only party that creates
    and verifies tokens, so asymmetric RS256 adds complexity without benefit.
  - Tokens carry ``sub`` (user_id), ``email``, ``jti`` (unique token ID for
    logout/deny-listing), and ``exp`` (expiry).
  - Token deny-listing for logout is handled at the dependency layer
    (dependencies.py), not here — this module is pure encode/decode.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt  # PyJWT

from app.core.config import settings


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id:       User's primary key (stored as ``sub`` claim).
        email:         User's email (stored as ``email`` claim).
        expires_delta: Custom expiry duration. Defaults to JWT_EXPIRE_MINUTES
                       from settings.

    Returns:
        Encoded JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "email": email,
        "jti": str(uuid.uuid4()),       # unique ID — used for deny-listing
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: The raw JWT string from the Authorization header.

    Returns:
        The decoded payload dict with keys: sub, email, jti, iat, exp.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError:    Token is malformed or signature is invalid.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
