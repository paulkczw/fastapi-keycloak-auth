"""Shared fixtures for all tests."""

import os
import time

# Set env vars BEFORE any fastapi_keycloak_auth imports (auth_router triggers get_settings() at import)
TEST_SERVER_URL = "https://keycloak.example.com"
TEST_REALM = "test-realm"
TEST_CLIENT_ID = "test-client"
TEST_CLIENT_SECRET = "test-secret"
TEST_AUDIENCE = "test-client"

os.environ.setdefault("KEYCLOAK_SERVER_URL", TEST_SERVER_URL)
os.environ.setdefault("KEYCLOAK_REALM", TEST_REALM)
os.environ.setdefault("KEYCLOAK_CLIENT_ID", TEST_CLIENT_ID)
os.environ.setdefault("KEYCLOAK_CLIENT_SECRET", TEST_CLIENT_SECRET)
os.environ.setdefault("KEYCLOAK_AUDIENCE", TEST_AUDIENCE)

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import jwt

from fastapi_keycloak_auth.config import KeycloakSettings
from fastapi_keycloak_auth.models import TokenPayload, OpenIdConfiguration
from fastapi_keycloak_auth.client import KeycloakClient
from fastapi_keycloak_auth.dependencies import clear_settings_cache
from fastapi_keycloak_auth.events import auth_events


@pytest.fixture
def keycloak_settings(monkeypatch) -> KeycloakSettings:
    """KeycloakSettings with test values (via env vars)."""
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", TEST_SERVER_URL)
    monkeypatch.setenv("KEYCLOAK_REALM", TEST_REALM)
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", TEST_CLIENT_ID)
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", TEST_CLIENT_SECRET)
    monkeypatch.setenv("KEYCLOAK_AUDIENCE", TEST_AUDIENCE)
    return KeycloakSettings()  # type: ignore[call-arg]


# =============================================================================
# RSA Keys & JWT
# =============================================================================

@pytest.fixture(scope="session")
def rsa_keypair():
    """Generate RSA key pair for JWT signing (session-scoped for speed)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_numbers = public_key.public_numbers()

    def _int_to_base64url(value: int) -> str:
        import base64
        byte_length = (value.bit_length() + 7) // 8
        value_bytes = value.to_bytes(byte_length, byteorder="big")
        return base64.urlsafe_b64encode(value_bytes).rstrip(b"=").decode()

    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "test-key-id",
        "n": _int_to_base64url(public_numbers.n),
        "e": _int_to_base64url(public_numbers.e),
    }

    return {"private_pem": private_pem, "jwk": jwk}


@pytest.fixture
def jwks_response(rsa_keypair) -> dict:
    """JWKS JSON matching the RSA key pair."""
    return {"keys": [rsa_keypair["jwk"]]}


@pytest.fixture
def make_token(rsa_keypair, keycloak_settings):
    """Factory that creates signed JWT tokens."""

    def _make(
        sub: str = "test-user-id",
        email: str = "test@example.com",
        preferred_username: str = "testuser",
        realm_roles: list[str] | None = None,
        resource_access: dict | None = None,
        audience: str | None = None,
        expires_in: int = 300,
        **extra_claims,
    ) -> str:
        now = int(time.time())
        payload = {
            "sub": sub,
            "email": email,
            "email_verified": True,
            "preferred_username": preferred_username,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "iss": keycloak_settings.issuer,
            "aud": audience or keycloak_settings.audience,
            "iat": now,
            "exp": now + expires_in,
            **extra_claims,
        }
        if realm_roles is not None:
            payload["realm_access"] = {"roles": realm_roles}
        if resource_access is not None:
            payload["resource_access"] = resource_access

        return jwt.encode(
            payload,
            rsa_keypair["private_pem"],
            algorithm="RS256",
            headers={"kid": "test-key-id"},
        )

    return _make


# =============================================================================
# Models
# =============================================================================

@pytest.fixture
def sample_token_payload() -> TokenPayload:
    """Example TokenPayload for unit tests."""
    return TokenPayload(
        sub="test-user-id",
        email="test@example.com",
        email_verified=True,
        preferred_username="testuser",
        name="Test User",
        given_name="Test",
        family_name="User",
        realm_access={"roles": ["user", "admin"]},
        resource_access={"my-app": {"roles": ["editor"]}},
    )


@pytest.fixture
def openid_configuration() -> OpenIdConfiguration:
    """Mock OpenID configuration."""
    base = f"{TEST_SERVER_URL}/realms/{TEST_REALM}"
    return OpenIdConfiguration(
        issuer=base,
        authorization_endpoint=f"{base}/protocol/openid-connect/auth",
        token_endpoint=f"{base}/protocol/openid-connect/token",
        userinfo_endpoint=f"{base}/protocol/openid-connect/userinfo",
        jwks_uri=f"{base}/protocol/openid-connect/certs",
        end_session_endpoint=f"{base}/protocol/openid-connect/logout",
    )


# =============================================================================
# Client
# =============================================================================

@pytest.fixture
def keycloak_client(keycloak_settings, jwks_response, openid_configuration) -> KeycloakClient:
    """KeycloakClient with pre-loaded JWKS and OpenID config (no HTTP calls)."""
    client = KeycloakClient(keycloak_settings)
    client._jwks = jwks_response
    client._openid_configuration = openid_configuration
    return client


# =============================================================================
# Autouse: reset singletons between tests
# =============================================================================

@pytest.fixture(autouse=True)
def clear_caches():
    """Reset singletons and event handlers between tests."""
    clear_settings_cache()
    auth_events.clear_handlers()
    yield
    clear_settings_cache()
    auth_events.clear_handlers()
