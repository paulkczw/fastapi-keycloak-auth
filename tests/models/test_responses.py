"""Tests for response models (TokenResponse, AuthStatus, OpenIdConfiguration)."""

import pytest
from pydantic import ValidationError

from fastapi_keycloak_auth.models import TokenResponse, AuthStatus, OpenIdConfiguration, User


class TestTokenResponse:

    def test_create_with_all_fields(self):
        # Arrange & Act
        response = TokenResponse(
            access_token="access-abc",
            refresh_token="refresh-xyz",
            token_type="Bearer",
            expires_in=300,
        )

        # Assert
        assert response.access_token == "access-abc"
        assert response.refresh_token == "refresh-xyz"
        assert response.token_type == "Bearer"
        assert response.expires_in == 300

    def test_default_token_type_is_bearer(self):
        # Arrange & Act
        response = TokenResponse(access_token="token", expires_in=300)

        # Assert
        assert response.token_type == "Bearer"

    def test_refresh_token_is_optional(self):
        # Arrange & Act
        response = TokenResponse(access_token="token", expires_in=300)

        # Assert
        assert response.refresh_token is None


class TestAuthStatus:

    def test_authenticated_with_user(self, sample_token_payload):
        # Arrange
        user = User.from_token(sample_token_payload)

        # Act
        status = AuthStatus(authenticated=True, user=user)

        # Assert
        assert status.authenticated is True
        assert status.user is not None
        assert status.user.id == "test-user-id"

    def test_not_authenticated_without_user(self):
        # Arrange & Act
        status = AuthStatus(authenticated=False)

        # Assert
        assert status.authenticated is False
        assert status.user is None


class TestOpenIdConfiguration:

    def test_create_with_all_endpoints(self, openid_configuration):
        # Assert
        assert "auth" in openid_configuration.authorization_endpoint
        assert "token" in openid_configuration.token_endpoint
        assert "userinfo" in openid_configuration.userinfo_endpoint
        assert "certs" in openid_configuration.jwks_uri
        assert "logout" in openid_configuration.end_session_endpoint

    def test_requires_all_fields(self):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            OpenIdConfiguration(issuer="https://example.com")  # type: ignore[call-arg]
