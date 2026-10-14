"""Authentication and session management.

Fixes IMS-4 (user logged out after 10 seconds on mobile) by:
  * always building token expiry with timedelta(minutes=...), never seconds
  * returning an explicit `expires_in` (seconds) on login/refresh so clients
    know exactly when to renew instead of guessing
  * issuing a long-lived refresh token so the access token can be silently
    rotated before it expires, rather than forcing a re-login
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Demo in-memory user store. Password is "password123" for both users.
_DEMO_PASSWORD_HASH = pwd_context.hash("password123")
USERS_DB = {
    "jdoe": {"username": "jdoe", "full_name": "Jane Doe", "hashed_password": _DEMO_PASSWORD_HASH},
    "smishra": {"username": "smishra", "full_name": "Shamik Mishra", "hashed_password": _DEMO_PASSWORD_HASH},
}

# Tracks refresh-token ids that are still valid (not logged out / rotated away).
_ACTIVE_REFRESH_TOKENS: set[str] = set()


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until the access token expires


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    jti: Optional[str] = None
    type: str = "access"


class User(BaseModel):
    username: str
    full_name: str


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = USERS_DB.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user


def _create_token(subject: str, expires_delta: timedelta, token_type: str, jti: Optional[str] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "exp": now + expires_delta,
        "iat": now,
        "type": token_type,
        # A unique id per token guards against two tokens issued within the
        # same second (e.g. rapid refresh) encoding to an identical JWT.
        "jti": jti or str(uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_session_tokens(username: str) -> Token:
    """Issue a fresh access/refresh token pair for a newly authenticated user."""
    access_expires = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
    refresh_jti = str(uuid4())
    refresh_expires = timedelta(days=settings.REFRESH_TOKEN_TIMEOUT_DAYS)

    access_token = _create_token(username, access_expires, "access")
    refresh_token = _create_token(username, refresh_expires, "refresh", jti=refresh_jti)
    _ACTIVE_REFRESH_TOKENS.add(refresh_jti)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_expires.total_seconds()),
    )


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def refresh_session_tokens(refresh_token: str) -> Token:
    """Rotate a refresh token for a brand new access/refresh pair.

    Mobile clients should call this a little before `expires_in` elapses so
    the session stays alive without ever showing a login screen.
    """
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token.")

    jti = payload.get("jti")
    if jti not in _ACTIVE_REFRESH_TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or unknown.")

    # Rotate: invalidate the old refresh token, issue a new pair.
    _ACTIVE_REFRESH_TOKENS.discard(jti)
    return create_session_tokens(payload["sub"])


def revoke_refresh_token(refresh_token: str) -> None:
    try:
        payload = _decode_token(refresh_token)
    except HTTPException:
        return
    _ACTIVE_REFRESH_TOKENS.discard(payload.get("jti"))


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = _decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token.")

    username = payload.get("sub")
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return User(username=user["username"], full_name=user["full_name"])
