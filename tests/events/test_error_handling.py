"""Tests for error handling in event emitter."""

import pytest

from fastapi_keycloak_auth.events import AuthEventEmitter, AuthEvent


class TestHandlerErrors:

    @pytest.mark.asyncio
    async def test_error_in_handler_does_not_stop_other_handlers(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_error_in_handler_is_logged(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_all_handlers_run_even_if_first_fails(self):
        pytest.skip("TODO")
