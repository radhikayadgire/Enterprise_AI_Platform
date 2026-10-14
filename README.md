# Enterprise AI Platform

A small multi-agent assistant: a FastAPI backend fronts a coordinator that
routes chat messages to an HR agent, an email agent, or a document search
agent, with a Streamlit UI on top.

## Running the backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Demo users: `jdoe` / `smishra`, password `password123` for both.

## Running the UI

```bash
streamlit run ui/app.py
```

## Session handling (IMS-4)

Users were getting logged out ~10 seconds after login in the mobile app.
Root cause: the access token's expiry was built from
`SESSION_TIMEOUT_MINUTES` but applied as *seconds* instead of minutes, so the
default value of `10` produced a token that expired in 10 seconds.

Fix, in `backend/auth.py` / `backend/config.py`:

- Token expiry is always built with `timedelta(minutes=SESSION_TIMEOUT_MINUTES)`.
- Login and refresh responses include an explicit `expires_in` (seconds) so
  clients never have to guess the token lifetime.
- A long-lived refresh token (`REFRESH_TOKEN_TIMEOUT_DAYS`, default 7 days)
  lets the UI silently rotate the access token before it expires
  (`ui/app.py`, `REFRESH_BUFFER_SECONDS`) instead of forcing a re-login.

## Tests

```bash
pytest
```
