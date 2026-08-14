"""Backend API for the Enterprise AI Platform.

Currently exposes a lightweight FastAPI service. The `/contact` endpoint
backs the "Contact Us" page added for MT-2.
"""

from fastapi import FastAPI
from pydantic import BaseModel

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


@app.get("/")
def read_root():
    return {"status": "ok", "service": "Enterprise AI Platform API"}


@app.get("/contact", response_model=ContactInfo)
def get_contact_info() -> ContactInfo:
    """Return the Contact Us information (MT-2)."""
    return CONTACT_INFO
