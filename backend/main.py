"""FastAPI backend for the Enterprise AI Platform.

Exposes registration/login plus a refresh-token flow (see backend/auth.py)
so mobile clients stay logged in instead of being dropped as soon as the
short-lived access token expires.
"""
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    revoke_session,
    rotate_session,
    verify_password,
)
from backend.database import Base, engine, get_db
from backend.models import User
from backend.schemas import (
    AccessTokenResponse,
    RefreshRequest,
    Token,
    UserCreate,
    UserOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise AI Platform")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    x_device_type: str = Header(default="web", alias="X-Device-Type"),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    device = x_device_type.lower() if x_device_type.lower() in ("web", "mobile") else "web"
    access_token, expires_in = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(user=user, device=device, db=db)
    return Token(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)


@app.post("/api/auth/refresh", response_model=AccessTokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access_token, expires_in = rotate_session(payload.refresh_token, db)
    return AccessTokenResponse(access_token=access_token, expires_in=expires_in)


@app.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    revoke_session(payload.refresh_token, db)
    return None


@app.get("/api/auth/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
