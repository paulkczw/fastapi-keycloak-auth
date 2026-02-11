"""
FastAPI Keycloak Auth - Simple Keycloak authentication for FastAPI + Svelte.

Usage:
    from fastapi import FastAPI
    from fastapi_keycloak_auth import auth_router, CurrentUser, require_role

    app = FastAPI()
    app.include_router(auth_router)

    @app.get("/protected")
    async def protected(user: CurrentUser):
        return {"email": user.email}

    @app.get("/admin")
    async def admin(user = require_role("admin")):
        return {"message": "Hello admin"}

Environment Variables:
    KEYCLOAK_SERVER_URL: Keycloak server URL
    KEYCLOAK_REALM: Realm name
    KEYCLOAK_CLIENT_ID: OAuth2 client ID
    KEYCLOAK_CLIENT_SECRET: OAuth2 client secret
    KEYCLOAK_FRONTEND_URL: Frontend URL (default: http://localhost:5173)
    KEYCLOAK_BACKEND_URL: Backend URL (default: http://localhost:8000)
"""

# Load .env file on import
from dotenv import load_dotenv
load_dotenv()

from .config import KeycloakSettings
from .client import KeycloakClient
from .models import TokenPayload, User, AuthStatus, TokenResponse
from .events import (
    AuthEvent,
    AuthEventEmitter,
    LoginEventData,
    LogoutEventData,
    RefreshEventData,
    TokenVerifiedEventData,
    TokenInvalidEventData,
    auth_events,
)
from .dependencies import (
    CurrentUser,
    OptionalUser,
    get_current_user,
    get_current_user_optional,
    get_keycloak_client,
    get_settings,
    require_role,
    require_any_role,
    clear_settings_cache,
    clear_client_cache,
)
from .router import auth_router, create_auth_router

__all__ = [
    # Config
    "KeycloakSettings",
    # Client
    "KeycloakClient",
    # Models
    "TokenPayload",
    "User",
    "AuthStatus",
    "TokenResponse",
    # Events
    "AuthEvent",
    "AuthEventEmitter",
    "LoginEventData",
    "LogoutEventData",
    "RefreshEventData",
    "TokenVerifiedEventData",
    "TokenInvalidEventData",
    "auth_events",
    # Dependencies
    "CurrentUser",
    "OptionalUser",
    "get_current_user",
    "get_current_user_optional",
    "get_keycloak_client",
    "get_settings",
    "require_role",
    "require_any_role",
    "clear_settings_cache",
    "clear_client_cache",
    # Router
    "auth_router",
    "create_auth_router",
]

__version__ = "1.0.0"