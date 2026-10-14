"""Password hashing and JWT session helpers.

IMS-4: mobile users were being logged out almost immediately. The mobile
client was only ever issued a short-lived access token with no way to renew
it, so the very first time the app was backgrounded (or a request simply
raced the token's expiry) the user was bounced back to the login screen.

The fix splits the session into two tokens:
  * a short-lived *access* token used to authorize API calls, and
  * a long-lived, revocable *refresh* token (tracked in ``UserSession``)
    that lets a client silently obtain a new access token without asking
    the user to log in again.
"""
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import bcrypt

from backend.database import get_db
from backend.models import User, UserSession

ACCESS_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "dev-refresh-secret-key-change-me")
ALGORITHM = "HS256"

# NOTE: these must be minutes/days, not seconds — a prior misconfiguration
# that mixed up units is exactly how a "10 second" session can happen.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> tuple[str, int]:
    expire_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expire_delta
    payload = {"sub": subject, "exp": expire, "type": "access"}
    token = jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expire_delta.total_seconds())


def create_refresh_token(user: User, device: str, db: Session) -> str:
    now = datetime.now(timezone.utc)
    session = UserSession(
        user_id=user.id,
        device=device,
        created_at=now,
        expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    payload = {
        "sub": user.username,
        "sid": session.id,
        "exp": session.expires_at,
        "type": "refresh",
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def _decode_refresh_token(token: str) -> dict:
    invalid_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise invalid_error
    if payload.get("type") != "refresh":
        raise invalid_error
    return payload


def rotate_session(refresh_token: str, db: Session) -> tuple[str, int]:
    """Validate a refresh token and mint a fresh access token from it."""
    payload = _decode_refresh_token(refresh_token)
    session = db.query(UserSession).filter(UserSession.id == payload.get("sid")).first()
    if session is None or not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or been revoked, please log in again",
        )

    user = db.query(User).filter(User.id == session.user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return create_access_token(subject=user.username)


def revoke_session(refresh_token: str, db: Session) -> None:
    payload = _decode_refresh_token(refresh_token)
    session = db.query(UserSession).filter(UserSession.id == payload.get("sid")).first()
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_error
        username = payload.get("sub")
        if username is None:
            raise credentials_error
    except jwt.PyJWTError:
        raise credentials_error

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_error
    return user
