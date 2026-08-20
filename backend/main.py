"""FastAPI application exposing the Enterprise AI Platform's agent endpoints."""

import logging
import re
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.coordinator import route
from agents.email_agent import handle as send_email
from agents.hr_agent import handle as answer_hr_question
from agents.search_agent import handle as search_documents

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Enterprise AI Platform")


class HRQuery(BaseModel):
    question: str


class SearchQuery(BaseModel):
    query: str


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str


class ChatMessage(BaseModel):
    message: str


class UserDetails(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None


_user_submissions: list[UserDetails] = []


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/hr/query")
def hr_query(payload: HRQuery):
    try:
        return {"answer": answer_hr_question(payload.question)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected error answering HR query")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/search")
def search(payload: SearchQuery):
    try:
        return {"results": search_documents(payload.query)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected error performing search")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/email/send")
def email_send(payload: EmailRequest):
    try:
        return send_email(payload.to, payload.subject, payload.body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected error sending email")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/coordinator/chat")
def coordinator_chat(payload: ChatMessage):
    try:
        return route(payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected error routing chat message")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/user")
def submit_user_details(payload: UserDetails):
    try:
        if not payload.name or not payload.name.strip():
            raise ValueError("name must not be empty")
        if not payload.email or not _EMAIL_RE.match(payload.email):
            raise ValueError(f"invalid email address: {payload.email!r}")

        _user_submissions.append(payload)
        return {"status": "received", "name": payload.name}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected error submitting user details")
        raise HTTPException(status_code=500, detail="Internal server error")
