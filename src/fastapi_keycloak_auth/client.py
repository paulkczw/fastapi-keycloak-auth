"""
Keycloak HTTP client for token operations.
"""

import httpx
from jose import JWTError, jwt

from .config import KeycloakSettings
from .models import TokenPayload, TokenResponse


class KeycloakClient:
    """HTTP client for Keycloak operations."""

    def __init__(self, settings: KeycloakSettings):
        self.settings = settings
        self._jwks: dict | None = None

    async def get_jwks(self) -> dict:
        """Fetch and cache JWKS from Keycloak."""
        if self._jwks is None:
            async with httpx.AsyncClient(verify=self.settings.ssl_context) as client:
                response = await client.get(self.settings.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()
        return self._jwks

    def clear_jwks_cache(self) -> None:
        """Clear JWKS cache (useful for key rotation)."""
        self._jwks = None

    async def exchange_code(self, code: str) -> TokenResponse:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient(verify=self.settings.ssl_context) as client:
            response = await client.post(
                self.settings.token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "code": code,
                    "redirect_uri": self.settings.callback_url,
                },
            )
            response.raise_for_status()
            data = response.json()
            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token"),
                token_type=data.get("token_type", "Bearer"),
                expires_in=data.get("expires_in", 300),
            )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        async with httpx.AsyncClient(verify=self.settings.ssl_context) as client:
            response = await client.post(
                self.settings.token_url,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()
            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token"),
                token_type=data.get("token_type", "Bearer"),
                expires_in=data.get("expires_in", 300),
            )

    async def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode JWT token."""
        jwks = await self.get_jwks()

        # Decode without audience verification (Keycloak can be tricky)
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=self.settings.issuer,
            options={"verify_aud": False},
        )

        # Manual audience check
        aud = payload.get("aud", [])
        if isinstance(aud, str):
            aud = [aud]

        valid_audiences = {self.settings.client_id, "account"}
        if aud and not any(a in valid_audiences for a in aud):
            raise JWTError(f"Invalid audience: {aud}")

        return TokenPayload(**payload)

    async def get_userinfo(self, access_token: str) -> dict:
        """Fetch user info from Keycloak userinfo endpoint."""
        async with httpx.AsyncClient(verify=self.settings.ssl_context) as client:
            response = await client.get(
                self.settings.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()