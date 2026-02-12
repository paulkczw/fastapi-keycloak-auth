"""Tests for KeycloakSettings."""

import pytest
from pydantic import ValidationError

from fastapi_keycloak_auth.config import KeycloakSettings


class TestSettingsFromEnv:

    def test_loads_required_fields_from_env(self, keycloak_settings):
        # Assert
        from tests.conftest import TEST_SERVER_URL, TEST_REALM, TEST_CLIENT_ID, TEST_CLIENT_SECRET, TEST_AUDIENCE
        assert keycloak_settings.server_url == TEST_SERVER_URL
        assert keycloak_settings.realm == TEST_REALM
        assert keycloak_settings.client_id == TEST_CLIENT_ID
        assert keycloak_settings.client_secret == TEST_CLIENT_SECRET
        assert keycloak_settings.audience == TEST_AUDIENCE

    def test_raises_on_missing_required_fields(self, monkeypatch):
        # Arrange
        monkeypatch.delenv("KEYCLOAK_SERVER_URL", raising=False)
        monkeypatch.delenv("KEYCLOAK_REALM", raising=False)
        monkeypatch.delenv("KEYCLOAK_CLIENT_ID", raising=False)
        monkeypatch.delenv("KEYCLOAK_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("KEYCLOAK_AUDIENCE", raising=False)

        # Act & Assert
        with pytest.raises(ValidationError):
            KeycloakSettings()  # type: ignore[call-arg]

    def test_default_values_applied(self, keycloak_settings):
        # Assert
        assert keycloak_settings.cookie_name == "access_token"
        assert keycloak_settings.refresh_cookie_name == "refresh_token"
        assert keycloak_settings.cookie_secure is False
        assert keycloak_settings.cookie_httponly is True
        assert keycloak_settings.cookie_samesite == "lax"
        assert keycloak_settings.ssl_verify is True
        assert keycloak_settings.scopes == "openid email profile"

    def test_custom_cookie_settings(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("KEYCLOAK_SERVER_URL", "https://kc.test")
        monkeypatch.setenv("KEYCLOAK_REALM", "r")
        monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "c")
        monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "s")
        monkeypatch.setenv("KEYCLOAK_AUDIENCE", "a")
        monkeypatch.setenv("KEYCLOAK_COOKIE_NAME", "my_token")
        monkeypatch.setenv("KEYCLOAK_COOKIE_SECURE", "true")
        monkeypatch.setenv("KEYCLOAK_COOKIE_SAMESITE", "strict")

        # Act
        settings = KeycloakSettings()  # type: ignore[call-arg]

        # Assert
        assert settings.cookie_name == "my_token"
        assert settings.cookie_secure is True
        assert settings.cookie_samesite == "strict"

    def test_custom_url_settings(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("KEYCLOAK_SERVER_URL", "https://kc.test")
        monkeypatch.setenv("KEYCLOAK_REALM", "r")
        monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "c")
        monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "s")
        monkeypatch.setenv("KEYCLOAK_AUDIENCE", "a")
        monkeypatch.setenv("KEYCLOAK_FRONTEND_URL", "https://app.test")
        monkeypatch.setenv("KEYCLOAK_BACKEND_URL", "https://api.test")
        monkeypatch.setenv("KEYCLOAK_AUTH_PATH", "/auth/kc")

        # Act
        settings = KeycloakSettings()  # type: ignore[call-arg]

        # Assert
        assert settings.frontend_url == "https://app.test"
        assert settings.backend_url == "https://api.test"
        assert settings.auth_path == "/auth/kc"
