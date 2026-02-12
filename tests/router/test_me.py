"""Tests for /me endpoint."""


class TestMe:

    def test_returns_user_json_when_authenticated(self, client, keycloak_settings, make_token):
        # Arrange
        token = make_token(sub="user-42", email="me@example.com", preferred_username="me")
        client.cookies.set(keycloak_settings.cookie_name, token)

        # Act
        response = client.get("/auth/me")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user-42"
        assert data["email"] == "me@example.com"
        assert data["username"] == "me"

    def test_returns_401_when_not_authenticated(self, client):
        # Act
        response = client.get("/auth/me")

        # Assert
        assert response.status_code == 401
