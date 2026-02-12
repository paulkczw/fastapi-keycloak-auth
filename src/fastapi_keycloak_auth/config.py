"""
Configuration for Keycloak authentication.
"""
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakSettings(BaseSettings):
    """
    Keycloak authentication settings.

    All settings can be configured via environment variables with the
    KEYCLOAK_ prefix, e.g. KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="KEYCLOAK_",
        env_file=".env",
        extra="ignore",
    )

    # Required Keycloak settings
    server_url: str = Field(description="Keycloak server URL (e.g. https://auth.example.com)")
    realm: str = Field(description="Keycloak realm name")
    client_id: str = Field(description="OAuth2 client ID")
    client_secret: str = Field(description="OAuth2 client secret")
    audience: str = Field(description="For which audience the access token should be issued")

    # SSL settings
    ssl_verify: bool = Field(default=True, description="Verify SSL certificates")
    ca_cert: str | None = Field(default=None, description="Path to CA certificate file")

    # Cookie settings
    cookie_name: str = Field(default="access_token", description="Name of the access token cookie")
    refresh_cookie_name: str = Field(default="refresh_token", description="Name of the refresh token cookie")
    cookie_secure: bool = Field(default=False, description="Set Secure flag on cookies (requires HTTPS)")
    cookie_httponly: bool = Field(default=True, description="Set HttpOnly flag on cookies")
    cookie_samesite: Literal["lax", "strict", "none"] | None = Field(default="lax", description="SameSite cookie attribute (lax, strict, none)")

    # URL settings
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend URL for redirects (Svelte dev server)")
    backend_url: str = Field(default="http://localhost:8000", description="Backend URL for OAuth callbacks")
    auth_path: str = Field(default="/auth", description="Base path for auth endpoints (e.g. /auth, /auth/keycloak)")
    login_redirect_path: str = Field(default="/", description="Frontend path to redirect after login")
    logout_redirect_path: str = Field(default="/", description="Frontend path to redirect after logout")

    # Scopes
    scopes: str = Field(default="openid email profile", description="OAuth2 scopes to request")

    @property
    def ssl_context(self) -> bool | str:
        """Return SSL verification setting for httpx."""
        if not self.ssl_verify:
            return False
        if self.ca_cert:
            return self.ca_cert
        return True

    @property
    def issuer(self) -> str:
        """Return the token issuer URL."""
        return f"{self.server_url}/realms/{self.realm}"

    @property
    def configuration_url(self):
        """Return the Keycloak OpenID configuration URL."""
        return f"{self.issuer}/.well-known/openid-configuration"

    @property
    def callback_url(self) -> str:
        """Return the OAuth2 callback URL."""
        return f"{self.backend_url}{self.auth_path}/callback"

    @property
    def logout_callback_url(self) -> str:
        """Return the logout callback URL (backend handles redirect to frontend)."""
        return f"{self.backend_url}{self.auth_path}/logout-callback"

    @property
    def post_login_redirect(self) -> str:
        """Return the full URL to redirect after login."""
        return f"{self.frontend_url}{self.login_redirect_path}"

    @property
    def post_logout_redirect(self) -> str:
        """Return the full URL to redirect after logout."""
        return f"{self.frontend_url}{self.logout_redirect_path}"