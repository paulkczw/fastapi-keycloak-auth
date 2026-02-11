"""
Event system for authentication callbacks.

Usage:
    from fastapi_keycloak_auth import auth_events, AuthEvent

    @auth_events.on(AuthEvent.LOGIN)
    async def on_login(user, tokens):
        print(f"User {user.email} logged in")
        # Create user in database, send welcome email, etc.

    @auth_events.on(AuthEvent.LOGOUT)
    async def on_logout(user):
        print(f"User {user.email} logged out")
        # Cleanup, audit log, etc.
"""

from enum import Enum
from typing import Any, Callable, Coroutine
from dataclasses import dataclass

from .models import TokenPayload, TokenResponse


class AuthEvent(str, Enum):
    """Authentication events that can be subscribed to."""

    # Fired after successful login (token exchange)
    LOGIN = "login"

    # Fired before logout redirect
    LOGOUT = "logout"

    # Fired after successful token refresh
    REFRESH = "refresh"

    # Fired after token verification (on each authenticated request)
    TOKEN_VERIFIED = "token_verified"

    # Fired when token verification fails
    TOKEN_INVALID = "token_invalid"

    # Fired on first login (user not seen before) - requires custom check
    FIRST_LOGIN = "first_login"


@dataclass
class LoginEventData:
    """Data passed to LOGIN event handlers."""
    user: TokenPayload
    tokens: TokenResponse


@dataclass
class LogoutEventData:
    """Data passed to LOGOUT event handlers."""
    # User may be None if token was invalid/expired
    user: TokenPayload | None


@dataclass
class RefreshEventData:
    """Data passed to REFRESH event handlers."""
    tokens: TokenResponse


@dataclass
class TokenVerifiedEventData:
    """Data passed to TOKEN_VERIFIED event handlers."""
    user: TokenPayload


@dataclass
class TokenInvalidEventData:
    """Data passed to TOKEN_INVALID event handlers."""
    error: str
    token: str | None = None


# Type alias for event handlers
EventHandler = Callable[..., Coroutine[Any, Any, None]]


class AuthEventEmitter:
    """Event emitter for authentication events."""

    def __init__(self):
        self._handlers: dict[AuthEvent, list[EventHandler]] = {
            event: [] for event in AuthEvent
        }

    def on(self, event: AuthEvent):
        """
        Decorator to register an event handler.

        Usage:
            @auth_events.on(AuthEvent.LOGIN)
            async def handle_login(data: LoginEventData):
                print(f"User {data.user.email} logged in")
        """

        def decorator(func: EventHandler) -> EventHandler:
            self._handlers[event].append(func)
            return func

        return decorator

    def add_handler(self, event: AuthEvent, handler: EventHandler) -> None:
        """Register an event handler programmatically."""
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def remove_handler(self, event: AuthEvent, handler: EventHandler) -> None:
        """Remove an event handler."""
        if handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def clear_handlers(self, event: AuthEvent | None = None) -> None:
        """Clear all handlers for an event, or all events if None."""
        if event is None:
            for e in AuthEvent:
                self._handlers[e] = []
        else:
            self._handlers[event] = []

    async def emit(self, event: AuthEvent, data: Any = None) -> None:
        """
        Emit an event to all registered handlers.

        Handlers are called in order of registration.
        Exceptions in handlers are logged but don't stop other handlers.
        """
        for handler in self._handlers[event]:
            try:
                await handler(data)
            except Exception as e:
                # Log error but continue with other handlers
                import logging
                logging.error(f"Error in {event.value} handler {handler.__name__}: {e}")

    def has_handlers(self, event: AuthEvent) -> bool:
        """Check if an event has any handlers registered."""
        return len(self._handlers[event]) > 0


# Global event emitter instance
auth_events = AuthEventEmitter()