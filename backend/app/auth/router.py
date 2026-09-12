"""
Authentication router — Google OAuth 2.0 endpoints.

Endpoints:
    GET  /auth/login     → Returns Google authorization URL + CSRF state
    GET  /auth/callback  → Google redirects here; exchanges code, returns JWT
    GET  /auth/me        → Returns authenticated user's profile
    POST /auth/logout    → Revokes the current JWT (adds to Redis deny-list)
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.oauth import (
    get_google_auth_url,
    exchange_code_for_tokens,
    get_google_user_info,
)
from app.auth.jwt import create_access_token, decode_access_token
from app.auth.dependencies import get_current_user, deny_token
from app.db.session import get_db
from app.db.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("auth.router")

router = APIRouter(prefix="/auth", tags=["auth"])

# HTTPBearer for extracting raw token in logout
_bearer_scheme = HTTPBearer()

# ── In-memory CSRF state store ────────────────────────────────────────────────
# In production with multiple API replicas, move this to Redis.
# For a single-process deployment this is sufficient and avoids over-engineering.
_pending_states: set[str] = set()


from pydantic import BaseModel

class EmailLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(
    payload: EmailLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user with email and password.
    Returns a signed JWT on success.
    """
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format.",
        )

    if not payload.password or len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    repo = UserRepository(db)
    user = repo.register_by_email(email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Try signing in instead.",
        )

    logger.info(f"New user registered via email: {user.email} (id={user.id})")

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
        },
    }


@router.post("/email-login")
def email_login(
    payload: EmailLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing user using email and password.
    Generates and returns a signed JWT.
    """
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address format.",
        )

    if not payload.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required.",
        )

    repo = UserRepository(db)
    user = repo.login_by_email(email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    logger.info(f"User authenticated via email: {user.email} (id={user.id})")

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# GET /auth/login
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/login")
def login():
    """
    Start the Google OAuth flow.

    Returns the URL the client should redirect the user to, along with
    a CSRF state token that will be verified in the callback.
    """
    state = secrets.token_urlsafe(32)
    _pending_states.add(state)

    auth_url = get_google_auth_url(state)

    logger.info("OAuth login initiated")

    return {
        "auth_url": auth_url,
        "state": state,
    }


# ──────────────────────────────────────────────────────────────────────────────
# GET /auth/callback
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/callback")
async def callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    Google redirects here after the user authenticates.

    Steps:
      1. Verify CSRF state
      2. Exchange authorization code for tokens
      3. Extract user info from Google's ID token
      4. Upsert user in database (create on first login)
      5. Generate and return a signed JWT
    """
    # ── 1. CSRF check ────────────────────────────────────────────────────────
    if state not in _pending_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state parameter. "
                   "Please restart the login flow.",
        )
    _pending_states.discard(state)

    # ── 2. Exchange code for tokens ──────────────────────────────────────────
    try:
        token_data = await exchange_code_for_tokens(code)
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {e}",
        )

    # ── 3. Extract user info from ID token ───────────────────────────────────
    try:
        google_user = await get_google_user_info(token_data["id_token"])
    except Exception as e:
        logger.error(f"User info extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to verify Google ID token: {e}",
        )

    # ── 4. Upsert user ──────────────────────────────────────────────────────
    repo = UserRepository(db)
    user = repo.upsert_from_google(
        google_id=google_user["sub"],
        email=google_user["email"],
        name=google_user.get("name"),
        picture=google_user.get("picture"),
    )

    logger.info(f"User authenticated: {user.email} (id={user.id})")

    # ── 5. Generate JWT ──────────────────────────────────────────────────────
    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# GET /auth/me
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    """
    Return the currently authenticated user's profile.

    Requires a valid JWT in the Authorization header.
    """
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# POST /auth/logout
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    user: User = Depends(get_current_user),
):
    """
    Revoke the current JWT by adding its JTI to the Redis deny-list.

    The deny-list entry auto-expires when the token would have expired,
    so Redis memory is reclaimed automatically. After this call, any
    request using the same token will receive a 401.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    jti = payload.get("jti")
    exp = payload.get("exp")

    if jti and exp:
        # Calculate remaining lifetime — deny-list entry auto-expires with token
        now_ts = int(datetime.now(timezone.utc).timestamp())
        remaining = max(exp - now_ts, 0)
        deny_token(jti, ttl_seconds=remaining)

    logger.info(f"User logged out: {user.email}")

    return {"detail": "Successfully logged out"}
