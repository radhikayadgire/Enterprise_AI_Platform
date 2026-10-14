"""Regression tests for IMS-4: mobile session logout after 10 seconds."""
from datetime import datetime, timezone

from jose import jwt

from backend import auth
from backend.config import settings


def test_access_token_expiry_is_minutes_not_seconds():
    token = auth.create_session_tokens("jdoe")
    payload = jwt.decode(token.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    lifetime_seconds = (expires_at - issued_at).total_seconds()

    # With SESSION_TIMEOUT_MINUTES=30 this must be ~1800s, never ~10s.
    assert lifetime_seconds == settings.SESSION_TIMEOUT_MINUTES * 60
    assert lifetime_seconds > 60


def test_login_returns_expires_in_matching_session_timeout():
    token = auth.create_session_tokens("jdoe")
    assert token.expires_in == settings.SESSION_TIMEOUT_MINUTES * 60


def test_authenticate_user_rejects_wrong_password():
    assert auth.authenticate_user("jdoe", "wrong-password") is None


def test_authenticate_user_accepts_correct_password():
    user = auth.authenticate_user("jdoe", "password123")
    assert user is not None
    assert user["username"] == "jdoe"


def test_refresh_rotates_tokens_and_keeps_session_alive():
    token = auth.create_session_tokens("jdoe")
    refreshed = auth.refresh_session_tokens(token.refresh_token)

    assert refreshed.access_token != token.access_token
    assert refreshed.expires_in == settings.SESSION_TIMEOUT_MINUTES * 60


def test_refresh_token_cannot_be_reused_after_rotation():
    import pytest
    from fastapi import HTTPException

    token = auth.create_session_tokens("jdoe")
    auth.refresh_session_tokens(token.refresh_token)

    with pytest.raises(HTTPException):
        auth.refresh_session_tokens(token.refresh_token)


def test_revoked_refresh_token_cannot_be_used():
    import pytest
    from fastapi import HTTPException

    token = auth.create_session_tokens("jdoe")
    auth.revoke_refresh_token(token.refresh_token)

    with pytest.raises(HTTPException):
        auth.refresh_session_tokens(token.refresh_token)
