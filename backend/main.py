"""FastAPI backend exposing the Enterprise AI Platform's agent routes."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.coordinator import Coordinator
from agents.email_agent import EmailAgent
from agents.hr_agent import HRAgent
from agents.search_agent import SearchAgent

logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise AI Platform")

coordinator = Coordinator()
email_agent = EmailAgent()
hr_agent = HRAgent()
search_agent = SearchAgent()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


class SearchResponse(BaseModel):
    result: str


class EmailRequest(BaseModel):
    to: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = ""


class EmailResponse(BaseModel):
    to: str
    subject: str
    status: str


class HRRequest(BaseModel):
    question: str = Field(..., min_length=1)


class HRResponse(BaseModel):
    answer: str


class CoordinatorRequest(BaseModel):
    query: str = Field(..., min_length=1)


class CoordinatorResponse(BaseModel):
    result: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
def api_search(request: SearchRequest) -> SearchResponse:
    try:
        result = search_agent.run(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("search_agent failed for query=%r", request.query)
        raise HTTPException(status_code=500, detail="search failed") from None
    return SearchResponse(result=result)


@app.post("/api/email", response_model=EmailResponse)
def api_email(request: EmailRequest) -> EmailResponse:
    try:
        result = email_agent.run(request.to, request.subject, request.body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("email_agent failed for to=%r", request.to)
        raise HTTPException(status_code=500, detail="failed to send email") from None
    return EmailResponse(**result)


@app.post("/api/hr", response_model=HRResponse)
def api_hr(request: HRRequest) -> HRResponse:
    try:
        answer = hr_agent.run(request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("hr_agent failed for question=%r", request.question)
        raise HTTPException(status_code=500, detail="hr lookup failed") from None
    return HRResponse(answer=answer)


@app.post("/api/coordinator", response_model=CoordinatorResponse)
def api_coordinator(request: CoordinatorRequest) -> CoordinatorResponse:
    try:
        result = coordinator.route(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("coordinator failed for query=%r", request.query)
        raise HTTPException(status_code=500, detail="coordinator failed") from None
    return CoordinatorResponse(result=result)
