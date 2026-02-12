"""Tests for response models (TokenResponse, AuthStatus, OpenIdConfiguration)."""

import pytest

from fastapi_keycloak_auth.models import TokenResponse, AuthStatus, OpenIdConfiguration, User


class TestTokenResponse:

    def test_create_with_all_fields(self):
        pytest.skip("TODO")

    def test_default_token_type_is_bearer(self):
        pytest.skip("TODO")

    def test_refresh_token_is_optional(self):
        pytest.skip("TODO")


class TestAuthStatus:

    def test_authenticated_with_user(self, sample_token_payload):
        pytest.skip("TODO")

    def test_not_authenticated_without_user(self):
        pytest.skip("TODO")


class TestOpenIdConfiguration:

    def test_create_with_all_endpoints(self, openid_configuration):
        pytest.skip("TODO")

    def test_requires_all_fields(self):
        pytest.skip("TODO")
