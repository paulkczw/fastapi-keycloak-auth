"""Tests for User model."""

from fastapi_keycloak_auth.models import User, TokenPayload


class TestUserFromToken:

    def test_maps_all_fields_from_token(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.id == sample_token_payload.sub
        assert user.email == sample_token_payload.email
        assert user.email_verified == sample_token_payload.email_verified
        assert user.username == sample_token_payload.preferred_username
        assert user.name == sample_token_payload.name
        assert user.first_name == sample_token_payload.given_name
        assert user.last_name == sample_token_payload.family_name
        assert user.roles == sample_token_payload.roles

    def test_maps_sub_to_id(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.id == "test-user-id"

    def test_maps_preferred_username_to_username(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.username == "testuser"

    def test_maps_given_name_to_first_name(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.first_name == "Test"

    def test_maps_family_name_to_last_name(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.last_name == "User"

    def test_maps_realm_roles(self, sample_token_payload):
        # Act
        user = User.from_token(sample_token_payload)

        # Assert
        assert user.roles == ["user", "admin"]

    def test_handles_token_with_no_optional_fields(self):
        # Arrange
        token = TokenPayload(sub="minimal-user")

        # Act
        user = User.from_token(token)

        # Assert
        assert user.id == "minimal-user"
        assert user.email is None
        assert user.username is None
        assert user.name is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.roles == []
