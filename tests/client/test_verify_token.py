"""Tests for KeycloakClient.verify_token()."""

import time

import pytest
from jose import JWTError, jwt

from fastapi_keycloak_auth.client import KeycloakClient
from fastapi_keycloak_auth.models import TokenPayload


class TestVerifyValidToken:

    @pytest.mark.asyncio
    async def test_valid_token_returns_token_payload(self, keycloak_client, make_token):
        # Arrange
        token = make_token()

        # Act
        result = await keycloak_client.verify_token(token)

        # Assert
        assert isinstance(result, TokenPayload)

    @pytest.mark.asyncio
    async def test_token_payload_contains_correct_sub(self, keycloak_client, make_token):
        # Arrange
        token = make_token(sub="user-abc-123")

        # Act
        result = await keycloak_client.verify_token(token)

        # Assert
        assert result.sub == "user-abc-123"

    @pytest.mark.asyncio
    async def test_token_payload_contains_correct_email(self, keycloak_client, make_token):
        # Arrange
        token = make_token(email="john@example.com")

        # Act
        result = await keycloak_client.verify_token(token)

        # Assert
        assert result.email == "john@example.com"


class TestVerifyInvalidToken:

    @pytest.mark.asyncio
    async def test_expired_token_raises_jwt_error(self, keycloak_client, make_token):
        # Arrange
        token = make_token(expires_in=-10)

        # Act & Assert
        with pytest.raises(JWTError):
            await keycloak_client.verify_token(token)

    @pytest.mark.asyncio
    async def test_tampered_token_raises_jwt_error(self, keycloak_client):
        # Arrange
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.tampered.signature"

        # Act & Assert
        with pytest.raises(JWTError):
            await keycloak_client.verify_token(token)

    @pytest.mark.asyncio
    async def test_wrong_issuer_raises_jwt_error(self, keycloak_client, rsa_keypair):
        # Arrange
        now = int(time.time())
        token = jwt.encode(
            {
                "sub": "user",
                "iss": "https://wrong-issuer.com/realms/fake",
                "aud": "test-client",
                "iat": now,
                "exp": now + 300,
            },
            rsa_keypair["private_pem"],
            algorithm="RS256",
            headers={"kid": "test-key-id"},
        )

        # Act & Assert
        with pytest.raises(JWTError):
            await keycloak_client.verify_token(token)


class TestAudienceValidation:

    @pytest.mark.asyncio
    async def test_valid_audience_passes(self, keycloak_client, make_token):
        # Arrange
        token = make_token(audience="test-client")

        # Act
        result = await keycloak_client.verify_token(token)

        # Assert
        assert result.sub == "test-user-id"

    @pytest.mark.asyncio
    async def test_invalid_audience_raises_jwt_error(self, keycloak_client, make_token):
        # Arrange
        token = make_token(audience="wrong-audience")

        # Act & Assert
        with pytest.raises(JWTError, match="Invalid audience"):
            await keycloak_client.verify_token(token)

    @pytest.mark.asyncio
    async def test_token_without_audience_passes(self, keycloak_client, rsa_keypair, keycloak_settings):
        # Arrange — token with empty aud list (Keycloak sometimes omits aud)
        now = int(time.time())
        token = jwt.encode(
            {
                "sub": "user",
                "iss": keycloak_settings.issuer,
                "iat": now,
                "exp": now + 300,
            },
            rsa_keypair["private_pem"],
            algorithm="RS256",
            headers={"kid": "test-key-id"},
        )

        # Act
        result = await keycloak_client.verify_token(token)

        # Assert
        assert result.sub == "user"
