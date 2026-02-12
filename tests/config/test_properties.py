"""Tests for KeycloakSettings computed properties."""

import pytest

from fastapi_keycloak_auth.config import KeycloakSettings


class TestIssuer:

    def test_issuer_combines_server_url_and_realm(self, keycloak_settings):
        pytest.skip("TODO")


class TestConfigurationUrl:

    def test_configuration_url_appends_well_known(self, keycloak_settings):
        pytest.skip("TODO")


class TestCallbackUrl:

    def test_callback_url_combines_backend_and_auth_path(self, keycloak_settings):
        pytest.skip("TODO")


class TestLogoutCallbackUrl:

    def test_logout_callback_url(self, keycloak_settings):
        pytest.skip("TODO")


class TestPostLoginRedirect:

    def test_post_login_redirect_combines_frontend_and_path(self, keycloak_settings):
        pytest.skip("TODO")


class TestPostLogoutRedirect:

    def test_post_logout_redirect_combines_frontend_and_path(self, keycloak_settings):
        pytest.skip("TODO")


class TestSslContext:

    def test_ssl_context_returns_true_by_default(self, keycloak_settings):
        pytest.skip("TODO")

    def test_ssl_context_returns_false_when_verify_disabled(self, monkeypatch):
        pytest.skip("TODO")

    def test_ssl_context_returns_ca_cert_path(self, monkeypatch):
        pytest.skip("TODO")
