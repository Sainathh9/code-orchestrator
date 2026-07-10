"""
FastAPI authentication dependencies.

Usage in any route:

    from app.auth.dependencies import get_current_user
    from app.db.models.user import User

    @router.get("/protected")
    def protected_route(user: User = Depends(get_current_user)):
        return {"email": user.email}

The dependency extracts the Bearer token from the Authorization header,
decodes the JWT, checks the Redis deny-list (for logged-out tokens),
fetches the User from the database, and verifies the account is active.
"""

from __future__ import annotations

import logging

import jwt as pyjwt  # PyJWT
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.db.session import get_db
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.queue.connection import redis_conn

logger = logging.getLogger("auth.dependencies")

# HTTPBearer extracts 'Authorization: Bearer <token>' and raises 403 if missing
_bearer_scheme = HTTPBearer()

# Redis key prefix for denied (logged-out) token JTIs
_DENY_PREFIX = "token:denied:"


def _is_token_denied(jti: str) -> bool:
    """Check if a token's JTI has been added to the Redis deny-list."""
    return redis_conn.exists(f"{_DENY_PREFIX}{jti}") > 0


def deny_token(jti: str, ttl_seconds: int) -> None:
    """
    Add a token's JTI to the Redis deny-list.

    Called by the logout endpoint. The TTL matches the token's remaining
    lifetime so denied entries auto-expire and don't leak memory.
    """
    redis_conn.setex(f"{_DENY_PREFIX}{jti}", ttl_seconds, "1")
    logger.info(f"Token denied: jti={jti}, ttl={ttl_seconds}s")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that authenticates the current request.

    Extracts the JWT from the Authorization header, validates it,
    checks the deny-list, and returns the User ORM object.

    Raises:
        HTTPException 401: On expired, invalid, or denied tokens,
                           or if the user is not found / deactivated.
    """
    token = credentials.credentials

    # ── 1. Decode and verify JWT signature + expiry ───────────────────────────
    try:
        payload = decode_access_token(token)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── 2. Check deny-list (logged-out tokens) ───────────────────────────────
    jti = payload.get("jti")
    if jti and _is_token_denied(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── 3. Fetch user from database ──────────────────────────────────────────
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
