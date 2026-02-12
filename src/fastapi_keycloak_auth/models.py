"""
Pydantic models for authentication.
"""

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Validated JWT token payload from Keycloak."""

    sub: str = Field(description="Subject (user ID)")
    email: str | None = Field(default=None, description="User email")
    email_verified: bool = Field(default=False, description="Whether email is verified")
    preferred_username: str | None = Field(default=None, description="Username")
    name: str | None = Field(default=None, description="Full name")
    given_name: str | None = Field(default=None, description="First name")
    family_name: str | None = Field(default=None, description="Last name")
    realm_access: dict | None = Field(default=None, description="Realm-level access")
    resource_access: dict | None = Field(default=None, description="Resource-level access")

    @property
    def roles(self) -> list[str]:
        """Extract realm roles from token."""
        if self.realm_access:
            return self.realm_access.get("roles", [])
        return []

    def has_role(self, role: str) -> bool:
        """Check if user has a specific realm role."""
        return role in self.roles

    def get_client_roles(self, client_id: str) -> list[str]:
        """Get roles for a specific client."""
        if self.resource_access and client_id in self.resource_access:
            return self.resource_access[client_id].get("roles", [])
        return []


class User(BaseModel):
    """User model for API responses."""

    id: str = Field(description="User ID (sub)")
    email: str | None = Field(default=None)
    email_verified: bool = Field(default=False)
    username: str | None = Field(default=None)
    name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    roles: list[str] = Field(default_factory=list)

    @classmethod
    def from_token(cls, token: TokenPayload) -> "User":
        """Create User from token payload."""
        return cls(
            id=token.sub,
            email=token.email,
            email_verified=token.email_verified,
            username=token.preferred_username,
            name=token.name,
            first_name=token.given_name,
            last_name=token.family_name,
            roles=token.roles,
        )


class TokenResponse(BaseModel):
    """Token response for API mode (non-cookie)."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in: int


class AuthStatus(BaseModel):
    """Authentication status response."""

    authenticated: bool
    user: User | None = None


class OpenIdConfiguration(BaseModel):
    """OpenID Connect configuration from Keycloak."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    end_session_endpoint: str