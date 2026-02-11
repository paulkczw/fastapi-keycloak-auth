# fastapi-keycloak-auth

A small FastAPI integration for Keycloak authentication with two example apps (backend + Svelte frontend).

Prerequisites
- Python >= 3.12
- node and npm (for the Svelte example)

Quickstart (development)

1) Install the package in editable mode:

```powershell
peotry install
```

2) Start the backend example

```powershell
cd examples/backend
# starts the example API at http://127.0.0.1:8000
uvicorn main:app --reload --port 8000
```

3) Start the Svelte frontend example

```powershell
cd examples/svelte
npm install
npm run dev
# the Svelte dev server typically runs at http://127.0.0.1:5173
```

Environment variables

Keycloak settings are read from environment variables with the `KEYCLOAK_` prefix (a `.env` file is supported). At minimum set:

- `KEYCLOAK_SERVER_URL` (e.g. https://auth.example.com)
- `KEYCLOAK_REALM`
- `KEYCLOAK_CLIENT_ID`
- `KEYCLOAK_CLIENT_SECRET`

Additional options and defaults are defined in `src/fastapi_keycloak_auth/config.py` (frontend/backend URLs, cookie options, scopes, etc.).

Examples / Demo
- Backend: `examples/backend` — small FastAPI app with public and protected endpoints.
- Frontend: `examples/svelte` — Svelte example app that works with the backend.

Notes
- The examples are small and intended for demonstration and testing only. They are not production-ready.
- Make sure to set the Keycloak environment variables before starting the backend so the OAuth flow works.

Further reading
- See the source in `src/fastapi_keycloak_auth/` for router, dependencies and config.
- For local testing you can run Keycloak locally or use a hosted Keycloak and point the `KEYCLOAK_` variables to it.

License
- [MIT License](LICENSE)
