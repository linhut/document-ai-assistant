# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.

"""
Authentication middleware for the API.

Token-based authentication for sensitive endpoints.
Token is auto-generated on first start and stored in data/.auth_token.
"""
import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import APP_DATA_DIR
from utils.logger import logger

_TOKEN_FILE = APP_DATA_DIR / ".auth_token"

# Public paths that do NOT require authentication
_PUBLIC_PATHS: set[str] = {
    "/api/health",
    "/api/office/health",
    "/api/office/check",
    "/api/office/fix",
    "/api/office/ai-optimize",
    "/api/office/templates",
    "/api/office/apply-template",
    "/api/office/generate-template",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/",
}


def _get_or_create_token() -> str:
    """Load token from disk, or generate and persist a new one."""
    os.makedirs(os.path.dirname(_TOKEN_FILE), exist_ok=True)
    if _TOKEN_FILE.exists():
        content = _TOKEN_FILE.read_text(encoding="utf-8").strip()
        if content:
            return content
    token = secrets.token_urlsafe(32)
    _TOKEN_FILE.write_text(token, encoding="utf-8")
    return token


# Module-level token cache (set on first access)
_AUTH_TOKEN: Optional[str] = None


def init_auth() -> None:
    """Initialize the auth module (call once at startup)."""
    global _AUTH_TOKEN
    _AUTH_TOKEN = _get_or_create_token()
    logger.info("Auth module initialized")


def get_auth_token() -> str:
    """Return the current auth token, initializing lazily if needed."""
    global _AUTH_TOKEN
    if _AUTH_TOKEN is None:
        _AUTH_TOKEN = _get_or_create_token()
    return _AUTH_TOKEN


def regenerate_token() -> str:
    """Generate a new token, persist it, and return it."""
    global _AUTH_TOKEN
    os.makedirs(os.path.dirname(_TOKEN_FILE), exist_ok=True)
    token = secrets.token_urlsafe(32)
    _TOKEN_FILE.write_text(token, encoding="utf-8")
    _AUTH_TOKEN = token
    logger.info("Auth token regenerated")
    return token


class AuthMiddleware(BaseHTTPMiddleware):
    """Bearer Token authentication middleware for FastAPI."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Public endpoints: health checks, docs, static assets
        if path in _PUBLIC_PATHS:
            return await call_next(request)

        if path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Static file extensions do not need auth
        if path.endswith((".js", ".css", ".ico", ".png", ".svg", ".woff", ".woff2")):
            return await call_next(request)

        # Validate Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token and secrets.compare_digest(token, get_auth_token()):
                return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized: valid Bearer token required"},
        )
