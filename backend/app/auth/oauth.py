"""
Google OAuth 2.0 server-side flow.

Handles:
  1. Building the authorization URL the client should redirect to.
  2. Exchanging the authorization code for tokens.
  3. Extracting user info from Google's ID token.

Uses httpx (already in the project) for HTTP calls.
Uses Google's tokeninfo endpoint to verify ID tokens rather than doing
local JWT verification — avoids managing Google's rotating public keys.
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

import httpx

from app.core.config import settings

logger = logging.getLogger("auth.oauth")

# ── Google OAuth endpoints ────────────────────────────────────────────────────
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

# Scopes: openid for ID token, email + profile for user info
SCOPES = "openid email profile"


def get_google_auth_url(state: str) -> str:
    """
    Build the Google authorization URL the client should redirect to.

    Args:
        state: A random CSRF token. Google echoes it back in the callback
               so we can verify the request originated from us.

    Returns:
        Full URL string the client should navigate to.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",       # get refresh_token on first consent
        "state": state,
        "prompt": "consent",            # always show consent screen
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    logger.info("Generated Google auth URL")
    return url


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchange the authorization code for an ID token + access token.

    Args:
        code: The authorization code from Google's callback.

    Returns:
        Dict with keys: id_token, access_token, refresh_token (if present),
        token_type, expires_in.

    Raises:
        httpx.HTTPStatusError: If Google's token endpoint returns a non-2xx.
        ValueError: If the response is missing expected fields.
    """
    payload = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=payload)
        response.raise_for_status()

    data = response.json()

    if "id_token" not in data:
        raise ValueError(
            "Google token response missing 'id_token'. "
            f"Keys received: {list(data.keys())}"
        )

    logger.info("Exchanged authorization code for tokens")
    return data


async def get_google_user_info(id_token: str) -> dict:
    """
    Verify and decode a Google ID token using Google's tokeninfo endpoint.

    Returns a dict with at least:
        sub     — Google's stable user ID
        email   — user's email
        name    — display name (may be absent)
        picture — profile picture URL (may be absent)

    Raises:
        httpx.HTTPStatusError: If the tokeninfo endpoint rejects the token.
        ValueError: If required fields are missing.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_TOKENINFO_URL,
            params={"id_token": id_token},
        )
        response.raise_for_status()

    info = response.json()

    # Verify the token was issued for our client
    if info.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise ValueError(
            f"ID token audience mismatch: expected {settings.GOOGLE_CLIENT_ID}, "
            f"got {info.get('aud')}"
        )

    if "sub" not in info or "email" not in info:
        raise ValueError(
            f"ID token missing required claims. Got: {list(info.keys())}"
        )

    logger.info(f"Verified Google user: {info['email']}")
    return {
        "sub": info["sub"],
        "email": info["email"],
        "name": info.get("name"),
        "picture": info.get("picture"),
    }
