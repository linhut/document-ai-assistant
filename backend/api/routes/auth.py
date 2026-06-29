# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.

"""
Authentication API routes.

Provides token management endpoints (view / refresh).
All endpoints in this router require a valid Bearer token.
"""
from fastapi import APIRouter

from auth import get_auth_token, regenerate_token

router = APIRouter()


@router.get("/token")
async def get_token():
    """Return the current auth token (masked only, never expose full token via API)."""
    token = get_auth_token()
    masked = token[:4] + "****" + token[-4:] if len(token) > 8 else "****"
    return {
        "masked": masked,
        "message": "Token is stored locally. Use the console output on first startup.",
    }


@router.post("/refresh")
async def refresh_token():
    """Regenerate the auth token. The old token becomes invalid."""
    new_token = regenerate_token()
    masked = new_token[:4] + "****" + new_token[-4:] if len(new_token) > 8 else "****"
    return {
        "masked": masked,
        "message": "Token refreshed. Check the server console for the new token.",
    }
