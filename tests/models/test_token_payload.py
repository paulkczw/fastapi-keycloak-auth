"""Tests for TokenPayload model."""

from fastapi_keycloak_auth.models import TokenPayload


class TestTokenPayloadCreation:

    def test_create_with_required_fields_only(self):
        # Arrange & Act
        payload = TokenPayload(sub="user-123")

        # Assert
        assert payload.sub == "user-123"
        assert payload.email is None
        assert payload.email_verified is False
        assert payload.preferred_username is None
        assert payload.name is None
        assert payload.given_name is None
        assert payload.family_name is None
        assert payload.realm_access is None
        assert payload.resource_access is None

    def test_create_with_all_fields(self):
        # Arrange & Act
        payload = TokenPayload(
            sub="user-123",
            email="user@example.com",
            email_verified=True,
            preferred_username="johndoe",
            name="John Doe",
            given_name="John",
            family_name="Doe",
            realm_access={"roles": ["admin"]},
            resource_access={"app": {"roles": ["editor"]}},
        )

        # Assert
        assert payload.sub == "user-123"
        assert payload.email == "user@example.com"
        assert payload.email_verified is True
        assert payload.preferred_username == "johndoe"
        assert payload.name == "John Doe"
        assert payload.given_name == "John"
        assert payload.family_name == "Doe"
        assert payload.realm_access == {"roles": ["admin"]}
        assert payload.resource_access == {"app": {"roles": ["editor"]}}

    def test_defaults_are_applied(self):
        # Arrange & Act
        payload = TokenPayload(sub="user-123")

        # Assert
        assert payload.email_verified is False
        assert payload.realm_access is None
        assert payload.resource_access is None


class TestTokenPayloadRoles:

    def test_roles_returns_realm_roles(self, sample_token_payload):
        # Act
        roles = sample_token_payload.roles

        # Assert
        assert roles == ["user", "admin"]

    def test_roles_returns_empty_list_when_no_realm_access(self):
        # Arrange
        payload = TokenPayload(sub="user-123", realm_access=None)

        # Act
        roles = payload.roles

        # Assert
        assert roles == []

    def test_roles_returns_empty_list_when_realm_access_has_no_roles(self):
        # Arrange
        payload = TokenPayload(sub="user-123", realm_access={})

        # Act
        roles = payload.roles

        # Assert
        assert roles == []


class TestTokenPayloadHasRole:

    def test_has_role_returns_true_for_existing_role(self, sample_token_payload):
        # Act & Assert
        assert sample_token_payload.has_role("admin") is True
        assert sample_token_payload.has_role("user") is True

    def test_has_role_returns_false_for_missing_role(self, sample_token_payload):
        # Act & Assert
        assert sample_token_payload.has_role("superadmin") is False

    def test_has_role_returns_false_when_no_realm_access(self):
        # Arrange
        payload = TokenPayload(sub="user-123")

        # Act & Assert
        assert payload.has_role("admin") is False


class TestTokenPayloadGetClientRoles:

    def test_get_client_roles_returns_roles_for_known_client(self, sample_token_payload):
        # Act
        roles = sample_token_payload.get_client_roles("my-app")

        # Assert
        assert roles == ["editor"]

    def test_get_client_roles_returns_empty_for_unknown_client(self, sample_token_payload):
        # Act
        roles = sample_token_payload.get_client_roles("unknown-app")

        # Assert
        assert roles == []

    def test_get_client_roles_returns_empty_when_no_resource_access(self):
        # Arrange
        payload = TokenPayload(sub="user-123")

        # Act
        roles = payload.get_client_roles("my-app")

        # Assert
        assert roles == []
