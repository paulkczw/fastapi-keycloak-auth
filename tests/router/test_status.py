"""Tests for /status endpoint."""


class TestStatus:

    def test_returns_200_always(self, client):
        # Act
        response = client.get("/auth/status")

        # Assert
        assert response.status_code == 200

    def test_authenticated_true_with_valid_token(self, client, keycloak_settings, make_token):
        # Arrange
        token = make_token()
        client.cookies.set(keycloak_settings.cookie_name, token)

        # Act
        response = client.get("/auth/status")

        # Assert
        assert response.json()["authenticated"] is True

    def test_authenticated_false_without_token(self, client):
        # Act
        response = client.get("/auth/status")

        # Assert
        assert response.json()["authenticated"] is False

    def test_includes_user_when_authenticated(self, client, keycloak_settings, make_token):
        # Arrange
        token = make_token(sub="user-99", email="user@test.com")
        client.cookies.set(keycloak_settings.cookie_name, token)

        # Act
        response = client.get("/auth/status")

        # Assert
        data = response.json()
        assert data["user"] is not None
        assert data["user"]["id"] == "user-99"
        assert data["user"]["email"] == "user@test.com"
