"""Tests for TokenPayload model."""

import pytest

from fastapi_keycloak_auth.models import TokenPayload


class TestTokenPayloadCreation:

    def test_create_with_required_fields_only(self):
        pytest.skip("TODO")

    def test_create_with_all_fields(self):
        pytest.skip("TODO")

    def test_defaults_are_applied(self):
        pytest.skip("TODO")


class TestTokenPayloadRoles:

    def test_roles_returns_realm_roles(self, sample_token_payload):
        pytest.skip("TODO")

    def test_roles_returns_empty_list_when_no_realm_access(self):
        pytest.skip("TODO")

    def test_roles_returns_empty_list_when_realm_access_has_no_roles(self):
        pytest.skip("TODO")


class TestTokenPayloadHasRole:

    def test_has_role_returns_true_for_existing_role(self, sample_token_payload):
        pytest.skip("TODO")

    def test_has_role_returns_false_for_missing_role(self, sample_token_payload):
        pytest.skip("TODO")

    def test_has_role_returns_false_when_no_realm_access(self):
        pytest.skip("TODO")


class TestTokenPayloadGetClientRoles:

    def test_get_client_roles_returns_roles_for_known_client(self, sample_token_payload):
        pytest.skip("TODO")

    def test_get_client_roles_returns_empty_for_unknown_client(self, sample_token_payload):
        pytest.skip("TODO")

    def test_get_client_roles_returns_empty_when_no_resource_access(self):
        pytest.skip("TODO")
