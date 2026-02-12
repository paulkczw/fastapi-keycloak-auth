"""
FastAPI router with authentication endpoints.
"""

from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from jose import JWTError

from .dependencies import (
    get_current_user,
    get_current_user_optional,
    get_keycloak_client,
    get_settings,
)
from .events import (
    AuthEvent,
    LoginEventData,
    LogoutEventData,
    RefreshEventData,
    auth_events, TokenInvalidEventData,
)
from .models import AuthStatus, TokenPayload, User


def create_auth_router(
    prefix: str | None = None,
    tags: list[str] | None = None,
) -> APIRouter:
    """
    Create an authentication router with Keycloak endpoints.

    Args:
        prefix: URL prefix for all routes. If None, uses KEYCLOAK_AUTH_PATH
                from settings (default: /auth). Examples: /auth, /auth/keycloak
        tags: OpenAPI tags for the routes

    Returns:
        Configured APIRouter

    Endpoints:
        GET {prefix}/login - Redirect to Keycloak login
        GET {prefix}/callback - OAuth2 callback handler
        GET {prefix}/logout - Logout and clear session
        GET {prefix}/logout-callback - Logout callback from Keycloak
        GET {prefix}/refresh - Refresh access token
        GET {prefix}/me - Get current user info
        GET {prefix}/status - Check authentication status

    Example:
        # Default: /auth/*
        app.include_router(auth_router)

        # Custom path: /auth/keycloak/*
        keycloak_router = create_auth_router(prefix="/auth/keycloak")
        app.include_router(keycloak_router)
    """
    # Use prefix from settings if not provided
    if prefix is None:
        prefix = get_settings().auth_path

    router = APIRouter(prefix=prefix, tags=tags or ["auth"])

    @router.get("/login")
    async def login(
        redirect: str | None = Query(default=None, description="URL to redirect after login"),
    ):
        """
        Initiate OAuth2 login flow.

        Redirects to Keycloak login page. After successful login,
        user is redirected back to /auth/callback.
        """
        settings = get_settings()
        client = get_keycloak_client()
        openid_configuration = await client.get_openid_configuration()

        params = {
            "client_id": settings.client_id,
            "response_type": "code",
            "scope": settings.scopes,
            "redirect_uri": settings.callback_url,
        }

        # Store redirect URL in state parameter if provided
        if redirect:
            params["state"] = redirect

        return RedirectResponse(f"{openid_configuration.authorization_endpoint}?{urlencode(params)}")

    @router.get("/callback")
    async def callback(
        code: str,
        state: str | None = None,
    ):
        """
        OAuth2 callback handler.

        Exchanges authorization code for tokens and sets them as cookies.
        Redirects to frontend after successful authentication.
        """
        settings = get_settings()
        client = get_keycloak_client()

        try:
            tokens = await client.exchange_code(code)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to exchange code for token",
            ) from e

        # Determine redirect URL
        redirect_url = state if state else settings.post_login_redirect

        response = RedirectResponse(url=redirect_url, status_code=302)

        # Set access token cookie
        response.set_cookie(
            key=settings.cookie_name,
            value=tokens.access_token,
            httponly=settings.cookie_httponly,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            max_age=tokens.expires_in,
        )

        # Set refresh token cookie if available
        if tokens.refresh_token:
            response.set_cookie(
                key=settings.refresh_cookie_name,
                value=tokens.refresh_token,
                httponly=settings.cookie_httponly,
                secure=settings.cookie_secure,
                samesite=settings.cookie_samesite,
            )

            try:
                user = await client.verify_token(tokens.access_token)
                # Emit LOGIN event
                if auth_events.has_handlers(AuthEvent.LOGIN):
                    await auth_events.emit(AuthEvent.LOGIN, LoginEventData(user=user, tokens=tokens))
            except JWTError as e:
                # Emit TOKEN_INVALID event
                if auth_events.has_handlers(AuthEvent.TOKEN_INVALID):
                    auth_events.emit(AuthEvent.TOKEN_INVALID, TokenInvalidEventData(error=str(e), token=tokens.access_token))

        return response

    @router.get("/logout")
    async def logout(
        request: Request,
        redirect: str | None = Query(default=None, description="URL to redirect after logout"),
    ):
        """
        Logout user.

        Clears authentication cookies and redirects to Keycloak logout.
        After Keycloak logout, user is redirected to {auth_path}/logout-callback,
        which then redirects to the frontend.
        """
        settings = get_settings()
        client = get_keycloak_client()
        openid_configuration = await client.get_openid_configuration()

        # Try to get user for event (may be None if token expired)
        user = None
        token = request.cookies.get(settings.cookie_name)
        if token:
            try:
                user = await client.verify_token(token)
            except JWTError as e:
                if auth_events.has_handlers(AuthEvent.TOKEN_INVALID):
                    await auth_events.emit(AuthEvent.TOKEN_INVALID, TokenInvalidEventData(error=str(e), token=token))

            if auth_events.has_handlers(AuthEvent.LOGOUT):
                await auth_events.emit(AuthEvent.LOGOUT, LogoutEventData(user=user))

        # Use the logout callback URL from settings (includes auth_path)
        callback_url = settings.logout_callback_url
        if redirect:
            callback_url = f"{callback_url}?redirect={redirect}"

        params = {
            "client_id": settings.client_id,
            "post_logout_redirect_uri": callback_url,
        }

        response = RedirectResponse(f"{openid_configuration.end_session_endpoint}?{urlencode(params)}")
        response.delete_cookie(settings.cookie_name)
        response.delete_cookie(settings.refresh_cookie_name)

        return response

    @router.get("/logout-callback")
    async def logout_callback(
        redirect: str | None = Query(default=None, description="URL to redirect to"),
    ):
        """
        Logout callback handler.

        Called by Keycloak after logout. Redirects to frontend.
        This allows Keycloak to only whitelist backend URLs.
        """
        settings = get_settings()

        redirect_url = redirect if redirect else settings.post_logout_redirect

        # Ensure cookies are cleared (belt and suspenders)
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.delete_cookie(settings.cookie_name)
        response.delete_cookie(settings.refresh_cookie_name)

        return response

    @router.post("/refresh")
    async def refresh(
        request: Request,
        refresh_token: str | None = None,
    ):
        """
        Refresh access token.

        Uses refresh token from cookie or request body to get new tokens.
        """
        settings = get_settings()
        client = get_keycloak_client()

        # Get refresh token from cookie if not provided in body
        if not refresh_token:
            refresh_token = request.cookies.get(settings.refresh_cookie_name)

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token required",
            )

        try:
            tokens = await client.refresh_tokens(refresh_token)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token",
            ) from e

        # Emit REFRESH event
        if auth_events.has_handlers(AuthEvent.REFRESH):
            await auth_events.emit(AuthEvent.REFRESH, RefreshEventData(tokens=tokens))

        return {
            "access_token": tokens.access_token,
            "expires_in": tokens.expires_in,
        }

    @router.get("/me", response_model=User)
    async def get_me(user: TokenPayload = Depends(get_current_user)):
        """
        Get current authenticated user.

        Returns user information from the JWT token.
        """
        return User.from_token(user)

    @router.get("/status", response_model=AuthStatus)
    async def get_status(user: TokenPayload | None = Depends(get_current_user_optional)):
        """
        Check authentication status.

        Returns whether the user is authenticated and user info if so.
        Useful for frontend to check auth state without triggering 401.
        """
        if user:
            return AuthStatus(authenticated=True, user=User.from_token(user))
        return AuthStatus(authenticated=False, user=None)

    return router


# Default router instance
auth_router = create_auth_router()