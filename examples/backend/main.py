"""
Example FastAPI backend with Keycloak authentication.

Run with:
    cd backend
    uvicorn main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from fastapi_keycloak_auth import (
    auth_router,
    require_role,
    require_any_role,
    get_current_user,
    get_current_user_optional,
    TokenPayload,
    auth_events,
    AuthEvent,
    LoginEventData,
    LogoutEventData,
)

app = FastAPI(
    title="Example API",
    description="FastAPI + Keycloak + Svelte Example",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173", # Svelte dev server
    ],
    allow_credentials=True,  # important for cookies!
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register auth router (/auth/login, /auth/callback, /auth/logout, /auth/me, /auth/status)
app.include_router(auth_router)


# ============================================================================
# Public Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Public endpoint"""
    return {
        "message": "Welcome to the API!",
        "docs": "/docs",
        "login": "/auth/login",
    }


@app.get("/api/public")
async def public_data():
    """Public endpoint"""
    return {
        "data": ["item1", "item2", "item3"],
        "public": True,
    }


@app.get("/api/greeting")
async def greeting(user: TokenPayload | None = Depends(get_current_user_optional)):
    """Public endpoint, with optional authentication"""
    if user:
        return {"message": f"Hallo {user.preferred_username}!"}
    return {"message": "Hello guest!"}


# ============================================================================
# Protected Endpoints
# ============================================================================

@app.get("/api/protected")
async def protected_data(user: TokenPayload = Depends(get_current_user)):
    """Protected endpoint, authentication required"""
    return {
        "message": "You dont have permission to view this page!",
        "user": {
            "id": user.sub,
            "email": user.email,
            "username": user.preferred_username,
            "name": user.name,
            "roles": user.roles,
        },
    }


@app.get("/api/profile")
async def get_profile(user: TokenPayload = Depends(get_current_user)):
    """Get user profile"""
    return {
        "id": user.sub,
        "email": user.email,
        "email_verified": user.email_verified,
        "username": user.preferred_username,
        "name": user.name,
        "first_name": user.given_name,
        "last_name": user.family_name,
        "roles": user.roles,
    }


# ============================================================================
# Role-based Endpoints
# ============================================================================

@app.get("/api/admin")
async def admin_only(user: TokenPayload = Depends(require_role("admin"))):
    """Only for user with role admin"""
    return {
        "message": f"Welcome admin, {user.preferred_username}!",
        "admin_data": {
            "users_count": 42,
            "active_sessions": 17,
        },
    }


@app.get("/api/moderator")
async def moderator_area(user: TokenPayload = Depends(require_any_role("admin", "moderator"))):
    """Only for users with role moderator or admin"""
    return {
        "message": f"Welcome moderator, {user.preferred_username}",
        "your_roles": user.roles,
    }


# ============================================================================
# Example: Custom business logic
# ============================================================================

# Fake database
TODOS = {
    "user1": [
        {"id": 1, "title": "Buy", "done": False},
        {"id": 2, "title": "Play tennis", "done": True},
    ]
}


@app.get("/api/todos")
async def get_todos(user: TokenPayload = Depends(get_current_user)):
    """Get todos of user"""
    user_todos = TODOS.get(user.sub, [])
    return {"todos": user_todos}


@app.post("/api/todos")
async def create_todo(
        title: str,
        user: TokenPayload = Depends(get_current_user),
):
    """Create new todo"""
    if user.sub not in TODOS:
        TODOS[user.sub] = []

    new_todo = {
        "id": len(TODOS[user.sub]) + 1,
        "title": title,
        "done": False,
    }
    TODOS[user.sub].append(new_todo)
    return new_todo


# ============================================================================
# Example: Events
# ============================================================================

# Decorator-Syntax
@auth_events.on(AuthEvent.LOGIN)
async def on_login(data: LoginEventData):
    logging.info(f"User {data.user.email} logged in")

@auth_events.on(AuthEvent.LOGOUT)
async def on_logout(data: LogoutEventData):
    if data.user:
        logging.info(f"User {data.user.email} logged out")

@auth_events.on(AuthEvent.REFRESH)
async def on_refresh(data):
    logging.info(f"Token refreshed")

@auth_events.on(AuthEvent.TOKEN_VERIFIED)
async def on_request(data):
    logging.info(f"Request von {data.user.email}")

@auth_events.on(AuthEvent.TOKEN_INVALID)
async def on_invalid(data):
    logging.info(f"Invalid token: {data.error}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)