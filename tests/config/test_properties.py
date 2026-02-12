"""Tests for KeycloakSettings computed properties."""

from fastapi_keycloak_auth.config import KeycloakSettings


class TestIssuer:

    def test_issuer_combines_server_url_and_realm(self, keycloak_settings):
        # Act
        issuer = keycloak_settings.issuer

        # Assert
        assert issuer == f"{keycloak_settings.server_url}/realms/{keycloak_settings.realm}"


class TestConfigurationUrl:

    def test_configuration_url_appends_well_known(self, keycloak_settings):
        # Act
        url = keycloak_settings.configuration_url

        # Assert
        assert url == f"{keycloak_settings.issuer}/.well-known/openid-configuration"


class TestCallbackUrl:

    def test_callback_url_combines_backend_and_auth_path(self, keycloak_settings):
        # Act
        url = keycloak_settings.callback_url

        # Assert
        assert url == "http://localhost:8000/auth/callback"


class TestLogoutCallbackUrl:

    def test_logout_callback_url(self, keycloak_settings):
        # Act
        url = keycloak_settings.logout_callback_url

        # Assert
        assert url == "http://localhost:8000/auth/logout-callback"


class TestPostLoginRedirect:

    def test_post_login_redirect_combines_frontend_and_path(self, keycloak_settings):
        # Act
        url = keycloak_settings.post_login_redirect

        # Assert
        assert url == "http://localhost:5173/"


class TestPostLogoutRedirect:

    def test_post_logout_redirect_combines_frontend_and_path(self, keycloak_settings):
        # Act
        url = keycloak_settings.post_logout_redirect

        # Assert
        assert url == "http://localhost:5173/"


class TestSslContext:

    def test_ssl_context_returns_true_by_default(self, keycloak_settings):
        # Act
        ctx = keycloak_settings.ssl_context

        # Assert
        assert ctx is True

    def test_ssl_context_returns_false_when_verify_disabled(self, monkeypatch, keycloak_settings):
        # Arrange
        monkeypatch.setattr(keycloak_settings, "ssl_verify", False)

        # Act
        ctx = keycloak_settings.ssl_context

        # Assert
        assert ctx is False

    def test_ssl_context_returns_ca_cert_path(self, monkeypatch, keycloak_settings):
        # Arrange
        monkeypatch.setattr(keycloak_settings, "ca_cert", "/path/to/ca.pem")

        # Act
        ctx = keycloak_settings.ssl_context

        # Assert
        assert ctx == "/path/to/ca.pem"
