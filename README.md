# Enterprise AI Platform

Backend + agent tooling for an internal HR/insurance/search assistant.

## Authentication & sessions

`backend/` exposes a small FastAPI auth service used by the Streamlit UI
(`ui/app.py`) and, ultimately, the mobile client:

- `POST /api/auth/register` - create a user
- `POST /api/auth/login` - exchange credentials for an **access token**
  (short-lived, default 30 minutes, `ACCESS_TOKEN_EXPIRE_MINUTES`) and a
  **refresh token** (long-lived, default 7 days, `REFRESH_TOKEN_EXPIRE_DAYS`)
- `POST /api/auth/refresh` - exchange a valid refresh token for a new access
  token without re-entering credentials
- `POST /api/auth/logout` - revoke a refresh token's session
- `GET /api/auth/me` - fetch the current user (requires a valid access token)

### IMS-4: mobile users logged out after ~10 seconds

The mobile client previously had no way to renew its session once the
access token expired, and the only applied expiry was extremely short, so
users were bounced back to the login screen almost immediately. The fix:

1. Access tokens and refresh tokens are now distinct, with the refresh
   token's lifetime tracked server-side in `user_sessions` so it can be
   revoked or inspected independently of the JWT's own `exp` claim.
2. Clients (see `ui/app.py`) silently call `/api/auth/refresh` whenever an
   API call returns `401`, instead of surfacing the expiry to the user.
3. Expiry values are configured in minutes/days via environment variables
   (`.env`) rather than hard-coded, removing the class of bug where a
   seconds-vs-minutes mix-up silently produces a near-instant timeout.

## Running locally

```
pip install -r requirements.txt
uvicorn backend.main:app --reload
streamlit run ui/app.py
```
