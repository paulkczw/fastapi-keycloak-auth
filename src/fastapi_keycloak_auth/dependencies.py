"""
FastAPI dependencies for authentication.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError

from .client import KeycloakClient
from .config import KeycloakSettings
from .events import (
    AuthEvent,
    TokenInvalidEventData,
    TokenVerifiedEventData,
    auth_events,
)
from .models import TokenPayload


# =============================================================================
# Singleton instances
# =============================================================================

_settings: KeycloakSettings | None = None
_client: KeycloakClient | None = None


def get_settings() -> KeycloakSettings:
    """
    Get Keycloak settings (singleton).

    Settings are loaded from environment variables with KEYCLOAK_ prefix.
    Raises ValidationError if required settings are missing.
    """
    global _settings
    if _settings is None:
        _settings = KeycloakSettings()  # type: ignore[call-arg]
    return _settings


def get_keycloak_client() -> KeycloakClient:
    """Get Keycloak client (singleton)."""
    global _client
    if _client is None:
        _client = KeycloakClient(get_settings())
    return _client


def clear_settings_cache() -> None:
    """Clear settings cache (useful for testing)."""
    global _settings, _client
    _settings = None
    _client = None


def clear_client_cache() -> None:
    """Clear client cache (useful for testing)."""
    global _client
    _client = None


# =============================================================================
# Auth Dependencies
# =============================================================================

async def get_current_user(request: Request) -> TokenPayload:
    """
    Dependency to get the current authenticated user.

    Extracts token from cookie or Authorization header and validates it.

    Raises:
        HTTPException: 401 if not authenticated or token is invalid
    """
    settings = get_settings()
    client = get_keycloak_client()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get token from cookie (using configured name) or header
    token = request.cookies.get(settings.cookie_name)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")

    if not token:
        raise credentials_exception

    try:
        user = await client.verify_token(token)

        # Emit TOKEN_VERIFIED event
        if auth_events.has_handlers(AuthEvent.TOKEN_VERIFIED):
            await auth_events.emit(AuthEvent.TOKEN_VERIFIED, TokenVerifiedEventData(user=user))

        return user
    except JWTError as e:
        # Emit TOKEN_INVALID event
        if auth_events.has_handlers(AuthEvent.TOKEN_INVALID):
            await auth_events.emit(AuthEvent.TOKEN_INVALID, TokenInvalidEventData(error=str(e), token=token))

        raise credentials_exception from e


async def get_current_user_optional(request: Request) -> TokenPayload | None:
    """
    Dependency to get the current user if authenticated, None otherwise.

    Does not raise an exception if not authenticated.
    """
    settings = get_settings()
    client = get_keycloak_client()

    token = request.cookies.get(settings.cookie_name)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")

    if not token:
        return None

    try:
        result = await client.verify_token(token)
        # Emit TOKEN_VERIFIED event
        if auth_events.has_handlers(AuthEvent.TOKEN_VERIFIED):
            await auth_events.emit(AuthEvent.TOKEN_VERIFIED, TokenVerifiedEventData(user=result))
        return result
    except JWTError as e:
        # Emit TOKEN_INVALID event
        if auth_events.has_handlers(AuthEvent.TOKEN_INVALID):
            await auth_events.emit(AuthEvent.TOKEN_INVALID, TokenInvalidEventData(error=str(e), token=token))
        return None


def require_role(role: str):
    """
    Dependency factory to require a specific realm role.

    Usage:
        @app.get("/admin")
        async def admin(user = Depends(require_role("admin"))):
            ...
    """

    async def role_checker(request: Request) -> TokenPayload:
        user = await get_current_user(request)
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return user

    return role_checker


def require_any_role(*roles: str):
    """
    Dependency factory to require any of the specified roles.

    Usage:
        @app.get("/staff")
        async def staff(user = Depends(require_any_role("admin", "moderator"))):
            ...
    """

    async def role_checker(request: Request) -> TokenPayload:
        user = await get_current_user(request)
        if not any(user.has_role(role) for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {roles} required",
            )
        return user

    return role_checker


# =============================================================================
# Type aliases for cleaner dependency injection
# =============================================================================

CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
OptionalUser = Annotated[TokenPayload | None, Depends(get_current_user_optional)]