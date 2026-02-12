"""Tests for /logout endpoint."""

from urllib.parse import urlparse, parse_qs


class TestLogout:

    def test_redirects_to_keycloak_logout(self, client, openid_configuration):
        # Act
        response = client.get("/auth/logout")

        # Assert
        assert response.status_code == 307
        location = response.headers["location"]
        assert location.startswith(openid_configuration.end_session_endpoint)

    def test_deletes_access_token_cookie(self, client):
        # Arrange — set a cookie first
        client.cookies.set("access_token", "some-token")

        # Act
        response = client.get("/auth/logout")

        # Assert
        set_cookie_headers = response.headers.get_list("set-cookie")
        access_token_deleted = any(
            'access_token=""' in h or "access_token=;" in h or ('access_token' in h and 'Max-Age=0' in h)
            for h in set_cookie_headers
        )
        assert access_token_deleted

    def test_deletes_refresh_token_cookie(self, client):
        # Arrange
        client.cookies.set("refresh_token", "some-token")

        # Act
        response = client.get("/auth/logout")

        # Assert
        set_cookie_headers = response.headers.get_list("set-cookie")
        refresh_token_deleted = any(
            'refresh_token=""' in h or "refresh_token=;" in h or ('refresh_token' in h and 'Max-Age=0' in h)
            for h in set_cookie_headers
        )
        assert refresh_token_deleted

    def test_passes_custom_redirect(self, client):
        # Act
        response = client.get("/auth/logout?redirect=https://app.test/bye")

        # Assert
        location = response.headers["location"]
        params = parse_qs(urlparse(location).query)
        assert "redirect=https://app.test/bye" in params.get("post_logout_redirect_uri", [""])[0]


class TestLogoutCallback:

    def test_redirects_to_frontend(self, client):
        # Act
        response = client.get("/auth/logout-callback")

        # Assert
        assert response.status_code == 302
        assert response.headers["location"] == "http://localhost:5173/"

    def test_clears_cookies(self, client):
        # Arrange
        client.cookies.set("access_token", "tok")
        client.cookies.set("refresh_token", "ref")

        # Act
        response = client.get("/auth/logout-callback")

        # Assert
        set_cookie_headers = response.headers.get_list("set-cookie")
        assert any("access_token" in h for h in set_cookie_headers)
        assert any("refresh_token" in h for h in set_cookie_headers)
