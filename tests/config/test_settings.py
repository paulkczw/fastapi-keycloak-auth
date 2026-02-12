"""Tests for KeycloakSettings."""

import pytest

from fastapi_keycloak_auth.config import KeycloakSettings


class TestSettingsFromEnv:

    def test_loads_required_fields_from_env(self, keycloak_settings):
        pytest.skip("TODO")

    def test_raises_on_missing_required_fields(self, monkeypatch):
        pytest.skip("TODO")

    def test_default_values_applied(self, keycloak_settings):
        pytest.skip("TODO")

    def test_custom_cookie_settings(self, monkeypatch):
        pytest.skip("TODO")

    def test_custom_url_settings(self, monkeypatch):
        pytest.skip("TODO")
