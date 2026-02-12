"""Tests for AuthEventEmitter core functionality."""

import pytest

from fastapi_keycloak_auth.events import AuthEventEmitter, AuthEvent


class TestRegisterHandler:

    @pytest.mark.asyncio
    async def test_register_via_decorator(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_register_via_add_handler(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_duplicate_handler_not_added(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_remove_handler(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_clear_handlers_for_event(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_clear_all_handlers(self):
        pytest.skip("TODO")


class TestEmit:

    @pytest.mark.asyncio
    async def test_emit_calls_handler_with_data(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_emit_calls_handlers_in_registration_order(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_emit_with_no_handlers_does_not_raise(self):
        pytest.skip("TODO")


class TestHasHandlers:

    def test_has_handlers_returns_false_initially(self):
        pytest.skip("TODO")

    @pytest.mark.asyncio
    async def test_has_handlers_returns_true_after_registration(self):
        pytest.skip("TODO")
