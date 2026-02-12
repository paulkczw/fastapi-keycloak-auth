"""Tests for /login endpoint."""

from urllib.parse import urlparse, parse_qs


class TestLoginRedirect:

    def test_redirects_to_keycloak_auth_endpoint(self, client, openid_configuration):
        # Act
        response = client.get("/auth/login")

        # Assert
        assert response.status_code == 307
        location = response.headers["location"]
        assert location.startswith(openid_configuration.authorization_endpoint)

    def test_includes_client_id_in_params(self, client):
        # Act
        response = client.get("/auth/login")

        # Assert
        location = response.headers["location"]
        params = parse_qs(urlparse(location).query)
        assert params["client_id"] == ["test-client"]

    def test_includes_redirect_uri_in_params(self, client):
        # Act
        response = client.get("/auth/login")

        # Assert
        location = response.headers["location"]
        params = parse_qs(urlparse(location).query)
        assert "redirect_uri" in params
        assert "/auth/callback" in params["redirect_uri"][0]

    def test_passes_custom_redirect_as_state(self, client):
        # Act
        response = client.get("/auth/login?redirect=https://app.test/dashboard")

        # Assert
        location = response.headers["location"]
        params = parse_qs(urlparse(location).query)
        assert params["state"] == ["https://app.test/dashboard"]
