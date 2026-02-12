"""Tests for User model."""

import pytest

from fastapi_keycloak_auth.models import User, TokenPayload


class TestUserFromToken:

    def test_maps_all_fields_from_token(self, sample_token_payload):
        pytest.skip("TODO")

    def test_maps_sub_to_id(self, sample_token_payload):
        pytest.skip("TODO")

    def test_maps_preferred_username_to_username(self, sample_token_payload):
        pytest.skip("TODO")

    def test_maps_given_name_to_first_name(self, sample_token_payload):
        pytest.skip("TODO")

    def test_maps_family_name_to_last_name(self, sample_token_payload):
        pytest.skip("TODO")

    def test_maps_realm_roles(self, sample_token_payload):
        pytest.skip("TODO")

    def test_handles_token_with_no_optional_fields(self):
        pytest.skip("TODO")
