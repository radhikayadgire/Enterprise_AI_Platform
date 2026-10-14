"""FastAPI backend for the Enterprise AI Platform.

Exposes session/auth endpoints (see backend/auth.py for the IMS-4 session
timeout fix) and a /chat endpoint that delegates to the agent coordinator.
"""
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from agents.coordinator import coordinator
from backend.auth import (
    Token,
    User,
    authenticate_user,
    create_session_tokens,
    get_current_user,
    refresh_session_tokens,
    revoke_refresh_token,
)

app = FastAPI(title="Enterprise AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RefreshRequest(BaseModel):
    refresh_token: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    agent: str
    response: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    return create_session_tokens(user["username"])


@app.post("/auth/refresh", response_model=Token)
def refresh(payload: RefreshRequest) -> Token:
    return refresh_session_tokens(payload.refresh_token)


@app.post("/auth/logout")
def logout(payload: RefreshRequest) -> dict:
    revoke_refresh_token(payload.refresh_token)
    return {"status": "logged_out"}


@app.get("/auth/me", response_model=User)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_user: User = Depends(get_current_user)) -> ChatResponse:
    result = coordinator.route(request.message)
    return ChatResponse(**result)
