"""Backend API for the Enterprise AI Platform.

Currently exposes a lightweight FastAPI service. The `/contact` endpoint
backs the "Contact Us" page added for MT-2.

All routes include explicit error handling: expected failures are raised as
`HTTPException`s with an appropriate status code, and a global handler
guards against any unexpected exception leaking a raw traceback to callers.
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise AI Platform API")


class ContactInfo(BaseModel):
    name: str
    phone: str
    email: str


CONTACT_INFO = ContactInfo(
    name="Radhika",
    phone="1234567",
    email="radhika@gmail.com",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler so unexpected errors return a clean JSON response
    instead of an unhandled traceback."""
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def read_root():
    try:
        return {"status": "ok", "service": "Enterprise AI Platform API"}
    except Exception as exc:  # pragma: no cover - defensive, no failure path today
        logger.exception("Failed to build root status response")
        raise HTTPException(status_code=500, detail="Failed to retrieve service status") from exc


@app.get("/contact", response_model=ContactInfo)
def get_contact_info() -> ContactInfo:
    """Return the Contact Us information (MT-2)."""
    try:
        if CONTACT_INFO is None:
            raise HTTPException(status_code=404, detail="Contact information not found")
        return CONTACT_INFO
    except HTTPException:
        raise
    except ValidationError as exc:
        logger.exception("Contact information failed validation")
        raise HTTPException(status_code=500, detail="Contact information is invalid") from exc
    except Exception as exc:
        logger.exception("Unexpected error while retrieving contact information")
        raise HTTPException(status_code=500, detail="Failed to retrieve contact information") from exc
