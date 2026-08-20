"""
FastAPI backend for the Enterprise AI Platform.

MT-5: exposes the persistence layer for the "User Details" form
(name + phone number) that the Streamlit UI shows right after the
Contact Us page.
"""
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
)

PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")

app = FastAPI(title="Enterprise AI Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


init_db()


class UserDetails(BaseModel):
    name: str
    phone_number: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be empty")
        if len(value) > 100:
            raise ValueError("Name must be 100 characters or fewer")
        return value

    @field_validator("phone_number")
    @classmethod
    def phone_must_be_valid(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_RE.match(value):
            raise ValueError(
                "Phone number must contain 7-15 digits, optionally prefixed with +"
            )
        return value


class UserDetailsResponse(UserDetails):
    id: int
    created_at: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/user-details", response_model=UserDetailsResponse, status_code=201)
def create_user_details(payload: UserDetails):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO user_details (name, phone_number, created_at) VALUES (?, ?, ?)",
            (payload.name, payload.phone_number, created_at),
        )
        conn.commit()
        new_id = cursor.lastrowid

    if new_id is None:
        raise HTTPException(status_code=500, detail="Failed to save user details")

    return UserDetailsResponse(
        id=new_id,
        name=payload.name,
        phone_number=payload.phone_number,
        created_at=created_at,
    )


@app.get("/api/user-details", response_model=List[UserDetailsResponse])
def list_user_details():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, phone_number, created_at FROM user_details ORDER BY id DESC"
        ).fetchall()
    return [UserDetailsResponse(**dict(row)) for row in rows]
